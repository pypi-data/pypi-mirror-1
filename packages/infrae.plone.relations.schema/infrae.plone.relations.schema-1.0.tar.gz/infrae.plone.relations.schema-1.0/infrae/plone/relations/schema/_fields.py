# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: _fields.py 29100 2008-06-11 08:04:50Z sylvain $

__author__ ="sylvain@infrae.com"
__format__ ="plaintext"
__version__ ="$Id: _fields.py 29100 2008-06-11 08:04:50Z sylvain $"

from zope.interface import implements
from zope.schema import Field, getFieldNamesInOrder, ValidationError
from zope.schema.interfaces import TooSmall, TooBig

from plone.app.relations.interfaces import IRelationshipSource, IRelationshipTarget
from plone.app.relations.interfaces import IAnnotationsContext, NoResultsError
from plone.relations.interfaces import IContextAwareRelationship
try:
    from zope.app.annotation.interfaces import IAttributeAnnotatable
except ImportError:
    from zope.annotation.interfaces import IAttributeAnnotatable
    
from interfaces import IPloneRelation, IManyToManyRelationship


class PloneRelation(Field):
    implements(IPloneRelation)


    def __init__(self, relation=u'',
                 reverse=False,
                 relation_schema=None,
                 context_schema=None,
                 min_length=0,
                 max_length=0,
                 unique=False,
                 **kwargs):
        super(PloneRelation, self).__init__(**kwargs)
        self.relation = relation
        self.reverse = reverse
        self.relation_schema = relation_schema
        self.context_schema = context_schema
        self.min_length = min_length
        self.max_length = max_length
        self.unique = unique


    def _validate(self, values):
        """Validate data format for set/get."""
        if not isinstance(values, list):
            raise ValidationError("Invalid structure")
        
        for value in values:
            if not isinstance(value, dict):
                raise ValidationError("Invalid structure")
            if not value.has_key('objects') or not value['objects']:
                raise ValidationError("Invalid structure")

            # Check the objects.
            objs = value['objects']
            if self.unique and len(objs) != 1:
                raise ValidationError("Not uniques values in relation")
            if self.relation_schema:
                for obj in objs:
                    if not self.relation_schema.providedBy(obj):
                        raise ValidationError("Not valide type for content object")

            # Check the context.
            if value.has_key('context'):
                ctxt = value['context']
                if (not ctxt or not self.context_schema.providedBy(ctxt)):
                    raise ValidationError("Invalid context")

        # Check the len of the field.
        if self.min_length or self.max_length:
            len_obj = len(values)
            if len_obj < self.min_length:
                raise TooSmall("Less than %d values" % self.min_length)
            if len_obj > self.max_length:
                raise TooBig("More than %d values" % self.max_length)


    def set(self, context, values):
        """Set new relations on the object."""

        robj = IManyToManyRelationship(context)
        robj.setDirection(not self.reverse)

        # First, delete current relations.
        try:
            robj.deleteRelationship(relation=self.relation,
                                    source=context,
                                    multiple=True)
        except NoResultsError:
            pass                        # There is no relationship to delete.

        # Second, create new ones.
        for value in values:
            interfaces = ()
            if not (self.context_schema is None):
                interfaces = (IAttributeAnnotatable, IAnnotationsContext,)
            relation = robj.createRelationship(value['objects'],
                                               relation=self.relation,
                                               interfaces=interfaces)
            if value.has_key('context'):
                # FIXME: We have to register an event to eventually delete the context object
                # on the deletion of the relation.
                rcontext = IContextAwareRelationship(relation)
                rcontext.setContext(value['context'])



    def get(self, context):
        """Return current relations to the object."""
        
        robj = IManyToManyRelationship(context)
        robj.setDirection(not self.reverse)

        values = list()
        for relation in robj.getRelationships(relation=self.relation):
            if self.reverse:
                dobj = relation.sources
            else:
                dobj = relation.targets
            data = dict()
            data['objects'] = dobj
            if not (self.context_schema is None):
                context = IContextAwareRelationship(relation).getContext()
                data['context'] = context
            values.append(data)
        return values


    def query(self, context, default=None):
        return self.get(context) or default
                                   
