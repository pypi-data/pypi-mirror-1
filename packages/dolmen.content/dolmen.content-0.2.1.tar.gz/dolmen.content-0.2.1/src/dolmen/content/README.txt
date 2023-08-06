==============
dolmen.content
==============

The package `dolmen.content` is a convenient way to define content
types. Content types usually have several attributes : a type, a
schema, an icon. In addition, they need security to control the
creation, pages to edit them, easy ways to control the display, and
the widgets. This is what provides `dolmen.content`, with an
easy-to-use set of grok directives.

Example
=======

A `dolmen.content` content is declared as a simple class. Some
directives are available to define your content: `name`, `icon`,
`schema` and `factory`. To have detailed information about these
directives, please have a look at the package tests.

Defining the content
--------------------

Let's demonstrate the package's features with a simple and
non-exhaustive test::

  >>> import dolmen.content
  >>> from zope import schema

  >>> class IContentSchema(dolmen.content.IBaseContent):
  ...    text = schema.Text(title=u"A body text", default=u"N/A")

  >>> class MyContent(dolmen.content.Content):
  ...  """A very simple content
  ...  """
  ...  dolmen.content.schema(IContentSchema)
  ...  dolmen.content.name("a simple content type")


Grokking
--------

We now let Grok register our component::

  >>> import grok
  >>> grok.testing.grok_component('mycontent', MyContent)
  True


Factory
-------

When the content is registered, a factory is registered, using the
full module and class dotted names. It allows us to query and
instanciate the content easily::

  >>> from zope.component import getUtility
  >>> factory = getUtility(dolmen.content.IFactory,
  ...                      name="dolmen.content.MyContent")
  >>> factory
  <dolmen.content.factoring.Factory object at ...>


Schema
------

The content can now be instanciated. As we can see here, the object is
effectively providing the schema::

  >>> my_content = factory()

  >>> my_content.__content_type__
  'a simple content type'

  >>> IContentSchema.providedBy(my_content)
  True
  >>> my_content.text
  u'N/A'
