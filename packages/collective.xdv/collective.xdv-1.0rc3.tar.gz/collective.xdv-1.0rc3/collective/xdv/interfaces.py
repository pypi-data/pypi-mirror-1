from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory(u"collective.xdv")

class ITransformSettings(Interface):
    """Transformation settings
    """
    
    enabled = schema.Bool(
            title=_(u"Enabled"),
            description=_(u"Enable transforms globally"),
            required=True,
            default=False,
        )
    
    domains = schema.Set(
            title=_(u"Domains"),
            description=_(u"Domains (host names) for which the transform should apply. "
                           "Should include port numbers where necessary. Note that "
                           "'127.0.0.1' will not be styled, but 'localhost' is fine. "
                           "This is to ensure that you can always reach this screen if "
                           "things go wrong."),
            required=False,
            default=set([u'localhost:8080']),
            value_type=schema.TextLine(title=_(u"Domain")),
        )
        
    theme = schema.TextLine(
            title=_(u"Theme template"),
            description=_(u"File path or URL to the theme template"),
            required=False,
        )
    
    rules = schema.TextLine(
            title=_(u"Rules file"),
            description=_(u"File path to the rules file"),
            required=False,
        )
    
    boilerplate = schema.TextLine(
            title=_(u"Boilerplate XSLT file"),
            description=_(u"File path to a file to use for boilerplate transforms. "
                            "If left blank, the default will be used."),
            required=False,
        )
        
    absolute_prefix = schema.TextLine(
            title=_(u"Absolute URL prefix"),
            description=_(u"Convert relative URLs in the theme file to absolute paths "
                           "using this prefix."),
            required=False,
        )
    
    notheme = schema.Set(
            title=_(u"Unstyled paths"),
            description=_(u"Specify paths that should not be styled. May use regular expression syntax"),
            required=False,
            default=set([u'^.*/emptypage$', u'^.*/manage_[^/]+$']),
            value_type=schema.TextLine(title=_(u"Path")),
        )