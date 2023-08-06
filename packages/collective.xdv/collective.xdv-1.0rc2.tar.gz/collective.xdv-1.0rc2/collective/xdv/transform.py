import re
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
    _transform = None
    
    @property
    @synchronized(_lock)
    def notheme(self):
        return self._notheme
        
    @property
    @synchronized(_lock)
    def transform(self):
        return self._transform
    
    @synchronized(_lock)
    def clear(self):
        self._notheme = None
        self._transform = None
    
    @synchronized(_lock)
    def update_notheme(self, notheme):
        self._notheme = notheme
    
    @synchronized(_lock)
    def update_transform(self, transform):
        self._transform = transform

CACHE = _Cache()

def invalidate_cache(proxy, event):
    """When our settings are changed, invalidate the cache
    """
    CACHE.clear()

def apply_transform(object, event):
    """Apply the transform if required
    """
    
    try: # this method should never fail, lest it kills the publisher
    
        request = event.request
        response = request.response
        
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
            settings = registry.for_interface(ITransformSettings)
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
    
        # Check if we're on a path that should be ignored
    
        notheme = None
    
        if not DevelopmentMode:
            notheme = CACHE.notheme
    
        if notheme is None:
            notheme = [re.compile(n) for n in (settings.notheme or [])]
        
            if not DevelopmentMode:
                CACHE.update_notheme(notheme)
    
        if notheme:
            # Find real or virtual path - PATH_INFO has VHM elements in it
            actual_url = request.get('ACTUAL_URL')
            server_url = request.get('SERVER_URL')
            path = actual_url[len(server_url):]
            
            if not path:
                path = '/'
            for pattern in notheme:
                if pattern.match(path):
                    return
    
        # Apply theme
    
        transform = None
    
        if not DevelopmentMode:
            transform = CACHE.transform
    
        if transform is None:
        
            theme = settings.theme
            rules = settings.rules
            boilerplate = settings.boilerplate or None
            absolute_prefix = settings.absolute_prefix or None
    
            if not theme or not rules:
                return
    
            compiled_theme = compile_theme(theme, rules, boilerplate, absolute_prefix)
            if not compiled_theme:
                return
    
            xslt_tree = etree.fromstring(compiled_theme)
            transform = etree.XSLT(xslt_tree)
        
            if not DevelopmentMode:
                CACHE.update_transform(transform)
        
        content = etree.fromstring(body, parser=etree.HTMLParser())
        transformed = transform(content)
        new_body = etree.tostring(transformed)
    
        if not isinstance(new_body, basestring) or not new_body:
            return
        
        response.setBody(new_body)
    except ConflictError:
        raise
    except Exception, e:
        LOGGER.exception(u"Unexpected error whilst trying to apply xdv transform")