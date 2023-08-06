##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Grok directives.
"""

import sys
import grok
from zope import interface
from zope.interface.interfaces import IInterface
from zope.publisher.interfaces.browser import IBrowserView

import martian
from martian import util
from martian.error import GrokImportError, GrokError
from martian.directive import StoreMultipleTimes
from grokcore.component.scan import UnambiguousComponentScope
from grok import components

# Define grok directives
class template(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    validate = martian.validateText

class templatedir(martian.Directive):
    scope = martian.MODULE
    store = martian.ONCE
    validate = martian.validateText

class local_utility(martian.Directive):
    scope = martian.CLASS
    store = martian.DICT

    def factory(self, factory, provides=None, name=u'',
                setup=None, public=False, name_in_container=None):
        if provides is not None and not IInterface.providedBy(provides):
            raise GrokImportError("You can only pass an interface to the "
                                  "provides argument of %s." % self.name)

        if provides is None:
            provides = grok.provides.bind().get(factory)

        if provides is None:
            if util.check_subclass(factory, grok.LocalUtility):
                baseInterfaces = interface.implementedBy(grok.LocalUtility)
                utilityInterfaces = interface.implementedBy(factory)
                provides = list(utilityInterfaces - baseInterfaces)

                if len(provides) == 0 and len(list(utilityInterfaces)) > 0:
                    raise GrokImportError(
                        "Cannot determine which interface to use "
                        "for utility registration of %r. "
                        "It implements an interface that is a specialization "
                        "of an interface implemented by grok.LocalUtility. "
                        "Specify the interface by either using grok.provides "
                        "on the utility or passing 'provides' to "
                        "grok.local_utility." % factory, factory)
            else:
                provides = list(interface.implementedBy(factory))

            util.check_implements_one_from_list(provides, factory)
            provides = provides[0]

        if (provides, name) in self.frame.f_locals.get(self.dotted_name(), {}):
            raise GrokImportError(
                "Conflicting local utility registration %r. "
                "Local utilities are registered multiple "
                "times for interface %r and name %r." %
                (factory, provides, name), factory)

        info = LocalUtilityInfo(factory, provides, name, setup, public,
                                name_in_container)
        return (provides, name), info


class LocalUtilityInfo(object):

    _order = 0

    def __init__(self, factory, provides, name=u'',
                 setup=None, public=False, name_in_container=None):
        self.factory = factory
        self.provides = provides
        self.name = name
        self.setup = setup
        self.public = public
        self.name_in_container = name_in_container

        self.order = LocalUtilityInfo._order
        LocalUtilityInfo._order += 1

    def __cmp__(self, other):
        # LocalUtilityInfos have an inherit sort order by which the
        # registrations take place.
        return cmp(self.order, other.order)


class RequireDirectiveStore(StoreMultipleTimes):

    def get(self, directive, component, default):
        permissions = getattr(component, directive.dotted_name(), default)
        if (permissions is default) or not permissions:
            return default
        if len(permissions) > 1:
            raise GrokError('grok.require was called multiple times in '
                            '%r. It may only be set once for a class.'
                            % component, component)
        return permissions[0]

    def pop(self, locals_, directive):
        return locals_[directive.dotted_name()].pop()

class require(martian.Directive):
    scope = martian.CLASS
    store = RequireDirectiveStore()

    def validate(self, value):
        if util.check_subclass(value, components.Permission):
            return
        if util.not_unicode_or_ascii(value):
            raise GrokImportError(
                "You can only pass unicode, ASCII, or a subclass "
                "of grok.Permission to the '%s' directive." % self.name)

    def factory(self, value):
        if util.check_subclass(value, components.Permission):
            return grok.name.bind().get(value)
        return value

    def __call__(self, func):
        # grok.require can be used both as a class-level directive and
        # as a decorator for methods.  Therefore we return a decorator
        # here, which may be used for methods, or simply ignored when
        # used as a directive.
        frame = sys._getframe(1)
        permission = self.store.pop(frame.f_locals, self)
        self.set(func, [permission])
        return func

class site(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    validate = martian.validateInterfaceOrClass

class permissions(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = []

    def factory(*args):
        return args

class OneInterfaceOrClassOnClassOrModule(martian.Directive):
    """Convenience base class.  Not for public use."""
    scope = martian.CLASS_OR_MODULE
    store = martian.ONCE
    validate = martian.validateInterfaceOrClass

class layer(OneInterfaceOrClassOnClassOrModule):
    pass

class viewletmanager(OneInterfaceOrClassOnClassOrModule):
    scope = UnambiguousComponentScope('viewletmanager')

class view(OneInterfaceOrClassOnClassOrModule):
    default = IBrowserView

class traversable(martian.Directive):
    scope = martian.CLASS
    store = martian.DICT

    def factory(self, attr, name=None):
        if name is None:
            name = attr
        return (name, attr)

class order(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = 0, 0

    _order = 0

    def factory(self, value=0):
        order._order += 1
        return value, order._order
