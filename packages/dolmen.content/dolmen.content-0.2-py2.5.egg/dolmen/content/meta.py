# -*- coding: utf-8 -*-

import base
import martian
import warnings
import dolmen.content

import grokcore.security
import grokcore.component
from grokcore.formlib import formlib
from grokcore.component.scan import determine_module_component

from zope import component
from zope.formlib import form
from zope.interface import classImplements, verify, directlyProvides
from zope.schema.fieldproperty import FieldProperty
from zope.app.publisher.browser.icon import IconDirective


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
    martian.directive(dolmen.content.schema)
    martian.directive(dolmen.content.icon)
    martian.directive(dolmen.content.factory)
    martian.directive(grokcore.component.name)
    martian.directive(grokcore.security.require)


    def execute(self, class_, config, schema, icon,
                name, factory, require, **kw):

        formfields = form.FormFields(*schema)
        for formfield in formfields:
            fname = formfield.__name__
            if not hasattr(class_, fname):
                setattr(class_, fname, FieldProperty(formfield.field))

        for iface in schema:
            if not iface.providedBy(class_):
                classImplements(class_, iface)

        # icon providing
        specialized = formlib.most_specialized_interfaces(class_)
        IconDirective(config, 'contenttype_icon', specialized[0], file=icon)
        directlyProvides(class_, specialized[0])

        if getattr(class_, '__content_type__', None) is None:
            if not name:
                name = class_.__name__
                warnings.warn(
                    ("Content type not provided for '%s'. "
                     "Using %r instead. This prevents the "
                     "internationalization of the type name.") %
                    (class_, name), UserWarning, 2)
            class_.__content_type__ = name

        if dolmen.content.nofactory.bind().get(class_):
	    if factory:
	        warnings.warn(
		    ("Your Content type has an explicit Factory '%s'."
		     "At the same time you specified the *nofactory*"
		     "directive for your Content type '%s'.") %
		     (factory.__name__, class_.__name__), UserWarning, 2)
            return True

        elif factory is None:
            utility = dolmen.content.Factory(class_)
            verify.verifyObject(dolmen.content.IFactory, utility, tentative=0)
            factory_name = '%s.%s' % (class_.__module__, class_.__name__)

        else:
            factory_name = grokcore.component.name.bind().get(factory)
            if not factory_name:
                raise martian.error.GrokError(
                    "%r is used as a contenttype factory by %r. "
                    "However, the factory name was omitted. Please, "
                    "use the `name` directive to define a factory name."
                    % (factory, class_), factory
                    )
            utility = factory(class_)

        config.action(
            discriminator=('utility', dolmen.content.IFactory, factory_name),
            callable=component.provideUtility,
            args=(utility, dolmen.content.IFactory, factory_name),
            )
            
        return True
