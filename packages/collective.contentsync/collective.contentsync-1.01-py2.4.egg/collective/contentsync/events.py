from zope.interface import implements

from interfaces import ISynchronizeStateChangeEvent

class SynchronizeStateChangeEvent(object):

    implements(ISynchronizeStateChangeEvent)

    def __init__(self, object):
        self.object = object
