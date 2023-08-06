# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from container import GenericStorage
from interfaces import IStorageItem
from zope.annotation.interfaces import IAnnotations

_marker = object()

class AnnotationContainerProperty(object):
    """Handles a container written in annotations.
    """
    def __init__(self, field, ns=u"troll.storage", name=None):
        self._name = name or field.__name__
        self._namespace = ns
        self.__field = field


    def __get__(self, inst, klass):
        field = self.__field.bind(inst)
        annotations = IAnnotations(aq_inner(inst.context))
        own_storage = annotations.get(self._namespace, _marker)
        if own_storage is _marker:
            own_storage = annotations[self._namespace] = GenericStorage()
        return own_storage
        

    def __set__(self, inst, value):
        field = self.__field.bind(inst)
        if field.readonly:
            raise ValueError(self._name, 'field is readonly')
        annotations = IAnnotations(aq_inner(inst.context))
        annotations[self._namespace] = value


    def __getattr__(self, name):
        return getattr(self.__field, name)
