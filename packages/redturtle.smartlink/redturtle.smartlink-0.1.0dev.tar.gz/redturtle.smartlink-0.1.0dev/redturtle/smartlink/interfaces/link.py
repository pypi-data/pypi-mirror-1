from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from Products.ATContentTypes.interface import IATLink

class ISmartLink(IATLink):
    """A link to an internal or external resource."""


