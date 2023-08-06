from zope.component.interfaces import IObjectEvent
from zope.interface import Interface

class IInitialiseProgressBar(IObjectEvent):
    """ An event fired to initialise progress bar
    """

class IUpdateProgressEvent(IObjectEvent):
    """ An event fired to update progress
    """


