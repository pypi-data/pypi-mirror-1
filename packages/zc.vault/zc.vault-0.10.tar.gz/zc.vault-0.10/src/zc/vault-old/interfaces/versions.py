import zope.interface

class IReadVersions(zope.interface.Interface):
    """abstract: see IVersions"""

    vault = zope.interface.Attribute(
        """the vault that this collection of versions uses.""")

    factory = zope.interface.Attribute(
        """the (persistable) callable that gets an inventory and returns the
        persistable wrapper object that has the desired API.""")

    def __getitem__(ix):
        """return version for given index, or raise KeyError
        if no such index exists."""

    def __len__():
        """return number of versions"""

class IWriteVersions(zope.interface.Interface):
    """abstract: see IVersions"""

    def commit(version):
        """commit version"""

    def commitFrom(version):
        """commit from previous version"""

    def create():
        """create and return an editable version of the most recently
        committed."""

class IVersions(IReadVersions, IWriteVersions):
    """a collection of versions"""

class IWrapperAware(zope.interface.Interface):
    """A manifest that has a wrapper attribute pointing to it's
    desired wrapper"""

    wrapper = zope.interface.Attribute(
        """the desired wrapper""")
