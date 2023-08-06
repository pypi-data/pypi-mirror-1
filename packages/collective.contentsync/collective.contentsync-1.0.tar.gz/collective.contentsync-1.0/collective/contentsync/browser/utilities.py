from zope.interface import implements, alsoProvides
from zope.event import notify
from Acquisition import aq_inner, aq_base

from Products.CMFCore.utils import getToolByName

from collective.contentsync.events import SynchronizeStateChangeEvent
from interfaces import ISynchronizer, ISynchronizedObject

from time import sleep

class State:

    def __init__(self, source, view, step=1, total=0):
        self.source = source
        self.view = view
        self.step = step
        self.total = total
        self.initializing = True
        self.index = 0
        self.message = ''
        self.target = None
        self.done = False       
        notify(SynchronizeStateChangeEvent(self))
        self.initializing = False

    def edit(self, **kw):
        for k,v in kw.items():
            setattr(self, k, v)
        notify(SynchronizeStateChangeEvent(self))

    def log(self, message):
        self.message = message
        notify(SynchronizeStateChangeEvent(self))
        self.message = ''

    def reset(self):
        self.__init__(source=self.source, view=self.view)

class Synchronizer(object):
    """
    Provide synchronization methods
    """
    implements(ISynchronizer)

    def synchronize(self, source, targets, view=None):
        state = State(source=source, view=view)      # may change to an object in future
        portal = getToolByName(source, 'portal_url').getPortalObject()
        source_path = '/'.join(source.getPhysicalPath())

        # Build structure describing what needs to be done. This is 
        # needed for a progress report.
        source_child_paths = []
        for _, child in source.ZopeFind(source, search_sub=1):
            source_child_paths.append('/'.join(child.getPhysicalPath()))
        
        # Sort the paths. This means we traverse from highest to 
        # lowest level paths.
        source_child_paths.sort()

        sync = {}
        for target in targets:
            target_path = '/'.join(target.getPhysicalPath())

            # Find paths which need to be copied to the target
            sync_add_paths = []
            for source_child_path in source_child_paths:
                # Raise if source is in target
                if source_child_path == source_path:
                    raise "Target %s includes source %s" % (target_path, source_path)
                # If this path's parent is already in sync_add_paths 
                # then this object will be copied when the parent is
                # copied. Skip.
                parent_path = '/'.join(source_child_path.split('/')[:-1])
                if parent_path in sync_add_paths:
                    continue

                # Are any items in obj not in the corresponding location
                # of the target?
                source_obj = portal.unrestrictedTraverse(source_child_path)
                tpath = source_child_path.replace(source_path, '').lstrip('/')
                try:
                    target_obj = aq_base(target).unrestrictedTraverse(tpath)
                except AttributeError:
                    sync_add_paths.append(source_child_path)
                
            # Find paths which must be deleted from the target
            sync_delete_paths = []
            target_child_paths = []
            for _, child in target.ZopeFind(target, search_sub=1):
                target_child_paths.append('/'.join(child.getPhysicalPath()))

            # Sort the paths. This means we traverse from highest to 
            # lowest level paths.
            target_child_paths.sort()
            for target_child_path in target_child_paths:
                # If this path's parent is already in sync_delete_paths 
                # then this object will be deleted when the parent is
                # deleted. Skip.
                parent_path = '/'.join(target_child_path.split('/')[:-1])
                if parent_path in sync_delete_paths:
                    continue

                corresponding_path = source_path + '/' +  target_child_path.replace(target_path, '').lstrip('/')
                if corresponding_path not in source_child_paths:
                    # The target child may only be deleted if it
                    # was created by a sync.
                    obj = portal.unrestrictedTraverse(target_child_path)
                    if ISynchronizedObject.isImplementedBy(obj):
                        sync_delete_paths.append(target_child_path)
                 
            # Add to structure
            sync.setdefault(target, {})
            sync[target]['add'] = sync_add_paths
            sync[target]['delete'] = sync_delete_paths

        state.edit(total=len(sync.keys()))
        
        # Perform the operations
        count = 1
        for target, di in sync.items():
            target_path = '/'.join(target.getPhysicalPath())
            for path in di['add']:
                source_object = portal.unrestrictedTraverse(path)
                source_container = source_object.getParentNode()

                # The destination must be computed from path
                # A typical path is /plone/case5_source/a1/b1/c1/d1
                corresponding_path = '/'.join(path.replace(source_path, target_path).split('/')[:-1])
                dest = portal.unrestrictedTraverse(corresponding_path)

                cp = source_container.manage_copyObjects([source_object.getId()])
                try:
                    dest.manage_pasteObjects(cp)
                except:
                    # Something went wrong. We are probably not allowed to
                    # copy the object to that destination.
                    state.log("Cannot copy %s to %s" % (source_object.title_or_id(), dest.title_or_id()))

                # Apply marker interface ISynchronizedObject recursively to newly 
                # copied objects.
                root = dest[source_object.getId()]
                alsoProvides(root, ISynchronizedObject)
                for _, child in source.ZopeFind(root, search_sub=1):
                    alsoProvides(child, ISynchronizedObject)

            for path in di['delete']:
                # A typical path is /plone/case5_target/a1/b3'
                obj = portal.unrestrictedTraverse(path)
                container = obj.getParentNode()
                container.manage_delObjects([obj.getId()])              

            state.edit(index=count, target=target)
            
            count +=1

        state.edit(done=True)
