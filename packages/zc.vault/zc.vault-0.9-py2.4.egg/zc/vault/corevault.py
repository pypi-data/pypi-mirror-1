import BTrees.IOBTree
import BTrees.OOBTree
import persistent

import zope.interface
import zope.interface.common

import zc.vault.interfaces2
import zc.vault.keyref
import zc.vault.utils

try:
    any
except NameError:
    any = zc.vault.utils.any


class Vault(zc.vault.utils.BTreeReadSequence):

    interface.implements(zc.vault.interfaces2.IVault)

    def __init__(self, intids, relationship_types=(u'',),
                 contains_links=False, additional_relationship_indexes=()):
        super(Vault, self).__init__()
        if relationship_types is not None:
            tmp = []
            for t in relationship_types:
                if not isinstance(t, basestring):
                    raise ValueError('type must be unicode (or string)', t)
                tmp.append(unicode(t))
            if len(tmp) == 0:
                relationship_types = (u'',)
            else:
                relationship_types = tuple(tmp)
        else:
            relationship_types = (u'',)
        self._relationship_types = relationship_types
        self._contains_links = bool(contains_links)
        self._additional_relationship_indexes = tuple(
            d.items() for d in additional_relationship_indexes)
        self._intids = intids # for relationships
        self._top_token = intids.register(zc.vault.keyref.top_token)

    @property
    def additional_relationship_indexes(self):
        return tuple(
            dict(items) for items in self._additional_relationship_indexes)

    @property
    def contains_links(self):
        return self._contains_links

    @property
    def relationship_types(self):
        return self._relationship_types

    @property
    def intids(self):
        return self._intids

    @property
    def top_token(self):
        return self._top_token

    def createBranch(self, ix=-1):
        if not isinstance(ix, int):
            raise ValueError('ix must be int')
        res = self.__class__(self.intids, self.relationship_types,
                             self.contains_links,
                             self.additional_relationship_indexes)
        res.commit(self[ix].copy())
        return res

    @property
    def manifest(self):
        if self._data:
            return self._data[self._data.maxKey()]
        return None

    def commit(self, manifest):
        if not zc.vault.interfaces2.IManifest.providedBy(manifest):
            raise ValueError('may only commit an IManifest')
        current = self.manifest
        if current is not None:
            # id should be safe here--objects will be the same within a given
            # connection, and we are just using them for unambiguous set
            # operations.
            current_vaults = set(id(b.vault) for b in current.getBaseSources())
            current_vaults.add(id(current.vault))
            new_vaults = set(id(b.vault) for b in manifest.getBaseSources())
            new_vaults.add(id(manifest.vault))
            if not current_vaults & new_vaults:
                raise ValueError(
                    'may only commit a manifest with at least one shared base')
            elif manifest.getBaseSource(self) is not current and (
                not manifest.updating or (
                    manifest.updating and
                    manifest.update_source is not current)):
                raise zc.vault.interfaces2.OutOfDateError(manifest)
        self._commit(manifest)

    def _commit(self, manifest):
        if manifest._z_frozen:
            raise zc.freeze.interfaces.FrozenError(manifest)
        if manifest.get(self.top_token) is None:
            raise ValueError(
                'cannot commit a manifest without a top_token relationship')
        if (self.manifest is not None and
            not any(manifest.iterChanges(self.manifest)) and
            self.manifest.getBaseSources() == manifest.getBaseSources()):
            raise zc.vault.interfaces2.NoChangesError(manifest)
        if manifest.updating:
            # this raises errors with orphan, parent, or update conflicts
            manifest.completeUpdate()
        elif (any(manifest.iterOrphanConflicts()) or
              any(manifest.iterParentConflicts())):
             # don't need to check for update conflicts because not updating
            raise zc.vault.interfaces2.ConflictError(manifest)
        manifest.vault = self
        ix = len(self)
        self._data[ix] = manifest
        manifest.revision_number = ix
        manifest._z_freeze()
        for r in manifest:
            if manifest.getLocal(r.token) is r:
                p = r.previous
                if p is not None and p.manifest.vault is self:
                    p.next = r
        event.notify(zc.vault.interfaces2.ManifestCommitted(manifest))

    def commitFrom(self, source):
        if not zc.vault.interfaces2.IManifest.providedBy(source):
            raise ValueError('source must be an IManifest')
        if source.vault.intids is not self.intids:
            raise ValueError('source must share intids')
        if not source._z_frozen:
            raise ValueError('source must already be versioned')
        res = self.manifest.copy()
        base_rels = dict((r.token, r) for r in res.base_source)
        for rel in source:
            base_rel = base_rels.pop(rel.token, None)
            if base_rel is None or not base_rel.equalData(rel):
                rel = rel.copyFrozen(source)
                event.notify(
                    zope.lifecycleevent.ObjectCreatedEvent(rel))
                res.addLocal(rel, force=True)
        # Note that base orphans are not regarded as conflicts, so we don't
        # need to be careful with orphan conflicts.
        self._commit(res)
