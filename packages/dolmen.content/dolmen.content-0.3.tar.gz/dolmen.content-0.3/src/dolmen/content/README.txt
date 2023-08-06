==============
dolmen.content
==============

The package `dolmen.content` is a convenient way to define content
types.

.. contents::

About
=====

Content types usually have several attributes defined in a
schema and a name. In addition, they often need security to control the
creation or the modification (update, deletion, etc.). This is what
provides `dolmen.content`, with an easy-to-use set of grok directives.

Example
=======

A `dolmen.content` content is declared as a simple class. Some
directives are available to define your content: `name`, `schema` and
`factory`. To have detailed information about these directives, please
have a look at the package tests.


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


Schema
------

The content can now be instanciated. As we can see here, the object is
effectively providing the schema, even without grokking::

  >>> MyContent.text
  <zope.schema.fieldproperty.FieldProperty object at ...>

  >>> IContentSchema.implementedBy(MyContent)
  True

  >>> obj = MyContent()
  >>> obj.text
  u'N/A'

The content can also be instanciated providing initial values::

  >>> obj = MyContent(text=u"This is a nice text !")
  >>> obj.text
  u'This is a nice text !'

Even though the schema has been applied and the content type
boostrapped, the content type is not yet complete::

  >>> obj.__content_type__
  Traceback (most recent call last):
  ...
  AttributeError: 'MyContent' object has no attribute '__content_type__'

To get all the features of a `dolmen.content` Content, we need to
register our component : we need to grok it.


Grokking
--------

We register our component::

  >>> from grokcore.component import testing
  >>> testing.grok_component('mycontent', MyContent)
  True

An additional information is now available::

  >>> obj.__content_type__
  'a simple content type'

The grokking process also allowed an automatic registration of a very
convenient factory as an utility.


Factory
-------

When the content is grokked, a factory is registered, using the
full module and class dotted names. It allows us to query and
instanciate the content easily::

  >>> from zope.component import getUtility
  >>> factory = getUtility(dolmen.content.IFactory,
  ...                      name="dolmen.content.MyContent")
  >>> factory
  <dolmen.content.factoring.Factory object at ...>

The factory will create your content type for you, when called::

  >>> obj = factory()
  >>> obj
  <dolmen.content.MyContent object at ...>
  >>> obj.text
  u'N/A'

  >>> obj = factory(text=u"This is as easy as it seems.")
  >>> obj
  <dolmen.content.MyContent object at ...>
  >>> obj.text
  u'This is as easy as it seems.'

Security
--------

The created content type has a basic security declaration. We can
retrieve the value of the permission protecting the content type by
using the `require` directive::

  >>> dolmen.content.require.bind().get(obj)
  'zope.ManageContent'

Please note that this security declaration is _not_ used anywhere in
`dolmen.content`. It's provided as a convenient way to declare a
permission at the content type level. The factory does not check this
permission. If you need a permission checker at the factory level,
please provide your own factory : see the tests module, factory
folder, for examples.
