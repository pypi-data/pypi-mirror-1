==============
dolmen.storage
==============

`dolmen.storage` defines a clear high-level API to deal with pluggable
storage components.

Components
==========

Storage
-------

A storage is a component dedicated to store contents. It behaves like
a container and provides the interface `dolmen.storage.IStorage`.

Out of the box, two IStorage components are available, based on ZODB
BTrees::

  >>> from dolmen.storage import IStorage
  >>> from dolmen.storage import container
  >>> from zope.container.interfaces import IContainer

  >>> otree = container.OOBTreeStorage()
  >>> itree = container.IOBTreeStorage()

  >>> IStorage.extends(IContainer)
  True

  >>> from zope.interface import verify
  >>> verify.verifyObject(IStorage, otree)
  True
  >>> verify.verifyObject(IStorage, itree)
  True


Delegated storage
-----------------

A delegated storage is a component behaving like a Storage but
delegating all the container-level methods to a `storage`
attribute::

  >>> from dolmen.storage import IDelegatedStorage, DelegatedStorage
  
  >>> class MyStorage(DelegatedStorage):
  ...     def __init__(self):
  ...         self.storage = container.OOBTreeStorage()
  >>> container = MyStorage()

  >>> verify.verifyObject(IDelegatedStorage, container)
  True

  >>> container['manfred'] = 'mammoth'
  >>> 'manfred' in container
  True
  >>> 'manfred' in container.storage
  True

The `storage` attribute has to be a valid IStorage::

  >>> class FailingStorage(DelegatedStorage):
  ...     def __init__(self):
  ...         self.storage = list()
  >>> container = FailingStorage()
  Traceback (most recent call last):
  ...
  SchemaNotProvided


Annotations
===========

These storage components are used to provide a very flexible
annotation storage facility.

Annotation Storage
------------------

.. attention::

  This functionality is detailed in the package's tests. Please, read
  the tests for more information concerning the `AnnotationStorage`.

The annotation storage provides a way to delegate the storage in an
annotation container::

  >>> import grokcore.component as grok
  >>> from dolmen.storage import AnnotationStorage
  >>> from zope.annotation.interfaces import IAnnotations
  >>> from zope.annotation.interfaces import IAttributeAnnotatable

  >>> class Mammoth(object):
  ...    '''A furry creature
  ...    '''
  ...    grok.implements(IAttributeAnnotatable)

  >>> class NamedStorage(AnnotationStorage):
  ...    grok.name('some.name')

  >>> manfred = Mammoth()
  >>> named_storage = NamedStorage(manfred)
  >>> IDelegatedStorage.providedBy(named_storage)
  True

  >>> named_storage['test'] = 'This is a simple test'
  >>> list(named_storage.values())
  ['This is a simple test']

  >>> annotations = IAnnotations(manfred).get("some.name")
  >>> annotations == named_storage.storage
  True
  >>> annotations['test']
  'This is a simple test'


Annotation property
-------------------

.. attention::

  This functionality is detailed in the package's tests. Please, read
  the tests for more information concerning the `AnnotationProperty`.

The annotation property allows a direct access to an annotation
storage or value via a FieldProperty-like property::

  >>> from zope.schema import TextLine
  >>> from zope.interface import Interface
  >>> from dolmen.storage import AnnotationProperty
  
  >>> class WildMammoth(object):
  ...    '''A furry creature
  ...    '''
  ...    grok.implements(IAttributeAnnotatable)

  >>> class IRidingMount(Interface):
  ...    rider = TextLine(title=u'Name of the rider', default=None)
  
  >>> class MammothRiding(grok.Adapter):
  ...    rider = AnnotationProperty(IRidingMount['rider'])

  >>> wooly = WildMammoth()
  >>> annotator = MammothRiding(wooly)
  >>> annotator.rider = u'Grok'
  
  >>> IAnnotations(wooly).get("rider")
  u'Grok'
