from zope.interface import Interface
from zope import schema
from redturtle.smartlink import smartlinkMessageFactory as _
from zope.interface import invariant, Invalid


class ISmartlinkConfig(Interface):
    
    relativelink = schema.Bool(
        title=_(u"Relative link"),
        description=_(u"If selected, all links in the site will have a relative URL, rather than absolute."),
        required=False
    )
    
    frontendlink = schema.List(
        title=_(u"Front-end Link"),
        value_type=schema.TextLine(),
        default=[],
        unique=True,
        required=False
    )
    
    backendlink = schema.List(
        title=_(u"Back-end Link"),
        value_type=schema.TextLine(),
        default=[],
        unique=True,
        required=False
    )
    
    @invariant
    def otherFilledIfSelected(smartlink):

        if len(smartlink.frontendlink) != len(smartlink.backendlink):
            raise Invalid(_(u"Front-end link must correspond to a single back-end link"))
    