# -*- coding: utf-8 -*-

import martian
import warnings
import dolmen.content
import grokcore.security
import grokcore.component

from grokcore.component.scan import determine_module_component
from zope.component import provideUtility
from zope.interface import verify


class FactoryGrokker(martian.GlobalGrokker):
    """Grokker dedicated to find the factory within a module.
    """
    martian.priority(1002)

    def grok(self, name, module, module_info, config, **kw):
        context = determine_module_component(module_info,
                                             dolmen.content.factory,
                                             dolmen.content.IFactory)
        dolmen.content.factory.set(module, context)
        return True


class ContentTypeGrokker(martian.ClassGrokker):
    martian.component(dolmen.content.BaseContent)
    martian.directive(dolmen.content.factory)
    martian.directive(grokcore.component.name)
    martian.directive(grokcore.security.require)

    def grok(self, name, content, module_info, **kw):
        content.module_info = module_info
        return martian.ClassGrokker.grok(
            self, name, content, module_info, **kw)

    def execute(self, content, config, name, factory, require, **kw):
        if getattr(content, '__content_type__', None) is None:
            if not name:
                name = content.__name__
                warnings.warn(
                    ("Content type not provided for '%s'. "
                     "Using %r instead. This prevents the "
                     "internationalization of the type name.") %
                    (content, name), UserWarning, 2)
            content.__content_type__ = name

        if dolmen.content.nofactory.bind().get(content):
            if factory:
                warnings.warn(
                    ("Your Content type has an explicit Factory '%s'."
                     " At the same time you specified the *nofactory*"
                     " directive for your Content type '%s'. The"
                     " factory will be ignored.") %
                     (factory.__name__, content.__name__), UserWarning, 2)
            return True

        elif factory is None:
            utility = dolmen.content.Factory(content)
            verify.verifyObject(dolmen.content.IFactory, utility, tentative=0)
            factory_name = '%s.%s' % (content.__module__, content.__name__)

        else:
            factory_name = grokcore.component.name.bind().get(factory)
            if not factory_name:
                raise martian.error.GrokError(
                    "%r is used as a contenttype factory by %r. "
                    "However, the factory name was omitted. Please, "
                    "use the `name` directive to define a factory name."
                    % (factory, content), factory)
            utility = factory(content)

        config.action(
            discriminator=('utility', dolmen.content.IFactory, factory_name),
            callable=provideUtility,
            args=(utility, dolmen.content.IFactory, factory_name),
            )

        return True
