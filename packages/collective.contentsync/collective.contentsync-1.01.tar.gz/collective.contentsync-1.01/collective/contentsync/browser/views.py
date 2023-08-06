from Acquisition import aq_inner
from zope.interface import implements
from zope.component import getUtility

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Archetypes.atapi import BaseContent, Schema
from Products.Archetypes.Field import ReferenceField
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

from interfaces import ISyncForm, IReferenceBrowserAPIWrapper, ISynchronizer

schema = Schema((
    ReferenceField(
        name="targets",
        widget = ReferenceBrowserWidget(
                    label="Target",
                    label_msgid="collectivecontentsync_label_target",
                    i18n_domain="collective.contentsync"),
        multiValued=1,
        relationship="irrelevant"),
))

class FakeContent(BaseContent):
    """
    Content class needed to play nicely with Reference
    Browser API.
    """
    schema = schema

class SyncForm(BrowserView):
    """
    Provides Sync form and methods
    """
    implements(ISyncForm)

    def __init__(self, context, request):
        super(SyncForm, self).__init__(context, request)
        context = aq_inner(self.context)
        self.content = FakeContent('irrelevant').__of__(context)

    def name(self):
        return '.'.join(str(self.__name__).split('.')[:-1])

    def field(self):
        return self.content.Schema().getField('targets')
   
    def handle(self, targets=[], redirect=False):
        context = aq_inner(self.context)
        
        # Cleanup targets
        targets = [t for t in targets if t]

        # Validate
        errors = {}
        if not targets:
            errors['targets'] = _("Please select a target")

        if errors:
            view = context.restrictedTraverse('@@%s.form' % self.name())
            return view(REQUEST=context.REQUEST, errors=errors)

        # Delegate to synchronizer utility
        rc = getToolByName(context, 'reference_catalog')
        target_objects = []
        for uid in targets:
            target_objects.append(rc.lookupObject(uid))
        utility = getUtility(ISynchronizer)
        result = utility.synchronize(source=context, 
                    targets=target_objects, 
                    view=context.restrictedTraverse('@@collective.contentsync.progress'))

        if redirect:
            pu = getToolByName(context, 'plone_utils')
            msg = _("Synchronization complete")
            pu.addPortalMessage(msg)
            context.REQUEST.RESPONSE.redirect(context.absolute_url())

class ReferenceBrowserAPIWrapper(BrowserView):
    """
    Provides a browser view which plays nicely with the 
    Reference Browser API.
    """
    implements(IReferenceBrowserAPIWrapper)

    def __init__(self, context, request):
        super(ReferenceBrowserAPIWrapper, self).__init__(context, request)        
        context = aq_inner(self.context)
        self.content = FakeContent('irrelevant').__of__(context)

    def __getattr__(self, name):
        if hasattr(self.content, name):
            return getattr(self.content, name)
        return BrowserView.getattr(self, name)
