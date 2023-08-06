import re
import sys
import logging
from lxml import etree

from threading import Lock
from plone.synchronize import synchronized

from Globals import DevelopmentMode
from ZODB.POSException import ConflictError

from zope.component import queryUtility
from plone.registry.interfaces import IRegistry

from collective.xdv.interfaces import ITransformSettings
from collective.xdv.utils import compile_theme, get_host

HTML_DOC_PATTERN = re.compile(r"^.*<\s*html(\s*|>).*$",re.I|re.M)

LOGGER = logging.getLogger('collective.xdv')

class _Cache(object):
    """Simple cache for the transform and notheme regular expressions
    """
    
    _lock = Lock()
    _notheme = None
    _themes = None
    _transform = {}
    
    @property
    @synchronized(_lock)
    def notheme(self):
        return self._notheme

    @property
    @synchronized(_lock)
    def themes(self):
        return self._themes
        
    @property
    @synchronized(_lock)
    def transform(self):
        return self._transform
    
    @synchronized(_lock)
    def clear(self):
        self._notheme = None
        self._themes = None
        self._transform = {}
    
    @synchronized(_lock)
    def update_notheme(self, notheme):
        self._notheme = notheme
    
    @synchronized(_lock)
    def update_themes(self, themes):
        self._themes = themes
    
    @synchronized(_lock)
    def update_transform(self, theme_id, transform):
        self._transform[theme_id] = transform

CACHE = _Cache()

def invalidate_cache(proxy, event):
    """When our settings are changed, invalidate the cache
    """
    CACHE.clear()

def apply_transform(request, body=None):
    """Apply the transform if required
    """
    response = request.response
    
    try: # this method should never fail, lest it kills the publisher
        
        # Never style 127.0.0.1 - we want to be able to get back into Plone
        # if things go really wrong.
        
        host = get_host(request)
        if not host or host.startswith('127.0.0.1:'):
            return
    
        # Check request type
    
        content_type = response.getHeader('content-type')
        if not content_type or \
                not (content_type.startswith('text/html') or 
                        content_type.startswith('application/xhtml+xml')):
            return
    
        if body is None:
            body = response.getBody()
        if not isinstance(body, basestring) or not body:
            return
    
        if not HTML_DOC_PATTERN.search(body):
            return
        
        # Obtain xdv settings. Do noting if not found

        registry = queryUtility(IRegistry)
        if registry is None:
            return

        try:
            settings = registry.forInterface(ITransformSettings)
        except KeyError:
            return
    
        if settings is None:
            return
    
        if not settings.enabled:
            return
    
        # Test that we're on a domain that should be themed
    
        domains = settings.domains
        if not domains:
            return
        
        found_domain = False
        for domain in domains:
            if domain.lower() == host.lower():
                found_domain = True
                break
        if not found_domain:
            return
    
        # Find real or virtual path - PATH_INFO has VHM elements in it
        actual_url = request.get('ACTUAL_URL')
        server_url = request.get('SERVER_URL')
        path = actual_url[len(server_url):]

        # Check if we're on a path that should be ignored
        notheme = None
    
        if not DevelopmentMode:
            notheme = CACHE.notheme
    
        if notheme is None:
            notheme = [re.compile(n) for n in (settings.notheme or [])]
        
            if not DevelopmentMode:
                CACHE.update_notheme(notheme)
    
        if notheme:
            if not path:
                path = '/'
            for pattern in notheme:
                if pattern.match(path):
                    return
    
        theme = settings.theme
        rules = settings.rules
        theme_id = u'default'
        
        # If alternate_themes are set, resolve theme files
        alternate_themes = settings.alternate_themes
        if alternate_themes:
            themes = None
            if not DevelopmentMode:
                themes = CACHE.themes
        
            if themes is None:
                themes_settings = [ n.split('|') for n in alternate_themes]
                themes = [ (re.compile(n[0]),n[0],n[1],n[2]) for n in themes_settings]

                if not DevelopmentMode:
                    CACHE.update_themes(themes)

            # if we find a match, replace the original theme
            if themes:
                for pattern, i_theme_id, i_theme, i_rules in themes:
                    if pattern.match(path):
                        theme = i_theme
                        rules = i_rules
                        theme_id = i_theme_id
                        break

        if not theme or not rules or not theme_id:
            return

        # Apply theme
        transform = None
    
        if not DevelopmentMode:
            transform = CACHE.transform.get(theme_id)
    
        if transform is None:
                            
            boilerplate = settings.boilerplate or None
            extraurl = settings.extraurl or None
            absolute_prefix = settings.absolute_prefix or None
        
            compiled_theme = compile_theme(theme, rules, boilerplate, absolute_prefix, extraurl)
            if not compiled_theme:
                return
    
            xslt_tree = etree.fromstring(compiled_theme)
            transform = etree.XSLT(xslt_tree)
        
            if not DevelopmentMode:
                CACHE.update_transform(theme_id, transform)
        
        content = etree.fromstring(body, parser=etree.HTMLParser())
        transformed = transform(content)
        new_body = etree.tostring(transformed)
    
        if not isinstance(new_body, basestring) or not new_body:
            return
        return new_body
    except ConflictError:
        raise
    except Exception, e:
        LOGGER.exception(u"Unexpected error whilst trying to apply xdv transform")

def apply_transform_on_success(event):
    """Apply the transform if required
    """
    request = event.request
    new_body = apply_transform(request)
    if new_body is not None:
        request.response.setBody(new_body)

def apply_transform_on_failure(event):
    """Apply the transform to the error html
    """
    if not event.retry:
        exc_info = sys.exc_info()
        error = exc_info[1]
        request = event.request
        if isinstance(error, unicode):
            # Plone 3.x / Zope 2.10
            new_body = apply_transform(request, error)
            if new_body is not None:
                # If it's any consolation, I feel quite dirty doing this...
                raise exc_info[0], new_body, exc_info[2]
        #else:
        #    # Plone 4 / Zope 2.12
        #    body = error.args[0]
        #    new_body = apply_transform(request, error)
        #    if new_body is not None:
        #        error.args = (new_body, ) + error.args[1:]
