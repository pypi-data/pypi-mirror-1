from zope.component.interfaces import IObjectEvent

class ISynchronizeStateChangeEvent(IObjectEvent):
    """ 
    An event triggered by an utility which implements
    ISynchronizer
    """
