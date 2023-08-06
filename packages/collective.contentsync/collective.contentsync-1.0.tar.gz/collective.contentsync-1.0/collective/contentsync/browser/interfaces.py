from zope.interface import Interface

class ISynchronizer(Interface):
    """
    Interface for utility which provides synchronization methods
    """

    def synchronizer(self):
        """
        """

class ISyncForm(Interface):
    """ 
    Interface for Sync form and methods
    """

    def name(self):
        """
        Return the base view name as specified by ZCML
        """

    def field(self):
        """
        Return a reference field
        """

    def handle(self, targets=None, redirect=False):
        """
        Handle the post
        """

class IReferenceBrowserAPIWrapper(Interface):
    """ 
    Interface for a browser view which plays nicely
    with the Reference Browser API.
    """

class IProgressView(Interface):
    """
    Interface for progress view
    """

class ISynchronizedObject(Interface):
    """
    Marker interface to signal that an item was created 
    by a synchronization.
    """
