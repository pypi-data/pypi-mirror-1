
Many to Many Relation Interface
===============================

This interface provides a more generic way to edit relations than the
one provided by ``plone.app.relations``, to let the Zope 3 schema work
in both way (normal access to the relation, and reverse access).

Create simple content::

  >>> from OFS.SimpleItem import SimpleItem
  >>> class BaseContent(SimpleItem):
  ...    def __init__(self, id):
  ...       super(BaseContent, self).__init__()
  ...       self.id = id
 

  >>> for num in range(1, 20):
  ...    id = 'it%02d' % num
  ...    it = BaseContent(id)
  ...    _ = self.portal._setObject(id, it)

  >>> self.portal.it01
  <BaseContent at /plone/it01>

Contents must be ``IPersistent``::

  >>> from persistent import IPersistent
  >>> from zope.interface.verify import verifyObject
  >>> verifyObject(IPersistent, self.portal.it01)
  True


Simple test of the interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We have a new adapter to work on your relation::

  >>> from infrae.plone.relations.schema import IManyToManyRelationship
  >>> manager = IManyToManyRelationship(self.portal.it01)
  >>> verifyObject(IManyToManyRelationship, manager)
  True

Ok, try to add relation::

  >>> rel = manager.createRelationship((self.portal.it11, self.portal.it12,),
  ...                                  sources=(self.portal.it02,),
  ...                                  relation='test')
  >>> list(rel.sources)
  [<BaseContent at /plone/it01>, <BaseContent at /plone/it02>]
  >>> list(rel.targets)
  [<BaseContent at /plone/it11>, <BaseContent at /plone/it12>]

Now, we can retrieve a list of relation::

  >>> list(manager.getRelationships())
  [<Relationship 'test' from (<BaseContent at /plone/it01>, <BaseContent at /plone/it02>) to (<BaseContent at /plone/it11>, <BaseContent at /plone/it12>)>]


Direction
~~~~~~~~~

You can reverse the way a relation works, with the ``setDirection``
method::

  >>> rel = manager.createRelationship(self.portal.it05, relation='reverse')
  >>> list(rel.targets)
  [<BaseContent at /plone/it05>]
  >>> manager.setDirection(False)
  >>> rel = manager.createRelationship(self.portal.it04, relation='reverse')
  >>> list(rel.targets)
  [<BaseContent at /plone/it01>]

You have also the transitivity for search::

  >>> manager = IManyToManyRelationship(self.portal.it04)
  >>> list(manager.getRelationshipChains(relation='reverse', 
  ...                                    target=self.portal.it05,
  ...                                    maxDepth=2))
  [(<Relationship 'reverse' from (<BaseContent at /plone/it04>,) to (<BaseContent at /plone/it01>,)>, <Relationship 'reverse' from (<BaseContent at /plone/it01>,) to (<BaseContent at /plone/it05>,)>)]

  
But relation are always followed from source to target. So if we
reverse the search, we won't found a result::

  >>> manager.setDirection(False)
  >>> list(manager.getRelationshipChains(relation='reverse', 
  ...                                    target=self.portal.it05,
  ...                                    maxDepth=2))
  []

Direction just change the meaning of source or target on the relation
object. It's doesn't change the relation itself.


Bigger example with transitivity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Taking back the first test, and add a suite::

  >>> manager = IManyToManyRelationship(self.portal.it16)
  >>> manager.setDirection(False)
  >>> rel = manager.createRelationship((self.portal.it12, self.portal.it14),
  ...                                  relation='test')
  >>> manager.setDirection(True)
  >>> rel = manager.createRelationship((self.portal.it17, self.portal.it18),
  ...                                  sources=(self.portal.it19,),
  ...                                  relation='test')

New chain try::

  >>> manager = IManyToManyRelationship(self.portal.it02)
  >>> list(manager.getRelationshipChains(relation='test',
  ...                                    target=self.portal.it18,
  ...                                    maxDepth=3))
  [(<Relationship 'test' from (<BaseContent at /plone/it01>, <BaseContent at /plone/it02>) to (<BaseContent at /plone/it11>, <BaseContent at /plone/it12>)>, <Relationship 'test' from (<BaseContent at /plone/it12>, <BaseContent at /plone/it14>) to (<BaseContent at /plone/it16>,)>, <Relationship 'test' from (<BaseContent at /plone/it16>, <BaseContent at /plone/it19>) to (<BaseContent at /plone/it17>, <BaseContent at /plone/it18>)>)]


Accessor
~~~~~~~~

``getTargets`` returns a lazy list of objects having a relation with
the given object as source, and ``getSources`` returns a lazy list of
objects having a relation with the given object as target::

  >>> manager = IManyToManyRelationship(self.portal.it16)
  >>> list(manager.getTargets())
  [<BaseContent at /plone/it17>, <BaseContent at /plone/it18>]
  >>> list(manager.getSources())
  [<BaseContent at /plone/it12>, <BaseContent at /plone/it14>]

If we reverse the direction::

  >>> manager.setDirection(False)
  >>> list(manager.getTargets())
  [<BaseContent at /plone/it12>, <BaseContent at /plone/it14>]
  >>> list(manager.getSources())
  [<BaseContent at /plone/it17>, <BaseContent at /plone/it18>]


Deletion
~~~~~~~~

Delete relation::

   >>> manager.setDirection(True)
   >>> manager.deleteRelationship()
   >>> list(manager.getRelationships())
   []

   >>> manager = IManyToManyRelationship(self.portal.it19)
   >>> list(manager.getRelationships())
   [<Relationship 'test' from (<BaseContent at /plone/it19>,) to (<BaseContent at /plone/it17>, <BaseContent at /plone/it18>)>]

   >>> manager.deleteRelationship(target=self.portal.it17)
   >>> list(manager.getRelationships())
   [<Relationship 'test' from (<BaseContent at /plone/it19>,) to (<BaseContent at /plone/it18>,)>]

   >>> manager.deleteRelationship()
   >>> list(manager.getRelationships())
   []

   >>> manager = IManyToManyRelationship(self.portal.it01)
   >>> manager.deleteRelationship(remove_all_sources=True, multiple=True)
   >>> manager = IManyToManyRelationship(self.portal.it02)
   >>> list(manager.getRelationships())
   []


