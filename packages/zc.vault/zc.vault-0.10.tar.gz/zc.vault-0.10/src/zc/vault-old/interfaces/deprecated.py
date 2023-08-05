
import zope.interface
import zc.vault.interfaces.foundation
import zc.vault.interfaces.containment


class IVault(zc.vault.interfaces.foundation.IVault,
             zope.app.container.interfaces.IContained):

    def getPrevious(relationship):
        '''return the previous version of the relationship (based on token)
        or None'''

    def getNext(relationship):
        '''return the next version of the relationship (based on token)
        or None'''

    def commitFrom(source):
        '''combines the functionality of mergeFrom with commitFrom.'''


class IManifest(zc.vault.interfaces.foundation.IManifest):

    held = interface.Attribute(
        """Container of any related objects held because they were nowhere
        else.
        """) # this might get promoted back out of deprecated to someplace

    vault_index = zope.interface.Attribute(
        "revision_number")


class IRelationshipContainment(
    zc.vault.interfaces.containment.IRelationshipContainment):
    __parent__ = zope.interface.Attribute('relationship.')


class IRelationship(
    zc.vault.interfaces.containment.IObjectRelationship):

    __parent__ = interface.Attribute(
        """The manifest of this relationship before versioning (may be
        reused for other manifests after being versioned)""")


class IInventoryVault(
    IVault,
    zc.vault.interfaces.containment.IInventoryVault):
    pass

