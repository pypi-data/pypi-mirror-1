import BTrees.IIBTree
import persistent
import zope.interface
import zope.app.container.contained
import zc.freeze

import zc.vault.interfaces2


# XXX use `any` more
# XXX don't allow to start updating if parent or orphan conflicts?
# XXX commitFrom should only rely on manifest interface (currently _local
#     and _add)


def getPrevious(relationship):
    manifest = relationship.manifest # first one with this relationship
    ix = manifest.revision_number
    if ix > 0:
        return manifest.vault[ix-1].get(relationship.token)
    return None


def getNext(relationship):
    manifest = relationship.manifest # first one with this relationship
    return manifest.nextIndex.get(relationship.token)


_BASE_INDEX = ({'element': zc.vault.interfaces2.IBaseRelationship['token'],
                'dump': None, 'load': None, 'btree': IIBTree},
               {'element': zc.vault.interfaces2.IHierarchyRelationship['children'],
                'multiple': True, 'dump': None, 'load': None,
                'name': 'child', 'btree': IIBTree})

_LINK_INDEX = ({'element': zc.vault.interfaces.ILinkRelationship['links'],
                'multiple': True, 'dump': None, 'load': None,
                'name': 'link', 'btree': IIBTree},)

_TYPE_INDEX = ({'element': zc.vault.interfaces.IBaseRelationship['type'],
                'dump': typeMap.__getitem__, 'load': typeMap.getKey},)

class Manifest(persistent.Persistent, zc.freeze.Freezing,
               zope.app.container.contained.Contained):

    zope.interface.implements(zc.vault.interfaces2.IManifest)

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
        self.__parent__ = self._vault = vault
        attrs = _BASE_INDEX
        if vault.contains_links:
            attrs += _LINK_INDEX
        if len(vault.relationship_types) > 1:
            attrs += _TYPE_INDEX
        self._index = index.Index(
            ,
              # optional if only one type
             {'element': zc.vault.interfaces.IBaseRelationship['type'],
              'dump': typeMap.__getitem__, 'load': typeMap.getKey},
              # this one could be optional; simpler if it is built in
             {'element': zc.vault.interfaces.ILinkRelationship['links'],
              'multiple': True, 'dump': None, 'load': None,
              'name': 'link', 'btree': IIBTree}) + vault.additional,
            index.TransposingTransitiveQueriesFactory('token', 'child'),
            localDump, localLoad)
        self._index.__parent__ = self
        self.nextIndex = BTrees.IOBTree.IOBTree() # rel intid to next rel intid
        self._selections = IFBTree.IFTreeSet()
        self._oldSelections = IFBTree.IFTreeSet()
        self._conflicts = IFBTree.IFTreeSet()
        self._resolutions = IFBTree.IFTreeSet()
        self._orphanResolutions = IFBTree.IFTreeSet()
        self._oldOrphanResolutions = IFBTree.IFTreeSet()
        self._updated = IFBTree.IFTreeSet()
        self._local = IFBTree.IFTreeSet()
        self._suggested = IFBTree.IFTreeSet()
        self._modified = IFBTree.IFTreeSet()
        self._bases = IOBTree.IOBTree()
        if base:
            self._indexBases(base.getBaseSources(), base, True)
        if vault.held is None:
            self._held = HeldContainer()
            zope.location.locate(self._held, self, "held")
        else:
            self._held = vault.held

    @property
    def held(self):
        return self._held

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
            base_set = IFBTree.IFTreeSet()
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

    zc.freeze.makeProperty('vault_index')

    def getBaseSources(self): # XXX in interface, note that the order must
        # be stable
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
        if (list(self.iterParentConflicts()) or
            list(self.iterOrphanConflicts())):
            raise zc.freeze.interfaces.FreezingError(
                'cannot version with conflicts')
        selections = set(self._iterLinked())
        b = base = self.base_source
        for r in list(self._local):
            if r not in selections:
                self._local.remove(r)
                self._index.unindex_doc(r)
            else:
                rel = self.vault.intids.getObject(r)
                if base is not None:
                    b = base.get(rel.token)
                if (b is None or
                    b.object is not rel.object or
                    b.containment != rel.containment):
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

    def _locateObject(self, relationship, force=False):
        if not force:
            for child in relationship.children:
                if self.get(child) is None:
                    raise ValueError(
                        'child tokens must have selected relationships')
        if relationship.token == self.vault.top_token:
            assert relationship.object is None
            return
        obj = relationship.object
        if obj is not None and getattr(obj, '__parent__', None) is None:
            if zope.location.interfaces.ILocation.providedBy(obj):
                dest = self.held
                dest[INameChooser(dest).chooseName('', obj)] = obj
            else:
                obj.__parent__ = self.vault

    def _add(self, relationship, set, force=False):
        self._locateObject(relationship, force)
        if relationship.__parent__ is not self:
            if relationship.__parent__ is None:
                relationship.__parent__ = self
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
        if self.getLocal(relationship.token) is not None:
            raise ValueError(
                'cannot add a second local relationship for the same token')
        self._add(relationship, self._local)
        event.notify(interfaces.LocalRelationshipAdded(relationship))
        if len(self._index.findRelationshipTokenSet(
            self._index.tokenizeQuery({'token': relationship.token}))) == 1:
            self.select(relationship)

    @zc.freeze.method
    def addModified(self, relationship):
        if not self.updating:
            raise interfaces.UpdateError(
                'can only add modified relationships during update')
        self._add(relationship, self._modified)
        event.notify(interfaces.ModifiedRelationshipAdded(relationship))
        if len(self._index.findRelationshipTokenSet(
            self._index.tokenizeQuery({'token': relationship.token}))) == 1:
            self.select(relationship)

    @zc.freeze.method
    def addSuggested(self, relationship):
        if not self.updating:
            raise interfaces.UpdateError(
                'can only add suggested relationships during update')
        if len(self._index.findRelationshipTokenSet(
               {'token': relationship.token})) == 0:
            raise ValueError('cannot add suggested relationship for new token')
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
        elif base._z_freeze_timestamp > source._z_freeze_timestamp:
            raise NotImplementedError(
                "don't know how to merge to older source")
        if not interfaces.IManifest.providedBy(base):
            raise ValueError('base must be manifest')
        if not source._z_frozen or not base._z_frozen:
            raise ValueError('manifests must be versioned')
        intids = self.vault.intids
        self._oldSelections.update(self._selections)
        self._oldOrphanResolutions.update(self._orphanResolutions)
        self._updateSource = source
        self._updateBase = base
        to_be_resolved = []
        for s in source:
            b = base.get(s.token)
            source_changed = (b is None or s.object is not b.object or 
                              s.containment != b.containment)
            l = self.get(s.token)
            if l is None: # even if base is non-None, that change is elsewhere
                local_changed = False
            elif b is None:
                local_changed = True
            else:
                local_changed = l is not b and (
                    l.object is not b.object or l.containment != b.containment)
            if source_changed:
                iid = intids.register(s)
                self._updated.insert(iid)
                self._index.index_doc(iid, s)
                if local_changed:
                    self._conflicts.insert(s.token)
                    if l is not s and (l.object is not s.object or
                                       l.containment != s.containment):
                        # material difference.  Give resolver a chance.
                        to_be_resolved.append((l, s, b))
                    else:
                        # we'll use the merged version by default
                        self.select(s)
                        self._resolutions.insert(s.token)
                else:
                    self.select(s)
        if to_be_resolved:
            resolver = interfaces.IConflictResolver(self.vault, None)
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
        token_to_source = dict((r.token, r) for r in source)
        if len(token_to_source) < len(source):
            raise ValueError(
                'cannot provide more than one update relationship for the '
                'same source')
        for rel in source:
            if rel.__parent__.vault.intids is not self.vault.intids:
                raise ValueError('sources must share intids')
            for child in rel.children:
                if (token_to_source.get(child) is None and 
                    self.get(child) is None):
                    raise ValueError(
                        'cannot update from a set that includes children '
                        'tokens without matching relationships in which the '
                        'child is the token')
        intids = self.vault.intids
        self._oldSelections.update(self._selections)
        self._oldOrphanResolutions.update(self._orphanResolutions)
        tmp_source = set()
        for rel in source:
            if not rel._z_frozen:
                if rel.__parent__ is not None and rel.__parent__ is not self:
                    rel = Relationship(rel.token, relationship=rel)
                    rel.__parent__ = self
                    event.notify(
                        zope.lifecycleevent.ObjectCreatedEvent(rel))
                self._add(rel, self._updated, force=True)
            else:
                iid = intids.register(rel)
                self._updated.insert(iid)
                self._locateObject(rel, force=True)
                self._index.index_doc(iid, rel)
            tmp_source.add(rel)
            local = self.getLocal(rel.token)
            if local is not None:
                self._conflicts.insert(rel.token)
                if (local.object is rel.object and 
                      local.containment == rel.containment):
                    self._resolutions.insert(rel.token)
                else:
                    resolver = component.queryMultiAdapter(
                        (local, rel, None), interfaces.IConflictResolver)
                    if resolver is not None:
                        resolver(self)
            else:
                self.select(rel)
        self._updateSource = frozenset(tmp_source)
        assert not self._getChildErrors()
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
        if (list(self.iterUpdateConflicts()) or
            list(self.iterParentConflicts()) or
            list(self.iterOrphanConflicts())):
            raise interfaces.UpdateError(
                'cannot complete update with conflicts')
        assert not self._getChildErrors(), 'children without relationships!'
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
            existing = IFBTree.multiunion(
                [data[0] for data in self._bases.values()])
            for i in selected:
                orig = rel = intids.getObject(i)
                if rel._z_frozen:
                    create_local = False
                    source_rel = source.get(rel.token)
                    if source_rel is rel:
                        create_local = True
                    elif source_rel is not None:
                        base_rel = base.get(rel.token)
                        if (base_rel is None or
                            source_rel._z_freeze_timestamp >
                            base_rel._z_freeze_timestamp):
                            create_local = True
                    if create_local:
                        rel = Relationship(
                            rel.token, relationship=rel, source_manifest=self)
                        rel.__parent__ = self
                        event.notify(
                            zope.lifecycleevent.ObjectCreatedEvent(rel))
                    else:
                        continue
                self._add(rel, self._local, True)
                event.notify(interfaces.LocalRelationshipAdded(rel))
                if orig is not rel:
                    self._selections.remove(i)
                    self.select(rel)
        else:
            self._indexBases(bases)
            existing = IFBTree.multiunion(
                [data[0] for data in self._bases.values()])
            for i in selected:
                if i not in existing:
                    rel = intids.getObject(i)
                    if rel._z_frozen:
                        rel = Relationship(
                            rel.token, relationship=rel, source_manifest=self)
                        rel.__parent__ = self
                        event.notify(
                            zope.lifecycleevent.ObjectCreatedEvent(rel))
                    self._add(rel, self._local, True)
                    event.notify(interfaces.LocalRelationshipAdded(rel))
        assert not (list(self.iterUpdateConflicts()) or
                    list(self.iterParentConflicts()) or
                    list(self.iterOrphanConflicts()) or
                    self._getChildErrors())
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
                b = base.get(rel.token)
                if (b is None or
                    b.object is not rel.object or
                    b.containment != rel.containment):
                    yield rel

    @zc.freeze.method
    def reindex(self, relationship):
        t = self.vault.intids.queryId(relationship)
        if t is not None and (t in self._local or t in self._suggested or
                              t in self._modified or t in self._updated):
            self._locateObject(relationship)
            self._index.index_doc(t, relationship)

    def _getFromSet(self, token, set, default):
        res = list(self._yieldFromSet(token, set))
        if not res:
            return default
        assert len(res) == 1, 'internal error: too many in the same category'
        return res[0]

    def _yieldFromSet(self, token, set):
        get = self.vault.intids.getObject
        for t in self._index.findRelationshipTokenSet({'token': token}):
            if t in set:
                yield get(t)

    def get(self, token, default=None):
        # return the selected relationship
        return self._getFromSet(token, self._selections, default)

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
                iid = intids.queryId(relationship.__parent__.vault)
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
            self._index.tokenizeQuery({'token': relationship.token}))
        for rel_t in rel_tokens:
            if rel_t in self._selections:
                self._selections.remove(rel_t)
                event.notify(interfaces.RelationshipDeselected(
                    self.vault.intids.getObject(rel_t), self))
                break
        self._selections.insert(t)
        event.notify(interfaces.RelationshipSelected(relationship, self))

    def getBase(self, token, default=None):
        vault = self.base_source
        for iiset, rel_set in self._bases.values():
            if rel_set is vault:
                return self._getFromSet(token, iiset, default)

    def getLocal(self, token, default=None):
        return self._getFromSet(token, self._local, default)

    def getUpdated(self, token, default=None):
        return self._getFromSet(token, self._updated, default)

    def iterSuggested(self, token):
        return self._yieldFromSet(token, self._suggested)

    def iterModified(self, token):
        return self._yieldFromSet(token, self._modified)

    def iterMerged(self, token):
        vault = self.vault
        seen = set()
        for iiset, rel_set in self._bases.values():
            if rel_set is not vault:
                for r in self._yieldFromSet(token, iiset):
                    if r not in seen:
                        yield r
                        seen.add(r)

    def _parents(self, token):
        return self._index.findRelationshipTokenSet({'child': token})

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

    def isLinked(self, token, child):
        return self._index.isLinked(
            self._index.tokenizeQuery({'token': token}),
            filter=self._selectionsFilter,
            targetQuery=self._index.tokenizeQuery({'child': child}))

    def iterUpdateConflicts(self):
        # any proposed (not accepted) relationship that has both update and
        # local for its token
        if self._updateSource is None:
            raise StopIteration
        get = self.vault.intids.getObject
        for t in self._conflicts:
            if t not in self._resolutions:
                rs = list(self._index.findRelationshipTokenSet({'token': t}))
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
        for t in self._resolutions:
            assert t in self._conflicts
            rs = list(self._index.findRelationshipTokenSet({'token': t}))
            for r in rs:
                if r in self._selections:
                    yield get(r)
                    break
            else:
                assert 0, (
                    'programmer error: no selected relationship found for '
                    'resolved token')

    def isUpdateConflict(self, token):
        return (token in self._conflicts and
                token not in self._resolutions)

    @zc.freeze.method
    def resolveUpdateConflict(self, token):
        if not self.updating:
            raise interfaces.UpdateError(
                'can only resolve merge conflicts during update')
        if token not in self._conflicts:
            raise ValueError('token does not have merge conflict')
        self._resolutions.insert(token)

    def _iterOrphans(self, condition):
        get = self.vault.intids.getObject
        res = set(self._selections)
        res.difference_update(self._iterLinked())
        bases = IFBTree.multiunion([d[0] for d in self._bases.values()])
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
        parents = set()
        children = set()
        for rid in self._iterLinked():
            parents.update(self._index.findValueTokenSet(rid, 'token'))
            children.update(self._index.findValueTokenSet(rid, 'child'))
        children.difference_update(parents)
        return children # these are token ids

    def iterAll(self): # XXX __iter__?
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

    def iterSelections(self): # XXX __iter__?
        get = self.vault.intids.getObject
        return (get(t) for t in self._selections)
            

    def __iter__(self): # XXX iterLinked?
        get = self.vault.intids.getObject
        return (get(t) for t in self._iterLinked())

    def iterUnchangedOrphans(self):
        get = self.vault.intids.getObject
        res = set(self._selections)
        res.difference_update(self._iterLinked())
        bases = IFBTree.multiunion([d[0] for d in self._bases.values()])
        res.intersection_update(bases)
        return (get(t) for t in res)

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

    def isOption(self, relationship): # XXX __contains__?
        for rel in self._index.findRelationships(
            self._index.tokenizeQuery(
                {'token': relationship.token, 'object': relationship.object})):
            if rel is relationship:
                return True
        return False
