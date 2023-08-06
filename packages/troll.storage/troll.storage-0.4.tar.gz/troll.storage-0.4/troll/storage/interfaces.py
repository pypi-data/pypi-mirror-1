# -*- coding: utf-8 -*-

from zope.schema import TextLine, Object
from zope.interface import Interface, Attribute
from zope.app.container.interfaces import IContainer
from zope.app.container.constraints import containers, contains   


class IStorageItem(Interface):
    """An item that can be stored in an IStorage.
    """    
    name = TextLine(
        title = u"name",
        default = u"",
        required = True
        )

    
class IStorage(IContainer):
    """Marker interface for useable containers.
    An IStorage can only contain a IStorageItem
    """
    contains(IStorageItem)
    

class IStorageHandler(Interface):
    """A storage item handles the persistence of a given item.
    A storage has three main actions : store, retrieve, delete.
    """
    storage = Object(
        title = u"Container",
        description = u"Contains IStorageItem items.",
        schema = IStorage,
        required = True,
        readonly = False
        )

    def store(self, obj):
        """Stores an object and returns True.
        Returns False is the object can't be stored.
        """

    def retrieve(self, key):
        """Retrieve the object according to the given key.
        The retrieving method depends of the storage type.
        If no object is found, None is returned.
        """

    def delete(self, key):
        """Deletes the object with the given oid.
        Returns True if success, False otherwise.
        """
