"""
Grokking the provided code will get us started.

  >>> testing.grok(__name__)

IStorageHandler provides an easy way to store items in annotations.
The first step is simple to instanciate a common persistent object.
Adapting it to IStorageHandler provides some convenient methods to
store, retrieve and delete annotation items.

  >>> item = ContentType()
  >>> item.id = 'item'
  >>> handler = IStorageHandler(item)
  >>> handler is not None
  True
  >>> IStorageHandler.providedBy(handler)
  True
  >>> IStorage.providedBy(handler.storage)
  True

As we can see, getting an annotation container is a matter of an adaptation.
Then, we can verify if the container has been effectively created.

  >>> from zope.annotation.interfaces import IAnnotations
  >>> annoted = IAnnotations(item)
  >>> 'troll.storage.tests' in annoted
  True
  >>> IStorage.providedBy(annoted['troll.storage.tests'])
  True
  >>> handler.storage is annoted['troll.storage.tests']
  True
  >>> len(annoted['troll.storage.tests'])
  0

Now, let's store and item in the annotation container. Storage and retrieval
are very straightforward.

  >>> foo = StoredItem('bar')
  >>> handler.store(foo)
  True
  >>> len(handler.storage)
  1
  >>> obj = handler.retrieve('bar')
  >>> isinstance(obj, StoredItem)
  True
  >>> obj.aq_parent is item
  True

Storage is non-destructive. If the entry already exists, it's not overriden.
Delete can be used to handle the destruction of the stored items.

  >>> usurper = StoredItem('bar')
  >>> handler.store(usurper)
  False
  >>> handler.delete('bar')
  True
  >>> handler.delete('bar')
  False
  >>> len(handler.storage)
  0
  >>> handler.store(usurper)
  True

Errors are raised if something went *very* wrong. Most of the classical errors
are already caught : non existing object on retrieval or deletion, etc.
Still, if you don't respect the storage integrity policy, you get troubles.

  >>> rogue = SimpleItem()
  >>> rogue.name = 'sneaky'
  >>> handler.store(rogue)
  Traceback (most recent call last):
        ...
  InvalidItemType: Trying to store a non IStorageItem object.
  >>> from zope.interface import directlyProvides
  >>> directlyProvides(rogue, IStorageItem)
  >>> handler.store(rogue)
  True

IStoredItem objects can be published. You can register views for them,
it works perfectly.

  >>> from zope.publisher.browser import TestRequest
  >>> from zope.component import getMultiAdapter
  >>> publishable = handler.retrieve('sneaky')
  >>> view = getMultiAdapter((publishable, TestRequest()), name='simple_view')
  >>> view.update()
  >>> view.render()
  '<h1>My name is sneaky and my parent is item</h1>'

"""

from five import grok
import five.grok.testing as testing
from Acquisition import Explicit
from OFS.SimpleItem import SimpleItem
from zope.interface import implements
from troll.storage.base import BaseStorageHandler
from troll.storage.descriptors import AnnotationContainerProperty
from troll.storage.interfaces import IStorageHandler, IStorage, IStorageItem
from zope.annotation.interfaces import IAttributeAnnotatable


class ContentType(SimpleItem):
    implements(IAttributeAnnotatable)


class StoredItem(Explicit):
    implements(IStorageItem)

    def __init__(self, name):
        self.name = name
        

class BaseStorageHandler(BaseStorageHandler):
    grok.context(ContentType)

    storage = AnnotationContainerProperty(
        IStorageHandler['storage'],
        ns='troll.storage.tests'
        )


class StoredItemView(grok.View):
    grok.name('simple_view')
    grok.context(IStorageItem)

    def render(self):
        return '<h1>My name is %s and my parent is %s</h1>' % (
            self.context.name, self.context.aq_inner.aq_parent.id
            )
