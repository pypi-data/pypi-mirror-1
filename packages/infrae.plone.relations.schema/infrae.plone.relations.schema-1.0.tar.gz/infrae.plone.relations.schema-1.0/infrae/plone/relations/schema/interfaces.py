# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: interfaces.py 29100 2008-06-11 08:04:50Z sylvain $

__author__ ="sylvain@infrae.com"
__format__ ="plaintext"
__version__ ="$Id: interfaces.py 29100 2008-06-11 08:04:50Z sylvain $"


from zope.interface import Interface
from zope.schema.interfaces import IField, IMinMaxLen
from zope.schema import TextLine, Bool, InterfaceField

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("plone")



class IPloneRelation(IField, IMinMaxLen):
    """Used to administrate a plone.app.relation
       on an object.
    """

    relation = TextLine(title=_(u"Relation name"),
                        description=_(u"The relation name used."),
                        required=True)

    reverse = Bool(title=_(u"Direction of relation"),
                   description=_(u"If true, the relation is a source one, otherwiser a target"),
                   required=True)

    context_schema = InterfaceField(title=_(u"Interface that should implement the context object"),
                                    required=False)

    relation_schema = InterfaceField(title=_(u"Relation items must implements this interface"),
                                     required=False)

    unique = Bool(title=_(u"Relation items have to be alone in a relation"),
                  required=False)




class IPloneRelationContextFactory(Interface):
    """Factory used to create a new context object.
    """

    def __call__(src, tgt, data):
        """
           - src: source of the relation,
           - tgt: target of the relation,
           - data: dictionnary with the parameters of the context.
        """


class IPloneRelationContext(Interface):
    """Base content type for plone relation context object.
    """

    meta_type = TextLine(title=_(u"Zope2 meta type."))

    def __init__(id):
        """Constructor, using id as object id.
        """


class IManyToManyRelationship(Interface):
    """An complex relation manager. You can administrate many to many
       relation, in the both direction.
    """

        
    def createRelationship(targets, sources, interfaces,
                           default_deletion):
        """Create relation.
        """


    def deleteRelationship(target, source, relation, state, context,
                           rel_filter, multiple, remove_all_target,
                           ignore_missing, remove_all_sources):
        """Delete relation.
        """

    def getRelationships(target, source, relation, state, context,
                         rel_filter):
        """Return a list of relations.
        """

    def getRelationshipChains(target, source, relation, state, context,
                              rel_filter, maxDepth, minDepth,
                              transitivity):
        """Return all the relation link.
        """


    def getSources(relation, state, context, maxDepth, minDepth,
                   transivity):
        """Return the sources of the relation.
        """

    def getTargets(relation, state, context, maxDepth, minDepth,
                   transitivity):
        """Return the targets of relation.
        """


    def setDirection(direction):
        """Set the direction of the relation. True for normal use,
           False for reverse.
        """

