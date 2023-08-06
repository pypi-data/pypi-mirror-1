from zope.interface import implements

from Products.Five import BrowserView

from interfaces import IProgressView

class ProgressView(BrowserView):
    """
    Progress view
    """
    implements(IProgressView)
