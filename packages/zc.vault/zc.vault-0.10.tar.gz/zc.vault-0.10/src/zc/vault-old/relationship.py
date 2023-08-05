import zope.interface
import zc.freeze
import zc.vault.interfaces

import zc.vault.keyref


class Relationship(zc.vault.keyref.Token, zc.freeze.Freezing):
    zope.interface.implements(zc.vault.interfaces.IRelationship)

    _token = next = _copy_source = None
    zc.freeze.makeProperty('name')
    zc.freeze.makeProperty('revision')

    default_name = u''

    def __init__(self, token=None, name=None):
        if name is None:
            name = self.default_name
        self.name = name
        self.token = token

    @property
    def previous(self):
        if self.manifest is None:
            return None
        ix = self.manifest.revision_number
        if ix > 0:
            return self.manifest.vault[ix-1].get(self.token)
        return None

    @property
    def copy_source(self):
        return self._copy_source

    @property
    def token(self):
        return self._token
    @zc.freeze.setproperty
    def token(self, value):
        if self._token is None:
            self._token = value
        elif not isinstance(value, int):
            raise ValueError('token must be int')
        else:
            self._token = value

    def equalData(self, other):
        # OVERRIDE if you subclass and add more values!
        return self.token == other.token and self.name == other.name

    def _copyImmutables(self, source_manifest, token=None, **kwargs):
        # OVERRIDE if you add more immutable values
        kwargs['token'] = token or self.token
        new = self.__class__(self.name, **kwargs)
        new._copy_source = (self, source_manifest)
        return new

    def copy(self, source_manifest, token=None):
        # OVERRIDE if you add more dynamic values
        return self._copyImmutables(source_manifest, token)

    def copyFrozen(self, source_manifest):
        # OVERRIDE if you add more dynamic values
        if not self._z_frozen:
            raise ValueError('source must be frozen')
        new = self._copyImmutables(source_manifest, token)
        new._z_freeze()
        return new
