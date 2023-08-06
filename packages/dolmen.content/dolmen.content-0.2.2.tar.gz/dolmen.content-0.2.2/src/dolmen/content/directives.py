# -*- coding: utf-8 -*-

import os.path
import martian
from sys import modules
from interfaces import IFactory
from martian.directive import StoreOnce
from zope.interface import Interface, verify


class FileValueStoreOnce(StoreOnce):

    def set(self, locals_, directive, value):

        if not os.path.isfile(value):
            pyfile = modules[locals_['__module__']].__file__
            value = os.path.join(os.path.dirname(pyfile), value)
            if not os.path.isfile(value):
                raise martian.error.GrokImportError(
                    "Directive %r cannot resolve the file %r." %
                    (directive.name, value)
                    )
        StoreOnce.set(self, locals_, directive, value)


FILE_PATH_ONCE = FileValueStoreOnce()


def validateSchema(directive, *ifaces):
    for iface in ifaces:
        if not iface.isOrExtends(Interface):
            raise martian.error.GrokImportError(
                "%s directive can only use interface classes. "
                "%s is not an interface class. " % (directive.name, iface)
                )


def verifyFactory(directive, factory):
    if factory and not IFactory.implementedBy(factory):
        raise martian.error.GrokImportError(
            "%s directive can only use classes that implement IFactory. "
            "%s is not a valid factory. " % (directive.name, factory)
            )


class schema(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    validate = validateSchema

    def factory(self, *schemas):
        return list(schemas)


class icon(martian.Directive):
    scope = martian.CLASS
    store = FILE_PATH_ONCE
    validate = martian.validateText


class factory(martian.Directive):
    scope = martian.CLASS_OR_MODULE
    store = martian.ONCE
    validate = verifyFactory


class nofactory(martian.MarkerDirective):
    scope = martian.CLASS
    store = martian.ONCE_NOBASE
