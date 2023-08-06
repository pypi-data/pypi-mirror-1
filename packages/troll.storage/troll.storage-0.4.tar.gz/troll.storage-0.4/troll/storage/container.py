# -*- coding: utf-8 -*-

from interfaces import IStorage
from zope.interface import implements
from zope.app.container.btree import BTreeContainer


class GenericStorage(BTreeContainer):
    """A Generic BTree Container that implements IStorage.
    """
    implements(IStorage)
    
