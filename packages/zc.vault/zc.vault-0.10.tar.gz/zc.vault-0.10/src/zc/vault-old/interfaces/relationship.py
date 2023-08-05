import zope.interface
from zc.vault.interfaces.foundation import IRelationship
import zope.component.interfaces

class ICollectionEvent(zope.component.interfaces.IObjectEvent): # abstract
    """object is collection"""

class ICollectionMemberEvent(ICollectionEvent):

    mapping = interface.Attribute(
        'the affected mapping; __parent__ is relationship')

    key = interface.Attribute('the key affected')

class IObjectRemoved(ICollectionEvent):
    """Object was removed from mapping"""

class IObjectAdded(ICollectionEvent):
    """Object was added to mapping"""

class IOrderChanged(zope.component.interfaces.IObjectEvent):
    """Object order changed; object is mapping"""

    old_keys = interface.Attribute('A tuple of the old key order')

# these support implementations of IHierarchyRelationships and
# IShortcutRelationships, but are not relied upon by the vault or revisions
# themselves.

class ICollectionRelationship(IRelationship):
    """uses collection to provide IHierarchyRelationship, IShortcutRelationship,
    or both"""
    
    collection = zope.interface.Attribute('an ITokenCollection')

class ITokenCollection(zope.interface.Interface):

    relationship = zope.interface.Attribute('an ICollectionRelationship')

    def copy(self):
        "return a non-frozen copy"

    def __eq__(self, other):
        "return whether other is equal in data to this collection"

    def __ne__(self, other):
        "return whether other is not equal in data to this collection"

class IHierarchyTokenCollection(ITokenCollection):
    """changes should fire ChildrenAdded, ChildrenRemoved, ChildrenReplaced,
    and OrderChanged events on pertinent changes to these objects"""
    
    child_tokens = zope.interface.Attribute(
        'see IHierarchyRelationship.child_tokens')

class IShortcutTokenCollection(ITokenCollection):
    """changes should fire ShortcutsAdded, ShortcutsRemoved, ShortcutsReplaced,
    and OrderChanged events on pertinent changes to these objects"""
    
    shortcut_tokens = zope.interface.Attribute(
        'see IShortcutRelationship.child_tokens')

class ICombinedTokenCollection(
    IHierarchyTokenCollection, IShortcutTokenCollection):
    'supports both'