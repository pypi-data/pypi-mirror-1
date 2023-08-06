# -*- coding: utf-8 -*-

import grok
import interfaces as base
import directives as config
from zope.dublincore.property import DCProperty


class BaseContent(grok.Model):
    config.icon('generic.png')
    config.schema(base.IBaseContent)
    grok.baseclass()

    title = DCProperty('title')

    
class Container(BaseContent, grok.Container):
    """A dolmen folderish content type.
    """
    grok.baseclass()
    grok.implements(base.IContainer)


class OrderedContainer(BaseContent, grok.OrderedContainer):
    """A dolmen folderish content type with ordered keys.
    """
    grok.baseclass()
    grok.implements(base.IOrderedContainer)


class Content(BaseContent):
    """A dolmen content type.
    """
    grok.baseclass()
    grok.implements(base.IContent)
