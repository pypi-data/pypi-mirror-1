# -*- coding: utf-8 -*-

from five import grok
from descriptors import AnnotationContainerProperty
from interfaces import IStorageHandler, IStorageItem
from zope.app.container.interfaces import InvalidItemType


class BaseStorageHandler(grok.Adapter):
    """A very generic storage system
    It will store the items in a dictionnary-ish container.
    Therefore, keys are unique and can be of any hashable type.
    """
    grok.implements(IStorageHandler)
    grok.baseclass()

    @property
    def storage(self):
        return NotImplementedError(
            "Your storage handler has to provide its own storage."
            )

    def store(self, obj):
        if not IStorageItem.providedBy(obj):
            raise InvalidItemType(
                "Trying to store a non IStorageItem object."
                )
        key = obj.name
        if key not in self.storage.keys():
            try:
                self.storage[key] = obj
                return True
            except InvalidItemType:
                return False
        return False

    def retrieve(self, key):
        item = self.storage.get(key, None)
        if item is None:
            return None
        return self.storage[key].__of__(self.context)
            
    def delete(self, key):
        if key not in self.storage.keys():
            return False
        del self.storage[key]
        return True
        
    def __getattr__(self, name):
        return self.retrieve(name)
