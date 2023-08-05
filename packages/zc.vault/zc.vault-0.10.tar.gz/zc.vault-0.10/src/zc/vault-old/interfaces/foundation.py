import zope.interface
import zope.interface.common.sequence
from zc.vault.interfaces.uniquereference import IUniqueReference

#### RELATIONSHIPS ####

class IRelationship(IUniqueReference):
    """XXX
    
    Mutations need to call revision.checkRelationshipChange(self) before
    allowing a change.  After change, must call
    revision.reindexRelationship(self).
    
    Must implement, or be adaptable to, zc.freeze.interfaces.IFreezing.
    """

    # __parent__ should typically be equivalent to manifest

    token = zope.interface.Attribute(
        """The token that this relationship maps""")

    type = zope.interface.Attribute(
        """The type of this relationship.
        
        Within a given vault, one "type" should be equivalent to a single
        relationship class.
        """)

    manifest = zope.interface.Attribute(
        """The manifest of this relationship when frozen (may be
        reused for other manifests in sequence in the same vault after being
        frozen)""")

    previous = zope.interface.Attribute(
        """the previous relationship for this token in the same vault, or None
        """)

    copy_source = zope.interface.Attribute(
        """A tuple of the relationship and manifest that was the source of
        this relationship. or None, if it was not generated from copy or
        copyFrozen""")

    next = zope.interface.Attribute(
        """the next relationship for this token in the same vault, or None
        """)

    def equalData(self, other):
        """return True if everything but manifest, next, previous, and
        copy_source are the same.  Because the relationship "type" should
        be associated with the same class, checking in only one direction
        should be sufficient.
        """

    def copyFrozen(source_manifest):
        """make a frozen copy.
        
        source_manifest should be the manifest from which this copy is being
        made (which may not be the same as this relationship's manifest
        
        allows optimizations over copy.
        """

    def copy(source_manifest, token=None):
        """make a non-frozen copy
        
        source_manifest should be the manifest from which this copy is being
        made (which may not be the same as this relationship's manifest
        """


class IHierarchyRelationship(IRelationship):

    child_tokens = zope.interface.Attribute(
        """a set of the tokens "contained" by the `token` for this `type`.
        It is an error to have more than one selected relationship with the
        same token as a child: a token has only one allowed child
        (hierarchical) relationship for a given relationship type.
        
        ideally an IOTreeSet (or LOTreeSet, if the relationship uses
        LOTrees)
        """)

class IShortcutRelationship(IRelationship):

    shortcut_tokens = zope.interface.Attribute(
        """a set of the tokens linked to by the `token` for this `type`.
        
        ideally an IOTreeSet (or LOTreeSet, if the relationship uses
        LOTrees)""")

#### CONFIGURATION ####

class IVersionFactory(interface.Interface):
    """looked up as a adapter of vault"""
    def __call__(object, manifest):
        """return the object to be stored"""

class IConflictResolver(interface.Interface):
    """looked up as a adapter of vault."""
    def __call__(manifest, local, update, base):
        """React to conflict between local and update as desired."""

#### VAULT ####

class IReadVault(zope.interface.common.sequence.IFiniteSequence):

    additional_relationship_indexes = zope.interface.Attribute(
        """a tuple of dictionaries that are used to configure the manifest's
        relationship indexes.  Readonly (mutating does not mutate the
        attribute, or it is a frozen dict).""")

    contains_links = zope.interface.Attribute(
        """a bool describing whether manifests will index and handle
        ILinksRelationship.links.  Links are only maintained in validating
        that they point to an available token.  Readonly.""")

    relationship_types = zope.interface.Attribute(
        """a tuple of the relationship types (unicode names).
        Must contain at least one.  If this contains more than one type,
        the manifests will index type.  Readonly.""")

    intids = zope.interface.Attribute(
        """the IIntId object that is to be used to assign ids to
        relationships.  Readonly.
        """) # this may be an extended interface to support
        # assigning 

    top_token = zope.interface.Attribute(
        """the integer that is the top of the hierarchy.  
        IVault.intids.getObj(IVault.top_token) is zc.vault.keyref.top_token.
        Readonly.
        """)

    manifest = zope.interface.Attribute(
        """The most recent committed manifest (self[-1]).  Readonly.""")

class IVault(zope.interface.common.sequence.IFiniteSequence):

    def createBranch(ix=-1):
        """create a new vault with the first manifest based on the given
        manifest specified by ix.  `intids`, `contains_links`,
        `relationship_types` and `additional_relationship_indexes` are
        shared."""

    def commit(manifest):
        """Commit a working manifest with changes to the vault.

        If not a manifest, raise ValueError; if not working (frozen), raise
        zc.freeze.interfaces.FrozenError; if the manifest has no changes
        from the last manifest and has the same bases, raise a NoChangesError;
        if the manifest does not contain a relationship from the top_token,
        raise a ValueError.

        If the vault has previous commits, the new manifest must share a base
        (or else raise ValueError) and must be based on or updating to the
        current manifest (or else raise OutOfDateError).

        If manifest is being updated, completeUpdate; this will raise conflict
        errors as usual.  Otherwise, check for orphan errors and parent
        errors, and raise ConflictError.

        declare the manifest's base vault to be this one and freeze it.
        Store it in the vault and assign it a revision_number.  Assign all of
        the `next` pointers to the changed relationships in the now-old
        manifest.  Fire a ManifestCommitted event.
        """

    def commitFrom(source, filter=None):
        """commit changes from a working manifest, without freezing it.
        
        The source (working manifest) is updated to the new head of the
        vault.
        
        The filter, if given, should be a callable that takes a relationship
        and returns a boolean specifying whether the relationship should be
        committed.
        
        [the following section duplicates a section from the `commit`
        description]

        If not a manifest, raise ValueError; if not working (frozen), raise
        zc.freeze.interfaces.FrozenError; if the manifest has no changes
        from the last manifest and has the same bases, raise a NoChangesError;
        if the manifest does not contain a relationship from the top_token,
        raise a ValueError.

        If the vault has previous commits, the new manifest must share a base
        (or else raise ValueError) and must be based on or updating to the
        current manifest (or else raise OutOfDateError).

        If manifest is being updated, completeUpdate; this will raise conflict
        errors as usual.  Otherwise, check for orphan errors and parent
        errors, and raise ConflictError.
        
        [end duplication]
        
        If the selected changes from the source result in a new manifest that
        has any parent or orphan conflicts, raise ConflictError.
        
        If we get this far, commit the new new head and update the source to
        the head.
        """

    def mergeFrom(source):
        """Create and commit a copy of a frozen manifest to the vault.
        
        If source is not frozen, not a manifest, or does not share intids
        with this vault, raise a ValueError.  If the manifest has no changes
        from the last manifest and has the same bases, raise a NoChangesError;
        if the manifest does not contain a relationship from the top_token,
        raise a ValueError.

        declare the manifest's base vault to be this one and freeze it.
        Store it in the vault and assign it a revision_number.  Assign all of
        the `next` pointers to the changed relationships in the now-old
        manifest.  Fire a ManifestCommitted event.
        """

#### MANIFEST ####

class IReadManifest(zope.interface.Interface):
    """XXX
    
    Must implement, or be adaptable to, zc.freeze.interfaces.IFreezing.
    (a readonly manifest would effectively be frozen).
    """
    # __parent__ should typically be vault and __name__ should be
    # unicode(revision_number)

    def copy():
        """return an unfrozen full-IManifest copy of this manifest"""

    revision_number = interface.Attribute(
        'the index of the manifest in its vault')

    def getBaseSources():
        '''iterate over all bases (per vault).  The order is arbitrary but
        must be stable.''' # restriction of stable order may be lifted later

    def getBaseSource(vault):
        '''get the base for the vault'''

    merged_sources = interface.Attribute(
        '''a tuple of the non-base merged sources, as found in
        getBaseSources.''')

    base_source = interface.Attribute(
        """the manifest used as a base for this one.""")

    vault = zope.interface.Attribute(
        "the IVault with which this manifest is associated")

    def iterChanges(base=None):
        ''''iterate over all selected relationships that differ from the base.
        if base is not given, uses self.base_source'''

    def iterAll():
        '''iterate over all relationships known (of all types)'''

    def iterSelections():
        '''iterate over all selected relationships.'''

    def __iter__():
        '''iterate over linked, selected relationships: selected non-orphans.
        '''

    def iterUnchangedOrphans():
        '''iterate over BASE and MERGED orphans (that do not cause conflicts)
        '''

    next = interface.Attribute('the next manifest in the vault')

    previous = interface.Attribute(
        "the previous manifest in the vault, or from a branch's source")

    def isOption(relationship):
        """boolean, whether relationship is known (in iterAll)"""

    def getBase(token, default=None):
        '''Get the base relationship for the token, or default if None'''

    def getLocal(token, default=None):
        '''Get the local relationship for the token, or default if None'''

    def get(token, default=None):
        '''return the currently selected relationship for the token'''

    def getType(relationship):
        '''return type of relationship: one of BASE, LOCAL, UPDATED,
        SUGGESTED, MODIFIED, MERGED (see constants in this file, above).

        BASE relationships are those in the base_source (which is the manifest
        from the current vault on which this manifest was based).  There will
        only be zero or one BASE relationship for any given token in a
        manifest.

        LOCAL relationships are new relationships added (replacing or in
        addition to BASE) when not updating.  They may not be modified while
        the manifest is updating.  There will only be zero or one LOCAL
        relationship for any given token in a manifest.

        UPDATED relationships only are available in this manifest while
        updating, and are relationships changed from the BASE of the same
        token.  They may not be modified, even if they have not been versioned
        (e.g., added via `beginCollectionUpdate`). There will only be zero or
        one UPDATED relationship for any given token in a manifest.

        SUGGESTED relationships only exist while updating, and are intended to
        be relationships that an IConflictResolver created (although the
        resolvers have free reign).  They may not be modified, even if they
        have not been versioned.  There will be zero or more (unbounded)
        SUGGESTED relationships for any given token in a manifest. All
        MODIFIED relationships are discarded after an `abortUpdate`.

        MODIFIED relationships only exist while updating, and are the only
        relationships that may be modified while updating. There will be zero
        or more (unbounded) MODIFIED relationships for any given token in a
        manifest. Unselected MODIFIED relationships are discarded after an
        `completeUpdate`, and all MODIFIED relationships are discarded after
        an `abortUpdate`.

        MERGED relationships are those in the manifests returned by
        `getBaseSources` that are not the `base_source`: that is, typically
        those in manifests that have been merged into this one.  There will
        be zero or more MERGED relationships--no more than
        `len(self.getBaseSources()) -1`--in a manifest for a given token.

        '''

    def isSelected(relationship):
        '''bool whether relationship is selected'''

    def iterParents(token):
        '''iterate over all possible parents, selected and unselected, for the
        token'''

    def isLinked(token, child):
        '''returns boolean, whether child token is transitively linked
        beneath token using only selected relationships.'''

    def iterSelectedParents(token):
        '''Iterate over selected parent for the token.  If there is more than
        one, it is a parent conflict; if there are none and the token is not
        the zc.vault.keyref.top_token, it is an orphan (but not necessarily
        an orphan conflict as defined in IWriteManifest.iterOrphanConflicts,
        since orphaned BASE relationships are not regarded as conflicts).'''
        # parent conflicts should only happen with merge; only BASE orphans
        # should be possible.

    def iterMerged(token):
        '''Iterate over merged relationships for the token.'''

class IWriteManifest(zope.interface.Interface):

    def addLocal(relationship, force=False):
        '''add local copy except during update.  If no other relationship
        exists for the token, select it.  If no relationship already exists
        for the child tokens, disallow, raising ValueError.'''

    def checkRelationshipChange(relationship):
        """raise errors if the relationship may not be changed.
        UpdateError if the manifest is updating and the relationship is LOCAL;
        TypeError (XXX?) if the relationship is SUGGESTED or UPDATED"""

    def reindex(relationship):
        '''reindex the relationship after a change: used by relationships.'''

    def select(relationship):
        '''select the relationship for the given token.  There should always be
        one and only one selected relationship for any given token known about
        by the manifest.'''

    def iterOrphanConflicts():
        '''iterate over unresolved orphan conflicts--selected relationships
        changed from the BASE and MERGED relationships.'''

    def iterOrphanResolutions():
        '''iterate over resolved orphan conflicts.'''

    def isOrphan(token):
        '''Whether token is an orphan.'''

    def isOrphanConflict(token):
        '''Whether token is an unresolved orphan token, as found in
        iterOrphanConflicts'''

    def resolveOrphanConflict(token):
        '''resolve the orphan conflict'''

    def undoOrphanConflictResolution(token):
        '''undo orphan conflict resolution'''

class IMergeableManifest(zope.interface.Interface):

    # data about merge

    update_source = interface.Attribute(
        '''the manifest used for the upate''')

    update_base = interface.Attribute(
        '''the manifest for the shared ancestor that the two manifests share'''
        )

    updating = interface.Attribute(
        '''boolean.  whether in middle of update.''')

    def getUpdated(token, default=None):
        '''Get the updated relationship for the token, or default if None'''

    def iterSuggested(token):
        '''Iterate over suggested relationships for the token.'''

    def iterModified(token):
        '''Iterate over modified relationships for the token.'''

    # starting and stopping a merge

    def beginUpdate(source=None, base=None):
        '''begin an update.  Calculates update conflicts, tries to resolve.
        If source is None, uses vault's most recent manifest.  If base is None,
        uses the most recent shared base between this manifest and the source,
        if any.

        if already updating, raise UpdateError.

        update conflicts (different changes from the base both locally and in
        the source) are given to an interfaces.IConflictResolver, if an
        adapter to this interface is provided by the vault, to do with as it
        will (typically including making suggestions and resolving).'''

    def beginCollectionUpdate(source):
        '''cherry-pick update interface.
        
        If you wanted to cherry-pick some changes from a manifest, the
        procedure would be this:
        - divide up desired changes from postponed changes
        - beginCollectionUpdate(changes)
        - [...handle conflicts...]
        - completeUpdate()
        - commit()
        - create a new manifest based on the newly committed manifest
        - beginCollectionUpdate(postponed)
        - [...handle conflicts...]
        - completeUpdate()
        
        The common case--no handling of conflicts, just errors--can be
        accomplished more simply with the `IVault.commitFrom` method.
        '''

    def completeUpdate():
        '''moves update source to bases; turns off updating; discards unused
        suggested, modified, and local relationships.

        Newer versions of the bases of the update source will replace the
        bases of this manifest. if a BASE or MERGED relationship (see getType
        for definitions) is selected and its source is no longer a part of the
        bases after the bases are replaced, a new (mutable) copy is created as
        a local relationship.'''

    def abortUpdate():
        '''return manifest to state before beginUpdate.'''

    # identify problems with a merge (also see iterOrphanConflicts)

    def iterUpdateConflicts():
        '''iterate over unresolved update conflicts.'''

    def iterUpdateResolutions():
        '''iterate over resolved update conflicts.'''

    def isUpdateConflict(token):
        '''returns boolean, whether token is an unresolved update conflict.'''

    def iterParentConflicts():
        '''iterate over all selected relationships that have more than
        one parent.'''
        # parent conflicts should only happen with merge

    # manipulating a merge

    def addModified(relationship):
        '''add modified copies during update  If no other relationship
        exists for the token, select it.  If no relationship already exists
        for the child tokens, disallow, raising ValueError.'''

    def addSuggested(relationship):
        '''add suggested copies during update.  Another relationship must
        already exist in the manifest for the relationship's token.'''

    def resolveUpdateConflict(token):
        '''resolve the update conflict ("stop complaining, and use whatever is
        selected")'''

class IManifest(IReadManifest, IWriteManifest, IMergeableManifest):

