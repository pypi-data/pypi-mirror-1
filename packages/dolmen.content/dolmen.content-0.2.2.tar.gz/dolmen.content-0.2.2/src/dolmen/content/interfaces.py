# -*- coding: utf-8 -*-

import zope.component.interfaces
from dolmen.field import GlobalClass
from zope.schema import TextLine
from zope.interface import Interface, Attribute
from zope.annotation.interfaces import IAttributeAnnotatable


class IBaseContent(IAttributeAnnotatable):
    """Marker interface for dolmen base content.
    """
    title = TextLine(
        title = u"Title",
        required = True
        )
    
    __content_type__ = Attribute(
        """Type of the object. Usually set by the grokker, using the
        grok.name directive."""
        )


class IContent(IBaseContent):
    """Marker interface for contentish dolmen objects.
    """


class IContainer(IBaseContent):
    """Marker interface for folderish dolmen objects.
    """

class IOrderedContainer(IContainer):
    """Marker interface for folderish dolmen objects with ordered keys.
    """


class IFactory(zope.component.interfaces.IFactory):
    """A factory for a dolmen content type.
    """
    factory = GlobalClass(
        required = True,
        title = u"Class used as a factory",
        schema = IBaseContent
        )

    addform = TextLine(
        required = True,
        title = u"Name of the add form",
        default = u"dolmen.add"
        )

    description = TextLine(
        required = True,
        title = u"Description of the added content",
        default = u""
        )

    def getSchema():
        """Returns a list of interfaces representing the schema
        of the factored item. The returned interfaces must be provided
        by the instance of the object issued from the factory.
        """

__all__ = (
    'IBaseContent', 'IContent',
    'IContainer', 'IOrderedContainer', 'IFactory'
    )
