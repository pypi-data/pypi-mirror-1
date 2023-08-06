"""
Custom factories
================

  >>> from zope.component import getUtility, queryUtility
  >>> joe = getUtility(dolmen.IFactory, 'baker_joe')
  >>> isinstance(joe, BakerJoe)
  True

  >>> steve = queryUtility(dolmen.IFactory, 'baker_steve')
  >>> steve is None
  True

"""

import dolmen.content as dolmen
from zope.interface import Interface, implements


class IBread(Interface):
    pass


class BakerJoe(dolmen.Factory):
    dolmen.name('baker_joe')
    title = u"Joe's bakery"


class BakerSteve(dolmen.Factory):
    dolmen.name('baker_steve')
    title = u"Steve and Sons."

    
class Baguette(dolmen.Content):
    """A crusty bread.
    """
    dolmen.name(u'White fresh bread')
    dolmen.factory(BakerJoe)
    implements(IBread)
