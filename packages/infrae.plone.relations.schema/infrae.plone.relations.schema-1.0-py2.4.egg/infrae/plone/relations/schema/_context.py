# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: _context.py 29099 2008-06-11 07:54:54Z sylvain $

__author__ ="sylvain@infrae.com"
__format__ ="plaintext"
__version__ ="$Id: _context.py 29099 2008-06-11 07:54:54Z sylvain $"

from zope.interface import implements
from interfaces import IPloneRelationContextFactory, IPloneRelationContext

from OFS.SimpleItem import SimpleItem

from zExceptions import BadRequest

from Products.Archetypes.Referenceable import Referenceable


class BasePloneRelationContext(Referenceable, SimpleItem):
    """Sample context object, stored as a SimpleItem. Referenceable
    from archetype is used by widget."""

    implements(IPloneRelationContext)

    meta_type                   = ''

    def __init__(self, id):
        super(BasePloneRelationContext, self).__init__()
        self.id = id

        

class BasePloneRelationContextFactory(object):
    """Sample factory, storing the context object in the src object,
    which have to be folderish."""

    implements(IPloneRelationContextFactory)

    def __init__(self, klass, schema):
        self.klass = klass
        self.schema = schema

    def __call__(self, src, tgt, data):
        name = tgt.UID()
        context = self.klass(name)
        try:
            src._setObject(name, context)
        except BadRequest:
            context = getattr(src, name)
        for key, value in data.iteritems():
            field = self.schema.get(key)
            field.validate(value)
            field.set(context, value)
        return getattr(src, name)


