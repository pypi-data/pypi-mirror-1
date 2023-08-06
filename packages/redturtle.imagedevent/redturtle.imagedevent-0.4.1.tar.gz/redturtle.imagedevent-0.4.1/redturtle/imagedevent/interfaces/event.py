from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from Products.ATContentTypes.interface import IATEvent

class IImagedEvent(IATEvent):
    """Information about an upcoming event, which can be displayed in the calendar."""
