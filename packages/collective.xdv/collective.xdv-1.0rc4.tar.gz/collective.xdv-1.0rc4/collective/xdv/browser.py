from Products.Five.browser import BrowserView

from zope.component import queryUtility

from plone.registry.interfaces import IRegistry

from plone.app.registry.browser import controlpanel

from collective.xdv.interfaces import ITransformSettings, _
from collective.xdv.utils import get_host

try:
    # only in z3c.form 2.0
    from z3c.form.browser.textlines import TextLinesFieldWidget
except ImportError:
    from plone.z3cform.textlines import TextLinesFieldWidget

class TransformSettingsEditForm(controlpanel.RegistryEditForm):
    
    schema = ITransformSettings
    label = _(u"Transform settings") 
    description = _(u"Please enter the options specified")
    
    def updateFields(self):
        super(TransformSettingsEditForm, self).updateFields()
        self.fields['domains'].widgetFactory = TextLinesFieldWidget
        self.fields['notheme'].widgetFactory = TextLinesFieldWidget
        self.fields['alternate_themes'].widgetFactory = TextLinesFieldWidget
        
    
    def updateWidgets(self):
        super(TransformSettingsEditForm, self).updateWidgets()
        self.widgets['domains'].rows = 4
        self.widgets['domains'].style = u'width: 30%;'
        self.widgets['notheme'].rows = 4
        self.widgets['notheme'].style = u'width: 30%;'
        self.widgets['theme'].size = 60
        self.widgets['rules'].size = 60
        self.widgets['alternate_themes'].rows = 4
        self.widgets['alternate_themes'].style = u'width: 40%;'
        self.widgets['boilerplate'].size = 60
        self.widgets['extraurl'].size = 60        
        self.widgets['absolute_prefix'].size = 60
    
class TransformSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = TransformSettingsEditForm

class Utility(BrowserView):
    """Utility view to determine if the site is currently styled with xdv
    """
    
    def enabled(self):
        """Determine if the utility is enabled and we are in an enabled domain
        """
       
        registry = queryUtility(IRegistry)
        if registry is None:
            return False
        
        settings = None
        try:
            settings = registry.forInterface(ITransformSettings)
        except KeyError:
            return False
        
        if not settings.enabled:
            return False
        
        domains = settings.domains
        if not domains:
            return False
        
        host = get_host(self.request)
        for domain in domains:
            if domain.lower() == host.lower():
                return True
        
        return False
    
    def domain_enabled(self):
        """Determine if the current request is in an xdv domain. Will return
        True even if the actual transform is disabled.
        """
        
        registry = queryUtility(IRegistry)
        if registry is None:
            return False
        
        settings = None
        try:
            settings = registry.forInterface(ITransformSettings)
        except KeyError:
            return False
        
        domains = settings.domains
        if not domains:
            return False
        
        host = get_host(self.request)
        for domain in domains:
            if domain.lower() == host.lower():
                return True
        
        return False