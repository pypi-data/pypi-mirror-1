import BTrees.IOBTree
import BTrees.OOBTree
import BTrees.IFBTree
import persistent

import zope.interface
import zope.interface.common
import zope.lifecycleevent
import zc.freeze

import zc.vault.interfaces
import zc.vault.keyref
import zc.vault.utils

try:
    any
except NameError:
    any = zc.vault.utils.any

# XXX additional_relationship_indexes should be made to work or removed

class Vault(zc.vault.utils.BTreeReadSequence):

    zope.interface.implements(zc.vault.interfaces.IVault)

    def __init__(self, intids, relationship_names=(u'',),
                 contains_shortcuts=False, additional_relationship_indexes=()):
        super(Vault, self).__init__()
        if relationship_names is not None:
            tmp = []
            for t in relationship_names:
                if not isinstance(t, basestring):
                    raise ValueError('name must be unicode (or string)', t)
                tmp.append(unicode(t))
            if not tmp:
                relationship_names = (u'',)
            else:
                relationship_names = tuple(tmp)
        else:
            relationship_names = (u'',)
        self._relationship_names = relationship_names
        self._contains_shortcuts = bool(contains_shortcuts)
        self._additional_relationship_indexes = tuple(
            d.items() for d in additional_relationship_indexes)
        self._intids = intids # for relationships
        self._top_token = intids.register(zc.vault.keyref.top_token)

    @property
    def additional_relationship_indexes(self):
        return tuple(
            dict(items) for items in self._additional_relationship_indexes)

    @property
    def contains_shortcuts(self):
        return self._contains_shortcuts

    @property
    def relationship_names(self):
        return self._relationship_names

    @property
    def intids(self):
        return self._intids

    @property
    def top_token(self):
        return self._top_token

    def createBranch(self, ix=-1):
        if not isinstance(ix, int):
            raise ValueError('ix must be int')
        res = self.__class__(self.intids, self.relationship_names,
                             self.contains_shortcuts,
                             self.additional_relationship_indexes)
        res.commit(self[ix].copy())
        return res

    @property
    def manifest(self):
        if self._data:
            return self._data[self._data.maxKey()]
        return None

    def commit(self, manifest):
        self._verify(manifest)
        self._commit(manifest)

    def _verify(self, manifest):
        if not zc.vault.interfaces.IManifest.providedBy(manifest):
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
                raise zc.vault.interfaces.OutOfDateError(manifest)

    def _commit(self, manifest):
        if manifest._z_frozen:
            raise zc.freeze.interfaces.FrozenError(manifest)
        if manifest.get(self.top_token) is None:
            raise ValueError(
                'cannot commit a manifest without a top_token relationship')
        if (self.manifest is not None and
            not any(manifest.iterChanges(self.manifest)) and
            self.manifest.getBaseSources() == manifest.getBaseSources()):
            raise zc.vault.interfaces.NoChangesError(manifest)
        if manifest.updating:
            # this raises errors with orphan, parent, or update conflicts
            manifest.completeUpdate()
        elif (any(manifest.iterOrphanConflicts()) or
              any(manifest.iterParentConflicts())):
             # don't need to check for update conflicts because not updating
            raise zc.vault.interfaces.ConflictError(manifest)
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
        event.notify(zc.vault.interfaces.ManifestCommitted(manifest))

    def commitFrom(self, source, filter=None):
        if source.updating:
            raise ValueError('cannot commitFrom a source during an update')
        self._verify(source)
        commit = [c for c in source.iterChanges(self.manifest)
                  if filter is None or filter(c)]
        if not commit:
            raise zc.vault.interfaces.NoChangesError(source)
        new = self.manifest.copy()
        event.notify(
            zope.lifecycleevent.ObjectCreatedEvent(new))
        new.beginCollectionUpdate(commit)
        new.completeUpdate() # this may raise; that's fine
        self._commit(new)
        source.update(new) # we don't want local changes for the committed bits
        source.completeUpdate() # if this raises an error, that's bad

    def mergeFrom(self, source):
        if not zc.vault.interfaces.IManifest.providedBy(source):
            raise ValueError('source must be an IManifest')
        if source.vault.intids is not self.intids:
            raise ValueError('source must share intids')
        if not source._z_frozen:
            raise ValueError('source must already be versioned')
        res = self.manifest.copy()
        event.notify(
            zope.lifecycleevent.ObjectCreatedEvent(res))
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


_BASE_INDEX = (
    {'element': zc.vault.interfaces.IBaseRelationship['token'],
     'dump': None, 'load': None, 'btree': BTrees.IIBTree},
    {'element': zc.vault.interfaces.IHierarchyRelationship['children'],
     'multiple': True, 'dump': None, 'load': None,
     'name': 'child', 'btree': BTrees.IIBTree})

_SHORTCUT_INDEX = (
    {'element': zc.vault.interfaces.IShortcutRelationship['shortcuts'],
     'multiple': True, 'dump': None, 'load': None,
     'name': 'shortcut', 'btree': BTrees.IIBTree},)

_NAME_INDEX = (
    {'element': zc.vault.interfaces.IBaseRelationship['name'],
     'dump': nameDump, 'load': nameLoad, 'btree': BTrees.IIBTree},)

def localDump(obj, index, cache):
    # NOTE: a reference to this function is persisted!
    return index.__parent__.vault.intids.register(obj)

def localLoad(token, index, cache):
    # NOTE: a reference to this function is persisted!
    return index.__parent__.vault.intids.getObject(token)

def nameDump(obj, index, cache):
    # NOTE: a reference to this function is persisted!
    for ix, val in index.__parent__.vault.relationship_names:
        if val == obj:
            return ix
    raise LookupError('not a valid relationship name for this vault', obj)

def nameLoad(token, index, cache):
    # NOTE: a reference to this function is persisted!
    return index.__parent__.vault.


# XXX check for links.

class Manifest(persistent.Persistent, zc.freeze.Freezing):

    zope.interface.implements(zc.vault.interfaces.IManifest)

    _updateSource = _updateBase = None

    def __init__(self, base=None, vault=None):
        if vault is None:
            if base is None:
                raise ValueError('must provide base or vault')
            vault = base.vault
        elif base is not None:
            if base.vault is not vault and base.getBaseSource(vault) is None:
                raise ValueError(
                    "explicitly passed vault must have a base in base_source.")
        else: # vault but not base
            base = vault.manifest
        if base is not None and not base._z_frozen:
            raise ValueError('base must be versioned')
        self._vault = vault
        attrs = _BASE_INDEX
        if vault.contains_shortcuts:
            attrs += _SHORTCUT_INDEX
        if len(vault.relationship_names) > 1:
            attrs += _NAME_INDEX
        attrs += vault.additional_relationship_indexes
        self._index = index.Index(
            attrs,
            index.TransposingTransitiveQueriesFactory('token', 'child'),
            localDump, localLoad)
        self._index.__parent__ = self
        self._selections = BTrees.IFBTree.IFTreeSet()
        self._oldSelections = BTrees.IFBTree.IFTreeSet()
        self._conflicts = BTrees.IFBTree.IFTreeSet()
        self._resolutions = BTrees.IFBTree.IFTreeSet()
        self._orphanResolutions = BTrees.IFBTree.IFTreeSet()
        self._oldOrphanResolutions = BTrees.IFBTree.IFTreeSet()
        self._updated = BTrees.IFBTree.IFTreeSet()
        self._local = BTrees.IFBTree.IFTreeSet()
        self._suggested = BTrees.IFBTree.IFTreeSet()
        self._modified = BTrees.IFBTree.IFTreeSet()
        self._bases = BTrees.IOBTree.IOBTree()
        if base:
            self._indexBases(base.getBaseSources(), base, True)

    def _indexBases(self, bases, base=None, select=False):
        intids = component.getUtility(zope.app.intid.interfaces.IIntIds)
        bases = dict((intids.register(b.vault), b) for b in bases)
        if base is not None:
            bid = intids.register(base.vault)
            bases[bid] = base
        else:
            bid = None
        assert not self._bases, (
            'programmer error: _indexBases should not be called with '
            'populated _bases')
        for iid, b in bases.items():
            select_this = select and iid==bid
            base_set = BTrees.IFBTree.IFTreeSet()
            data = (base_set, b)
            register = self.vault.intids.register
            for rel in b:
                rid = register(rel)
                base_set.insert(rid)
                if select_this:
                    self._selections.insert(rid)
                    event.notify(interfaces.RelationshipSelected(rel, self))
                self._index.index_doc(rid, rel)
            self._bases[iid] = data

    zc.freeze.makeProperty('revision_number')

    def getBaseSources(self):
        return tuple(data[1] for iid, data in sorted(self._bases.items()))

    def getBaseSource(self, vault):
        intids = component.getUtility(zope.app.intid.interfaces.IIntIds)
        iid = intids.queryId(vault)
        if iid is not None:
            data = self._bases.get(iid)
            if data is not None:
                return data[1]

    @property
    def base_source(self):
        return self.getBaseSource(self.vault)

    _vault = None
    @property
    def vault(self):
        return self._vault
    @zc.freeze.setproperty
    def vault(self, value):
        if self.updating:
            raise interfaces.UpdateError('Cannot change vault while updating')
        if value is not self._vault:
            old = self._vault
            s = set(old.intids.getObject(t) for t in self._selections)
            bases = tuple(self.getBaseSources())
            self._selections.clear()
            l = set(old.intids.getObject(t) for t in self._local)
            self._local.clear()
            self._index.clear()
            self._bases.clear()
            self._vault = value
            self._indexBases(bases)
            for r in l:
                self._add(r, self._local, True)
            self._selections.update(value.intids.register(r) for r in s)
            event.notify(interfaces.VaultChanged(self, old))

    @property
    def merged_sources(self):
        v = self.vault
        return tuple(b for b in self.getBaseSources() if b.vault is not v)

    @property
    def update_source(self):
        return self._updateSource

    @property
    def update_base(self):
        return self._updateBase

    @property
    def updating(self):
        return self._updateSource is not None

    @zc.freeze.method
    def _z_freeze(self):
        if self.updating:
            raise zc.freeze.interfaces.FreezingError(
                'cannot version during update')
        child_errors, shortcut_errors = self._getChildErrors()
        if (child_errors or shortcut_errors or
            list(self.iterParentConflicts()) or
            list(self.iterOrphanConflicts())):
            raise zc.freeze.interfaces.FreezingError(
                'cannot version with conflicts or errors')
        selections = set(self._iterLinked())
        b = base = self.base_source
        for r in list(self._local):
            if r not in selections:
                self._local.remove(r)
                self._index.unindex_doc(r)
            else:
                rel = self.vault.intids.getObject(r)
                if base is not None:
                    b = base.get(rel.token, rel.name)
                if b is None or not b.equalData(rel):
                    if not rel._z_frozen:
                        rel._z_freeze()
                else:
                    selections.remove(r)
                    self._local.remove(r)
                    selections.add(self.vault.intids.getId(b))
                    self._index.unindex_doc(r)
        self._selections.clear()
        self._selections.update(selections)
        super(Manifest, self)._z_freeze()

    def _add(self, relationship, set):
        if relationship.manifest is not self:
            if relationship.manifest is None:
                relationship.manifest = self
            else:
                raise ValueError(
                    'cannot add relationship already in another set')
        iid = self.vault.intids.register(relationship)
        set.insert(iid)
        self._index.index_doc(iid, relationship)

    @zc.freeze.method
    def addLocal(self, relationship):
        if self.updating:
            raise interfaces.UpdateError(
                'cannot add local relationships during update')
        if self.getLocal(relationship.token, relationship.name) is not None:
            raise ValueError(
                'cannot add a second local relationship for the same token '
                'and name')
        self._add(relationship, self._local)
        event.notify(interfaces.LocalRelationshipAdded(relationship))
        if len(self._index.findRelationshipTokenSet(
            self._index.tokenizeQuery(self._getQuery(
                relationship.token, relationship.name)))) == 1:
            self.select(relationship)

    @zc.freeze.method
    def addModified(self, relationship):
        if not self.updating:
            raise interfaces.UpdateError(
                'can only add modified relationships during update')
        self._add(relationship, self._modified)
        event.notify(interfaces.ModifiedRelationshipAdded(relationship))
        if len(self._index.findRelationshipTokenSet(
            self._index.tokenizeQuery(self._getQuery(
                relationship.token, relationship.name)))) == 1:
            self.select(relationship)

    @zc.freeze.method
    def addSuggested(self, relationship):
        if not self.updating:
            raise interfaces.UpdateError(
                'can only add suggested relationships during update')
        if len(self._index.findRelationshipTokenSet(
               self._getQuery(relationship.token, relationship.name))) == 0:
            raise ValueError('cannot add suggested relationship for new '
                             'token and name')
        self._add(relationship, self._suggested)
        event.notify(interfaces.SuggestedRelationshipAdded(relationship))

    @zc.freeze.method
    def beginUpdate(self, source=None, base=None):
        if self.updating:
            raise interfaces.UpdateError(
                'cannot begin another update while updating')
        if source is None:
            source = self.vault.manifest
        if not interfaces.IManifest.providedBy(source):
            raise ValueError('source must be manifest')
        if source.vault.intids is not self.vault.intids:
            raise ValueError('source must share intids')
        if base is None:
            if self.base_source is None or source.vault != self.vault:
                myBase = self.getBaseSource(source.vault)
                otherBase = source.getBaseSource(self.vault)
                if myBase is None:
                    if otherBase is None:
                        # argh.  Need to walk over all bases and find any
                        # shared ones.  Then pick the most recent one.
                        for b in self.getBaseSources():
                            if b.vault == self.vault:
                                continue
                            o = source.getBaseSource(b.vault)
                            if o is not None:
                                # we found one!
                                if (o._z_freeze_timestamp >
                                    b._z_freeze_timestamp):
                                    b = o
                                if base is None or (
                                    b._z_freeze_timestamp >
                                    base._z_freeze_timestamp):
                                    base = b
                        if base is None:
                            raise ValueError('no shared previous manifest')
                    else:
                        base = otherBase
                elif (otherBase is None or
                      otherBase._z_freeze_timestamp <=
                      myBase._z_freeze_timestamp):
                    base = myBase
                else:
                    base = otherBase
            else:
                base = self.base_source

        if base is source:
            raise ValueError('base is source')
        if not interfaces.IManifest.providedBy(base):
            raise ValueError('base must be manifest')
        if not source._z_frozen or not base._z_frozen:
            raise ValueError('manifests must be versioned')
        reverting = (source.revision_number - base.revision_number) < 0
        intids = self.vault.intids
        self._oldSelections.update(self._selections)
        self._oldOrphanResolutions.update(self._orphanResolutions)
        self._updateSource = source
        self._updateBase = base
        to_be_resolved = []
        for s in source:
            b = base.get(s.token, s.name)
            source_changed = b is None or (s is not b and not b.equalData(s))
            l = self.get(s.token, s.name)
            if l is None: # even if base is non-None, that change is elsewhere
                local_changed = False
            elif b is None:
                local_changed = True
            else:
                local_changed = not b.equalData(l)
            if source_changed:
                iid = intids.register(s)
                self._updated.insert(iid)
                self._index.index_doc(iid, s)
                if local_changed:
                    self._conflicts.insert((s.token, s.name))
                    if l is not s and not l.equalData(s):
                        # material difference.
                        if reverting:
                            # go ahead and select local changes and resolve
                            # (XXX use resolver instead?)
                            self.select(l)
                            self._resolutions.insert((s.token, s.name))
                        else:
                            # Give resolver a chance.
                            to_be_resolved.append((l, s, b))
                    else:
                        # we'll use the merged version by default
                        self.select(s)
                        self._resolutions.insert((s.token, s.name))
                else:
                    self.select(s)
        if to_be_resolved:
            resolver = zc.vault.interfaces.IConflictResolver(self.vault, None)
            if resolver is not None:
                for l, s, b in to_be_resolved:
                    resolver(self, l, s, b)
        event.notify(interfaces.UpdateBegun(self, source, base))

    @zc.freeze.method
    def beginCollectionUpdate(self, source):
        if self.updating:
            raise interfaces.UpdateError(
                'cannot begin another update while updating')
        source = set(source)
        count = 0
        token_mapping = {}
        for r in source:
            if r.manifest.vault.intids is not self.vault.intids:
                raise ValueError('sources must share intids')
            if r.name not in self.vault.relationship_names:
                raise ValueError('invalid relationship name', r.name, r)
            d = token_mapping.setdefault(r.token, {})
            if r.name not in d:
                count += 1
                d[r.name] = r
            elif d[r.name] is not r:
                raise ValueError(
                    'cannot provide more than one update relationship for the '
                    'same token and name', d[r.name], r)
        verify = zc.vault.interfaces.IHierarchyNameVerifier(self.vault, None)
        # example verify:
        # def verify(name_dictionary, parent, strict=False):
        #     if strict and not name_dictionary:
        #         raise ValueError(
        #             'hierarchy children must have at least one matching '
        #             'relationships in which the child is the token')
        if verify is not None:
            for rel in source:
                for child in rel.children:
                    all_names = self.getAll(child)
                    if child in token_mapping:
                        all_names.update(token_mapping[child])
                    verify(all_names, rel, strict=True)
        intids = self.vault.intids
        self._oldSelections.update(self._selections)
        self._oldOrphanResolutions.update(self._orphanResolutions)
        tmp_source = set()
        to_be_resolved = []
        for rel in source:
            if not rel._z_frozen:
                if rel.manifest is not None and rel.manifest is not self:
                    rel = rel.copy(rel.manifest)
                    rel.manifest = self
                    event.notify(
                        zope.lifecycleevent.ObjectCreatedEvent(rel))
                self._add(rel, self._updated)
            else: # XXX make sure that these are converted to new copies
                # if necessary in completeUpdate
                iid = intids.getId(rel)
                self._updated.insert(iid)
                self._index.index_doc(iid, rel)
            tmp_source.add(rel)
            local = self.getLocal(rel.token, rel.name)
            if local is not None:
                self._conflicts.insert((rel.token, rel.name))
                if local.equalData(rel):
                    self._resolutions.insert((rel.token, rel.name))
                else:
                    to_be_resolved.append((local, rel, None))
            else:
                self.select(rel)
        if to_be_resolved:
            resolver = zc.vault.interfaces.IConflictResolver(self.vault, None)
            if resolver is not None:
                for l, s, b in to_be_resolved:
                    resolver(self, l, s, b)
        self._updateSource = frozenset(tmp_source)
        child_errors, shortcut_errors = self._getChildErrors()
        assert not child_errors, shortcut_errors
        event.notify(interfaces.UpdateBegun(self, source, None))

    def _selectionsFilter(self, relchain, query, index, cache):
        return relchain[-1] in self._selections

    def _iterLinked(self):
        for p in self._index.findRelationshipTokenChains(
            {'token': self.vault.top_token}, filter=self._selectionsFilter):
            yield p[-1]

    def completeUpdate(self):
        source = self._updateSource
        if source is None:
            raise interfaces.UpdateError('not updating')
        child_errors, shortcut_errors = self._getChildErrors()
        if (child_errors or shortcut_errors or
            list(self.iterUpdateConflicts()) or
            list(self.iterParentConflicts()) or
            list(self.iterOrphanConflicts())):
            raise interfaces.UpdateError(
                'cannot complete update with conflicts or errors')
        manifest = interfaces.IManifest.providedBy(source)
        # assemble the contents of what will be the new bases
        intids = self.vault.intids
        selected = set(self._iterLinked())
        base = self._updateBase
        self._updateSource = self._updateBase = None
        self._selections.clear()
        self._selections.update(selected)
        self._local.clear()
        self._index.clear()
        self._updated.clear()
        self._modified.clear()
        self._suggested.clear()
        self._conflicts.clear()
        self._resolutions.clear()
        self._orphanResolutions.clear()
        self._oldOrphanResolutions.clear()
        self._oldSelections.clear()
        bases = self.getBaseSources()
        self._bases.clear()
        if manifest:
            global_intids = component.getUtility(
                zope.app.intid.interfaces.IIntIds)
            bases = dict((global_intids.register(b.vault), b) for b in bases)
            for b in source.getBaseSources():
                iid = global_intids.register(b.vault)
                o = bases.get(iid)
                if o is None or o._z_freeze_timestamp < b._z_freeze_timestamp:
                    bases[iid] = b
            self._indexBases(bases.values(), source)
            for i in selected:
                orig = rel = intids.getObject(i)
                base_rel = self.getBase(rel.token, rel.name)
                if rel._z_frozen:
                    if base_rel.equalData(rel):
                        rel = base_rel
                    else:
                        source_rel = source.get(rel.token, rel.name)
                        if source_rel is rel:
                            # we know it is not currently available because
                            # of above; it is selected; we need a new one
                            rel = rel.copy(source)
                            rel.manifest = self
                            event.notify(
                                zope.lifecycleevent.ObjectCreatedEvent(rel))
                            self._add(rel, self._local)
                            event.notify(
                                interfaces.LocalRelationshipAdded(rel))
                else:
                    if base_rel.equalData(rel):
                        rel = base
                    else:
                        self._add(rel, self._local)
                        event.notify(interfaces.LocalRelationshipAdded(rel))
                if orig is not rel:
                    self._selections.remove(i)
                    self.select(rel)
        else:
            self._indexBases(bases)
            existing = BTrees.IFBTree.multiunion(
                [data[0] for data in self._bases.values()])
            for i in selected:
                if i not in existing:
                    rel = intids.getObject(i)
                    if rel._z_frozen:
                        rel = rel.copy(source)
                        event.notify(
                            zope.lifecycleevent.ObjectCreatedEvent(rel))
                    self._add(rel, self._local)
                    event.notify(interfaces.LocalRelationshipAdded(rel))
        child_errors, shortcut_errors = self._getChildErrors()
        assert not (child_errors or shortcut_errors or
                    list(self.iterUpdateConflicts()) or
                    list(self.iterParentConflicts()) or
                    list(self.iterOrphanConflicts()))
        event.notify(interfaces.UpdateCompleted(self, source, base))

    def checkRelationshipChange(self, relationship):
        reltype = self.getType(relationship)
        if self.updating and reltype == interfaces.LOCAL:
            raise interfaces.UpdateError(
                'cannot change local relationships while updating')
        if reltype in (interfaces.SUGGESTED, interfaces.UPDATED):
            assert self.updating, (
                'internal state error: the system should not allow suggested '
                'or updated relationships when not updating')
            raise TypeError(
                'cannot change relationships when used as suggested or '
                'updated values')

    def abortUpdate(self):
        if self._updateSource is None:
            raise interfaces.UpdateError('not updating')
        source = self._updateSource
        base = self._updateBase
        self._updateSource = self._updateBase = None
        for s in (self._updated, self._modified, self._suggested):
            for t in s:
                self._index.unindex_doc(t)
            s.clear()
        self._conflicts.clear()
        self._resolutions.clear()
        self._orphanResolutions.clear()
        self._orphanResolutions.update(self._oldOrphanResolutions)
        self._oldOrphanResolutions.clear()
        self._selections.clear()
        self._selections.update(self._oldSelections)
        self._oldSelections.clear()
        event.notify(interfaces.UpdateAborted(self, source, base))

    def iterChanges(self, base=None):
        get = self.vault.intids.getObject
        if base is None:
            base = self.base_source
        for t in self._selections:
            rel = get(t)
            if base is None:
                yield rel
            else:
                b = base.get(rel.token, rel.name)
                if b is None or not b.equalData(rel):
                    yield rel

    @zc.freeze.method
    def reindex(self, relationship):
        t = self.vault.intids.queryId(relationship)
        if t is not None and (t in self._local or t in self._suggested or
                              t in self._modified or t in self._updated):
            self._index.index_doc(t, relationship)

    def _getQuery(self, token, name):
        if name is not None and name not in self.vault.relationship_names:
            raise ValueError('unknown relationship name', relationship.name)
        q = {'token': token}
        if len(self.vault.relationship_names > 1):
            if name is None:
                raise ValueError('ambiguous: specify relationship name')
            q['name'] = name
        return q

    def _getFromSet(self, token, name, filter_set, default):
        res = list(self._yieldFromSet(token, name, filter_set))
        if not res:
            return default
        assert len(res) == 1, 'internal error: too many in the same category'
        return res[0]

    def _yieldFromSet(self, token, name, filter_set):
        get = self.vault.intids.getObject
        for t in self._index.findRelationshipTokenSet(
            self._index.tokenizeQuery(self._getQuery(token, name))):
            if t in filter_set:
                yield get(t)

    def get(self, token, name=None, default=None):
        # return the selected relationship
        return self._getFromSet(token, name, self._selections, default)

    def getAll(self, token):
        res = {}
        get = self.vault.intids.getObject
        filter_set = sel._selections
        for t in self._index.findRelationshipTokenSet({'token': token}):
            if t in filter_set:
                rel = get(t)
                assert rel.name not in res, (
                    'programmer error: too many selected')
                res[rel.name] = rel
        return res

    def getType(self, relationship):
        t = self.vault.intids.queryId(relationship)
        if t is not None:
            if t in self._local:
                return interfaces.LOCAL
            elif t in self._updated:
                return interfaces.UPDATED
            elif t in self._suggested:
                return interfaces.SUGGESTED
            elif t in self._modified:
                return interfaces.MODIFIED
            else:
                intids = component.getUtility(
                    zope.app.intid.interfaces.IIntIds)
                iid = intids.queryId(relationship.manifest.vault)
                if iid is not None and iid in self._bases:
                    iiset, rel_set = self._bases[iid]
                    if t in iiset:
                        return interfaces.BASE
                    for bid, (iiset, rel_set) in self._bases.items():
                        if bid == iid:
                            continue
                        if t in iiset:
                            return interfaces.MERGED
        return None

    def isSelected(self, relationship):
        t = self.vault.intids.queryId(relationship)
        return t is not None and t in self._selections

    @zc.freeze.method
    def select(self, relationship):
        t = self.vault.intids.queryId(relationship)
        if t is None or self.getType(relationship) is None:
            raise ValueError('unknown relationship')
        if t in self._selections:
            return
        rel_tokens = self._index.findRelationshipTokenSet(
            self._index.tokenizeQuery(
                self._getQuery(relationship.token, relationship.name)))
        for rel_t in rel_tokens:
            if rel_t in self._selections:
                self._selections.remove(rel_t)
                event.notify(interfaces.RelationshipDeselected(
                    self.vault.intids.getObject(rel_t), self))
                break
        self._selections.insert(t)
        event.notify(interfaces.RelationshipSelected(relationship, self))

    def getBase(self, token, name=None, default=None):
        vault = self.base_source
        for iiset, rel_set in self._bases.values():
            if rel_set is vault:
                return self._getFromSet(token, name, iiset, default)

    def getLocal(self, token, name=None, default=None):
        return self._getFromSet(token, name, self._local, default)

    def getUpdated(self, token, name=None, default=None):
        return self._getFromSet(token, name, self._updated, default)

    def iterSuggested(self, token, name=None):
        return self._yieldFromSet(token, name, self._suggested)

    def iterModified(self, token, name=None):
        return self._yieldFromSet(token, name, self._modified)

    def iterMerged(self, token, name=None):
        vault = self.vault
        seen = set()
        for iiset, rel_set in self._bases.values():
            if rel_set is not vault:
                for r in self._yieldFromSet(token, iiset):
                    if r not in seen:
                        yield r
                        seen.add(r)

    def _parents(self, token):
        return self._index.findRelationshipTokenSet(
            {'token': relationship.token})

    def iterSelectedParents(self, token):
        get = self.vault.intids.getObject
        for iid in self._parents(token):
            if iid in self._selections:
                yield get(iid)

    def iterParents(self, token):
        get = self.vault.intids.getObject
        return (get(iid) for iid in self._parents(token))

    def getParent(self, token):
        good = set()
        orphaned = set()
        unselected = set()
        orphaned_unselected = set()
        for iid in self._parents(token):
            is_orphaned = self.isOrphan(iid)
            if iid in self._selections:
                if is_orphaned:
                    orphaned.add(iid)
                else:
                    good.add(iid)
            else:
                if is_orphaned:
                    orphaned_unselected.add(iid)
                else:
                    unselected.add(iid)
        for s in (good, orphaned, unselected, orphaned_unselected):
            if s:
                if len(s) > 1:
                    raise interfaces.ParentConflictError
                return self.vault.intids.getObject(s.pop())

    def isLinked(self, token, child, name=None):
        # TODO include_shortcuts=False
        if name is not None:
            query = self._getQuery(token, name)
        else:
            query = {'token': token}
        return self._index.isLinked(
            self._index.tokenizeQuery(query),
            filter=self._selectionsFilter,
            targetQuery=self._index.tokenizeQuery({'child': child}))

    def iterUpdateConflicts(self):
        # any unresolved relationship that has both update and
        # local for its token
        if self._updateSource is None:
            raise StopIteration
        get = self.vault.intids.getObject
        for t, n in self._conflicts:
            if (t, n) not in self._resolutions:
                rs = self._index.findRelationshipTokenSet(
                    self._index.tokenizeQuery(self._getQuery(t, n)))
                for r in rs:
                    if r in self._selections:
                        yield get(r)
                        break
                else:
                    assert 0, (
                        'programmer error: no selected relationship found for '
                        'conflicted token')

    def iterUpdateResolutions(self):
        if self._updateSource is None:
            raise StopIteration
        get = self.vault.intids.getObject
        for t, n in self._resolutions:
            assert (t, n) in self._conflicts, 'programmer error'
            rs = self._index.findRelationshipTokenSet(
                self._index.tokenizeQuery(self._getQuery(t, n)))
            for r in rs:
                if r in self._selections:
                    yield get(r)
                    break
            else:
                assert 0, (
                    'programmer error: no selected relationship found for '
                    'resolved token')

    def _getName(self):
        if len(self.vault.relationship_names) == 1:
            name = self.vault.relationship_names[0]
        else:
            raise ValueError('ambiguous: specify relationship name')
        return name

    def isUpdateConflict(self, token, name=None):
        if name is None:
            name = self._getName()
        return ((token, name) in self._conflicts and
                (token, name) not in self._resolutions)

    @zc.freeze.method
    def resolveUpdateConflict(self, token, name=None):
        if not self.updating:
            raise interfaces.UpdateError(
                'can only resolve merge conflicts during update')
        if name is None:
            name = self._getName()
        if (token, name) not in self._conflicts:
            raise ValueError('token does not have merge conflict')
        self._resolutions.insert((token, name))

    def _iterOrphans(self, condition):
        get = self.vault.intids.getObject
        res = set(self._selections)
        res.difference_update(self._iterLinked())
        bases = BTrees.IFBTree.multiunion([d[0] for d in self._bases.values()])
        res.difference_update(bases)
        for t in res:
            tids = self._index.findValueTokenSet(t, 'token')
            assert len(tids) == 1
            tid = iter(tids).next()
            if not condition(tid):
                continue
            yield get(t)

    def iterOrphanConflicts(self):
        return self._iterOrphans(lambda t: t not in self._orphanResolutions)

    def iterOrphanResolutions(self):
        return self._iterOrphans(lambda t: t in self._orphanResolutions)

    def iterUnchangedOrphans(self):
        get = self.vault.intids.getObject
        res = set(self._selections)
        res.difference_update(self._iterLinked())
        bases = BTrees.IFBTree.multiunion([d[0] for d in self._bases.values()])
        res.intersection_update(bases)
        return (get(t) for t in res)

    def isOrphan(self, token):
        return not (token == self.vault.top_token or
                    self.isLinked(self.vault.top_token, token))

    def isOrphanConflict(self, token):
        return (self.isOrphan(token) and
                self.getType(token) not in (interfaces.BASE, interfaces.MERGED)
                and token not in self._orphanResolutions)

    @zc.freeze.method
    def resolveOrphanConflict(self, token):
        self._orphanResolutions.insert(token)

    @zc.freeze.method
    def undoOrphanConflictResolution(self, token):
        self._orphanResolutions.remove(token)

    def iterParentConflicts(self):
        get = self.vault.intids.getObject
        seen = set()
        for r in self._iterLinked():
            if r in seen:
                continue
            seen.add(r)
            ts = self._index.findValueTokenSet(r, 'token')
            assert len(ts) == 1
            t = iter(ts).next()
            paths = list(self._index.findRelationshipTokenChains(
                {'child': t}, filter=self._selectionsFilter,
                targetQuery={'token': self.vault.top_token}))
            if len(paths) > 1:
                yield get(r)

    def _getChildErrors(self):
        tokens = set()
        children = set()
        shortcuts = set()
        for rid in self._iterLinked():
            tokens.update(self._index.findValueTokenSet(rid, 'token'))
            children.update(self._index.findValueTokenSet(rid, 'child'))
            if self.vault.contains_shortcuts:
                shortcuts.update(
                    self._index.findValueTokenSet(rid, 'shortcut'))
        children.difference_update(tokens)
        if self.vault.contains_shortcuts:
            shortcuts.difference_update(tokens)
        return children, shortcuts # these are token ids

    def getChildErrors(self):
        return self._getChildErrors()[0]

    def getShortcutErrors(self):
        return self._getChildErrors()[1]

    def iterAll(self):
        get = self.vault.intids.getObject
        seen = set()
        for s in (self._local, self._updated, self._suggested,
                  self._modified):
            for t in s:
                if t not in seen:
                    yield get(t)
                    seen.add(t)
        for iidset, rel_set in self._bases.values():
            for t in iidset:
                if t not in seen:
                    yield get(t)
                    seen.add(t)

    def iterSelections(self):
        get = self.vault.intids.getObject
        return (get(t) for t in self._selections)

    def __iter__(self):
        get = self.vault.intids.getObject
        return (get(t) for t in self._iterLinked())

    @property
    def previous(self):
        i = self.vault_index
        if i is not None and len(self.vault)-1 >= i and self.vault[i] is self:
            if i > 0:
                return self.vault[i-1]
            return None
        return self.base_source

    @property
    def next(self):
        i = self.vault_index
        if i is not None and len(self.vault) > i+1 and self.vault[i] is self:
            return self.vault[i+1]
        return None

    def isOption(self, relationship):
        for rel in self._index.findRelationships(
            self._index.tokenizeQuery(
                self._getQuery(relationship.token, relationship.name))):
            if rel is relationship:
                return True
        return False
