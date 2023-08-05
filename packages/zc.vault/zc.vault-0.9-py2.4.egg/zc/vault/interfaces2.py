import zope.interface
import zope.interface.common.sequence

class IUniqueReference(zope.interface.Interface):

    identifiers = zope.interface.Attribute(
        """An iterable of identifiers for this object.
        From most general to most specific.  Combination uniquely identifies
        the object.""")

    def __hash__():
        """return a hash of the full set of identifiers."""

    def __cmp__(other):
        """Compare against other objects that provide IUniqueReference,
        using the identifiers.""" # note that btrees do not support rich comps


class IBaseRelationship(IUniqueReference):
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

    copy_source = zope.interface.Attribute(
        """A tuple of the relationship and manifest that was the source of
        this relationship. or None, if it was not generated from copy or
        copyFrozen""")


class IHierarchyRelationship(IBaseRelationship):

    children = zope.interface.Attribute(
        """a set of the tokens "contained" by the `token` for this `type`.
        It is an error to have more than one selected relationship with the
        same token as a child: a token has only one allowed child
        (hierarchical) relationship for a given relationship type.""")


class ILinksRelationship(IBaseRelationship):

    links = zope.interface.Attribute(
        """a set of the tokens linked to by the `token` for this `type`.""")


class IVault(zope.interface.common.sequence.IFiniteSequence):

    additional_relationship_indexes = zope.interface.Attribute(
        """a tuple of dictionaries that are used to configure the manifest's
        relationship indexes""")

    contains_links = zope.interface.Attribute(
        """a bool describing whether manifests will index and handle
        ILinksRelationship.links.  Links are only maintained in validating
        that they point to an available token.""")

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

    def createBranch(ix=-1):
        """create a new vault with the first manifest based on the given
        manifest specified by ix.  `intids`, `contains_links`,
        `relationship_types` and `additional_relationship_indexes` are
        shared."""

    manifest = zope.interface.Attribute(
        """The most recent committed manifest (self[-1]).  Readonly.""")'

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

    def commitFrom(source):
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

class IManifest(zc.freeze.interfaces.):
    # __parent__ should typically be vault and __name__ should be
    # unicode(revision_number)

    vault = zope.interface.Attribute(
        "the IVault with which this manifest is associated")

    def copy():
        """return an unfrozen copy of this manifest"""

    def addLocal(relationship, force=False):
        """XXX"""
