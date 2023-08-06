# -*- coding: utf-8 -*-

from dolmen.content.directives import schema
from dolmen.content.interfaces import IFactory
from zope.i18nmessageid import MessageFactory
from zope.schema.fieldproperty import FieldProperty
from zope.interface import implements, implementedBy

_ = MessageFactory("dolmen")


class Factory(object):
    implements(IFactory)

    addform = FieldProperty(IFactory['addform'])
    description = FieldProperty(IFactory['description'])

    def __init__(self, factory):
        self.factory = factory

    def getInterfaces(self):
        return implementedBy(self.factory)

    def getSchema(self):
        return schema.bind().get(self.factory)

    @property
    def title(self):
        return _(u"add_action", default=u"Add: ${name}",
                 mapping={'name': self.factory.__content_type__})

    def __call__(self, *args, **kw):
        return self.factory(*args, **kw)
