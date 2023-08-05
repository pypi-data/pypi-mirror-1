import zope.component.interfaces

class IManifestCommitted(zope.component.interfaces.IObjectEvent):
    """Object is manifest."""

class ILocalRelationshipAdded(zope.component.interfaces.IObjectEvent):
    """Relationship added to manifest as a local version.
    Relationship.__parent__ must be manifest."""

class IModifiedRelationshipAdded(zope.component.interfaces.IObjectEvent):
    """Relationship added to manifest as a modified version.
    Relationship.__parent__ must be manifest."""

class ISuggestedRelationshipAdded(zope.component.interfaces.IObjectEvent):
    """Relationship added to manifest as a suggested version.
    Relationship.__parent__ must be manifest."""

class IUpdateEvent(zope.component.interfaces.IObjectEvent):

    source = interface.Attribute(
        '''source manifest (from beginUpdate) or collection
        (from beginCollectionUpdate)''')

    base = interface.Attribute(
        '''the base manifest from which the update proceeds, or None.''')

class IUpdateBegun(IUpdateEvent):
    '''fired from beginUpdate or beginCollectionUpdate'''

class IUpdateCompleted(IUpdateEvent):
    ''

class IUpdateAborted(IUpdateEvent):
    ''

class IObjectChanged(zope.component.interfaces.IObjectEvent):
    previous = interface.Attribute('the previous object')

class IVaultChanged(zope.component.interfaces.IObjectEvent):
    previous = interface.Attribute('the previous vault')

class IRelationshipSelected(zope.component.interfaces.IObjectEvent):
    """relationship was selected"""
    manifest = interface.Attribute(
        'the manifest in which this relationship was selected')

class IRelationshipDeselected(zope.component.interfaces.IObjectEvent):
    """relationship was deselected"""
    manifest = interface.Attribute(
        'the manifest in which this relationship was deselected')

class ObjectRemoved(zope.component.interfaces.ObjectEvent):
    interface.implements(IObjectRemoved)
    def __init__(self, obj, mapping, key):
        super(ObjectRemoved, self).__init__(obj)
        self.mapping = mapping
        self.key = key

class ObjectAdded(zope.component.interfaces.ObjectEvent):
    interface.implements(IObjectAdded)
    def __init__(self, obj, mapping, key):
        super(ObjectAdded, self).__init__(obj)
        self.mapping = mapping
        self.key = key

class OrderChanged(zope.component.interfaces.ObjectEvent):
    interface.implements(IOrderChanged)
    def __init__(self, obj, old_keys):
        super(OrderChanged, self).__init__(obj)
        self.old_keys = old_keys

class ManifestCommitted(zope.component.interfaces.ObjectEvent):
    interface.implements(IManifestCommitted)

class LocalRelationshipAdded(zope.component.interfaces.ObjectEvent):
    interface.implements(ILocalRelationshipAdded)

class ModifiedRelationshipAdded(zope.component.interfaces.ObjectEvent):
    interface.implements(IModifiedRelationshipAdded)

class SuggestedRelationshipAdded(zope.component.interfaces.ObjectEvent):
    interface.implements(ISuggestedRelationshipAdded)

class AbstractUpdateEvent(zope.component.interfaces.ObjectEvent):
    def __init__(self, obj, source, base):
        super(AbstractUpdateEvent, self).__init__(obj)
        self.source = source
        self.base = base

class UpdateBegun(AbstractUpdateEvent):
    interface.implements(IUpdateBegun)

class UpdateCompleted(AbstractUpdateEvent):
    interface.implements(IUpdateCompleted)

class UpdateAborted(AbstractUpdateEvent):
    interface.implements(IUpdateAborted)

class VaultChanged(zope.component.interfaces.ObjectEvent):
    interface.implements(IVaultChanged)
    def __init__(self, obj, previous):
        super(VaultChanged, self).__init__(obj)
        self.previous = previous

class ObjectChanged(zope.component.interfaces.ObjectEvent):
    interface.implements(IObjectChanged)
    def __init__(self, obj, previous):
        super(ObjectChanged, self).__init__(obj)
        self.previous = previous

class RelationshipSelected(zope.component.interfaces.ObjectEvent):
    interface.implements(IRelationshipSelected)
    def __init__(self, obj, manifest):
        super(RelationshipSelected, self).__init__(obj)
        self.manifest = manifest

class RelationshipDeselected(zope.component.interfaces.ObjectEvent):
    interface.implements(IRelationshipDeselected)
    def __init__(self, obj, manifest):
        super(RelationshipDeselected, self).__init__(obj)
        self.manifest = manifest
