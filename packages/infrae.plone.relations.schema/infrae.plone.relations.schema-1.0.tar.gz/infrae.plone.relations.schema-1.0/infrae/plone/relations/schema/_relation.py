# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: _relation.py 29099 2008-06-11 07:54:54Z sylvain $

__author__ ="sylvain@infrae.com"
__format__ ="plaintext"
__version__ ="$Id: _relation.py 29099 2008-06-11 07:54:54Z sylvain $"

from interfaces import IManyToManyRelationship

from plone.relations.interfaces import IComplexRelationshipContainer, _marker
from plone.relations.relationships import Z2Relationship
from plone.relations.lazylist import lazyresolver
from plone.app.relations import interfaces as pa_interfaces
from zope.component import adapts, getUtility
from zope.interface import implements, alsoProvides
from persistent import IPersistent


class ManyToManyRelationship(object):
    implements(IManyToManyRelationship)
    adapts(IPersistent)
    _name = 'relations'

    def __init__(self, context):
        self.context = context
        self.util = getUtility(IComplexRelationshipContainer, name=self._name,
                               context=context)
        self._resolver = self.util.relationIndex.resolveValueTokens
        self.setDirection(True)



    def setDirection(self, direction):
        self._direction = direction
        if direction:
            self._findSourceTokens = self.util.findSourceTokens
            self._findTargetTokens = self.util.findTargetTokens
        else:
            self._findSourceTokens = self.util.findTargetTokens
            self._findTargetTokens = self.util.findSourceTokens
            

    def _initializeDirectionList(self, target, others=None):
        if others:
            if isinstance(others, (list, tuple)):
                local = tuple(others)
            else:
                local = (others, )
            if not self.context in local:
                local = (self.context, ) + local
        else:
            local = (self.context,)
        self._initializeDirection(target, local)
        

    def _initializeDirection(self, target, local=None):
        if not local:
            local = self.context
        if self._direction:
            self._sources = local
            self._targets = target
        else:
            self._sources = target
            self._targets = local
            

    def createRelationship(self, targets, sources=None, relation=None,
                           interfaces=(), rel_factory=None,
                           default_deletion=True):
        
        if rel_factory is None:
            rel_factory = Z2Relationship
            
        if not isinstance(targets, (list, tuple)):
            targets = (targets,)

        self._initializeDirectionList(targets, sources)
            
        rel = rel_factory(self._sources, self._targets, relation=relation)
        alsoProvides(rel, *interfaces)
        if default_deletion:
            alsoProvides(rel, pa_interfaces.IDefaultDeletion)
        self.util.add(rel)
        return self.util[rel.__name__]



    def getRelationshipChains(self, target=None, source=None,
                               relation=_marker, state=_marker,
                               context=_marker, rel_filter=None,
                               maxDepth=1, minDepth=None,
                               transitivity=None):

        self._initializeDirection(target, source)
        
        return self.util.findRelationships(self._sources, self._targets, relation,
                                           state, context, maxDepth=maxDepth,
                                           minDepth=minDepth,
                                           filter=rel_filter,
                                           transitivity=transitivity)
    

    def getRelationships(self, target=None, source=None,
                         relation=_marker, state=_marker,
                         context=_marker, rel_filter=None):


        
        rels = self.getRelationshipChains(target, source, relation,
                                          state, context, rel_filter)
        for chain in rels:
            yield chain[0]


    def _source_resolver(self, r_value):
        r_type = 'source'
        if self._findTargetTokens != self.util.findTargetTokens:
            r_type = 'target'
        return self._resolver((r_value,), r_type).next()


    @lazyresolver(resolver_name='_source_resolver')
    def getTargets(self, relation=_marker, state=_marker, context=_marker,
                    rel_filter=None, maxDepth=1, minDepth=None,
                    transitivity=None):

        return self._findTargetTokens(self.context, relation, state,
                                      context, maxDepth=maxDepth,
                                      minDepth=minDepth,
                                      filter=rel_filter,
                                      transitivity=transitivity)


    def _target_resolver(self, r_value):
        r_type = 'target'
        if self._findSourceTokens != self.util.findSourceTokens:
            r_type = 'source'
        return self._resolver((r_value,), r_type).next()


    @lazyresolver(resolver_name='_target_resolver')
    def getSources(self, relation=_marker, state=_marker, context=_marker,
                    rel_filter=None, maxDepth=1, minDepth=None,
                    transitivity=None):

        return self._findSourceTokens(self.context, relation, state,
                                       context, maxDepth=maxDepth,
                                       minDepth=minDepth,
                                       filter=rel_filter,
                                       transitivity=transitivity)


    def deleteRelationship(self, target=None, source=None,
                           relation=_marker, state=_marker,
                           context=_marker, rel_filter=None,
                           multiple=False, remove_all_targets=False,
                           ignore_missing=False,
                           remove_all_sources=False):
        
        if target is None:
            remove_all_targets = True
            
        rels = self.getRelationships(target=target, source=source,
                                     relation=relation, state=state,
                                     context=context,
                                     rel_filter=rel_filter)
        
        rels = list(rels)
        if not rels and not ignore_missing:
            raise pa_interfaces.NoResultsError
        if len(rels) > 1 and not multiple:
            raise pa_interfaces.TooManyResultsError
        for rel in rels:
            if self._targets is not None:
                assert(self._targets in rel.targets)
            if self._sources is not None:
                assert(self._sources in rel.sources)

            if len(rel.sources) > 1:
                if remove_all_sources or self._sources is None:
                    self.util.remove(rel)                    
                elif remove_all_targets or len(rel.targets) == 1:
                    rel.sources.remove(self._sources)
                    self.util.reindex(rel)
                else:
                    raise pa_interfaces.TooManyResultsError, "One of the "\
                          "relationships to be deleted has multiple sources "\
                          "and targets."

            elif len(rel.targets) > 1:
                if remove_all_targets or self._targets is None:
                    self.util.remove(rel)
                else:
                    rel.targets.remove(self._targets)
                    self.util.reindex(rel)
            else:
                self.util.remove(rel)


  
