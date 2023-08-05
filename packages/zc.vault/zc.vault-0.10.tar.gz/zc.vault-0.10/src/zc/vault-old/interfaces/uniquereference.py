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