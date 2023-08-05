import zc.vault.interfaces.foundation
import zc.vault.interfaces.common

class IRelationshipContainment(
    zc.vault.interfaces.common.IBidirectionalNameMapping):
    """If relationship.manifest exists, must call
    manifest.approveRelationshipChange before making any changes, and should
    call manifest.reindex after all changes except order changes.
    """

    relationship = interface.Attribute( # DDD __parent__
        """The IRelationship of this containment before versioning (may be
        reused for other relationships after versioning).""")

class IRelationship(zc.vault.interfaces.foundation.IHierarchyRelationship):
    """The relationship for mapping a token to its contents and its object.
    Not mutable if can_modify is False."""

    containment = interface.Attribute(
        """The IRelationshipContainment, mapping names to contained tokens,
        for this relationship.""")

class IObjectRelationship(IRelationship): # ??? deprecate this?

    object = interface.Attribute(
        """the object that the token represents for this relationship.
        if __parent__ exists (manifest), should call
        manifest.approveRelationshipChange before making any changes, and
        call manifest.reindex after change.""")

class IContained(zc.vault.interfaces.common.IBidirectionalNameMapping):
    """Abstract interface."""

    previous = interface.Attribute(
        """The IContained in the vault's previous inventory, or None if
        it has no previous version.  May be equal to (have the same
        relationship as) this IContained.""")

    next = interface.Attribute(
        """The IContained in the vault's next inventory, or None if
        it has no next version.  May be equal to (have the same
        relationship as) this IContained.""")

    previous_version = interface.Attribute(
        """The previous version of the IContained in the vault, or None if
        it has no previous version.  Will never be equal to (have the same
        relationship as) this IContained.""")

    next_version = interface.Attribute(
        """The next version of the IContained in the vault, or None if
        it has no next version.  Will never be equal to (have the same
        relationship as) this IContained.""")

    __parent__ = interface.Attribute(
        """the inventory to which this IContained belongs; same as inventory.
        """)

    inventory = interface.Attribute(
        """the inventory to which this IContained belongs; same as __parent__.
        """)

    relationship = interface.Attribute(
        """The relationship that models the containment and object information
        for the token.""")

    token = interface.Attribute(
        """The token assigned to this IContained's relationship.

        Synonym for .relationship.token""")

    def __call__(name):
        """return an IContained for the name, or raise Key Error"""

    def makeMutable():
        """convert this item to a mutable version if possible. XXX"""

    type = interface.Attribute(
        '''readonly; one of LOCAL, BASE, MERGED, UPDATED, SUGGESTED, MODIFIED.
        see IManifest.getType (below) for definitions.''')

    selected = interface.Attribute(
        '''readonly boolean; whether this item is selected.
        Only one item (relationship) may be selected at a time for a given
        token in a given inventory''')

    selected_item = interface.Attribute(
        '''the selected version of this item''')

    def select():
        '''select this item, deselecting any other items for the same token'''

    is_update_conflict = interface.Attribute(
        '''whether this is an unresolved update conflict''')

    def resolveUpdateConflict():
        '''select this item and mark the update conflict as resolved.'''

    has_base = interface.Attribute("whether item has a base version")

    has_local = interface.Attribute("whether item has a local version")

    has_updated = interface.Attribute("whether item has an updated version")

    has_suggested = interface.Attribute(
        "whether item has any suggested versions")

    has_modified = interface.Attribute(
        "whether item has any modified versions")

    has_merged = interface.Attribute(
        "whether item has any merged versions")

    base_item = interface.Attribute('''the base item, or None''')

    local_item = interface.Attribute('''the local item, or None''')

    updated_item = interface.Attribute('''the updated item, or None''')

    def iterSuggestedItems():
        """iterate over suggested items"""

    def iterModifiedItems():
        """iterate over modified items"""

    def iterMergedItems():
        """iterate over merged items"""

    def updateOrderFromTokens(order):
        """Revise the order of keys, replacing the current ordering.

        order is an iterable containing the set of tokens in the new order.
        `order` must contain ``len(keys())`` items and cannot contain duplicate
        values.

        XXX what exceptions does this raise?
        """

class IInventoryContents(IContained):
    """The top node of an inventory's hierarchy"""

class IInventoryItem(IContained):

    is_orphan = interface.Attribute(
        '''whether this item cannot be reached from the top of the inventory's
        hierarchy via selected relationships/items''')

    is_orphan_conflict = interface.Attribute(
        '''whether this is an orphan (see is_orphan) that is not BASE or
        MERGED and not resolved.''')

    def resolveOrphanConflict():
        '''resolve the orphan conflict so that it no longer stops committing
        or completing an update'''

    is_parent_conflict = interface.Attribute(
        '''whether this object has more than one selected parent''')

    parent = interface.Attribute(
        """The effective parent of the IContained.
        Always another IContained, or None (for an IInventoryContents).
        Will raise ParentConflictError if multiple selected parents.""")

    name = interface.Attribute(
        """The effective name of the IContained.
        Always another IContained, or None (for an IInventoryContents).
        Will raise ParentConflictError if multiple selected parents.""")

    def iterSelectedParents():
        '''iterate over all selected parents'''

    def iterParents():
        '''iterate over all parents'''

    object = interface.Attribute(
        """the object to which this IContained's token maps.  The
        vault_contents for the vault's top_token""")

    def copyTo(location, name=None):
        """make a clone of this node and below in location.  Does not copy
        actual object(s): just puts the same object(s) in an additional
        location.

        Location must be an IContained.  Copying to another inventory is
        currently undefined.
        """

    def moveTo(location=None, name=None):
        """move this object's tree to location.

        Location must be an IMutableContained from the same vault_contents.
        Not specifying location indicates the current location (merely a
        rename)."""

    copy_source = interface.Attribute(
        '''the item representing the relationship and inventory from which this
        item's relationship was created.''')

class IInventory(interface.Interface):
    """IMPORTANT: the top token in an IInventory (and IManifest) is always
    zc.vault.keyref.top_token."""

    manifest = interface.Attribute(
        """The IManifest used by this inventory""")

    def iterUpdateConflicts():
        '''iterate over the unresolved items that have update conflicts'''

    def iterUpdateResolutions():
        '''iterate over the resolved items that have update conflicts'''

    def iterOrphanConflicts():
        '''iterate over the current unresolved orphan conflicts'''

    def iterOrphanResolutions():
        '''iterate over the current resolved orphan conflicts'''

    def iterUnchangedOrphans():
        '''iterate over the orphans that do not cause conflicts--the ones that
        were not changed, so are either in the base or a merged inventory.'''

    def iterParentConflicts():
        '''iterate over the items that have multiple parents.
        The only way to resolve these is by deleting the item in one of the
        parents.'''

    def __iter__():
        '''iterates over all selected items, whether or not they are orphans.
        '''

    updating = interface.Attribute(
        '''readonly boolean: whether inventory is updating''')

    merged_sources = interface.Attribute(
        '''a tuple of the merged sources for this item.''')

    update_source = interface.Attribute(
        '''the source currently used for an update, or None if not updating''')

    def beginUpdate(inventory=None, previous=None):
        """begin update.  Fails if already updating.  if inventory is None,
        uses the current vault's most recent checkin.  if previous is None,
        calculates most recent shared base.
        """

    def completeUpdate():
        """complete update, moving update to merged.  Fails if any update,
        orphan, or parent conflicts."""

    def abortUpdate():
        """returns to state before update, discarding all changes made during
        the update."""

    def beginCollectionUpdate(items):
        """start an update based on just a collection of items"""

    def iterChangedItems(source=None):
        '''iterate over items that have changed from source.
        if source is None, use previous.'''

    def getItemFromToken(token, default=None):
        """get an item for the token in this inventory, or return default."""

    previous = interface.Attribute('the previous inventory in the vault')

    next = interface.Attribute('the next inventory in the vault')

class IInventoryVault(zc.vault.interfaces.foundation.IVault):
    """commit and commitFrom also take inventories"""

    inventory = interface.Attribute(
        """The most recent committed inventory (self.getInventory(-1))""")

    def getInventory(self, ix):
        """return IInventory for relationship set at index ix"""
