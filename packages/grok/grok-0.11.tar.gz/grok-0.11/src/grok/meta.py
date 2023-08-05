#############################################################################
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
"""Grokkers for the various components."""

import os

import zope.component.interface
from zope import interface, component
from zope.publisher.interfaces.browser import (IDefaultBrowserLayer,
                                               IBrowserRequest,
                                               IBrowserPublisher,
                                               IBrowserSkinType)
from zope.publisher.interfaces.xmlrpc import IXMLRPCRequest
from zope.security.interfaces import IPermission
from zope.app.securitypolicy.interfaces import IRole
from zope.app.securitypolicy.rolepermission import rolePermissionManager

from zope.annotation.interfaces import IAnnotations

from zope.app.publisher.xmlrpc import MethodPublisher
from zope.app.container.interfaces import IContainer
from zope.app.container.interfaces import INameChooser
from zope.app.container.contained import contained

from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope.app.catalog.catalog import Catalog
from zope.app.catalog.interfaces import ICatalog

from zope.exceptions.interfaces import DuplicationError

import martian
from martian.error import GrokError
from martian import util

import grok
from grok import components, formlib, templatereg
from grok.util import check_adapts, get_default_permission, make_checker
from grok.util import determine_class_directive
from grok.rest import RestPublisher
from grok.interfaces import IRESTSkinType

class ContextGrokker(martian.GlobalGrokker):

    priority = 1001

    def grok(self, name, module, module_info, config, **kw):
        possible_contexts = martian.scan_for_classes(module, [grok.Model,
                                                              grok.Container])
        context = util.determine_module_context(module_info, possible_contexts)
        module.__grok_context__ = context
        return True


class AdapterGrokker(martian.ClassGrokker):
    component_class = grok.Adapter

    def grok(self, name, factory, module_info, config, **kw):
        context = module_info.getAnnotation('grok.context', None)
        adapter_context = util.determine_class_context(factory, context)
        provides = util.class_annotation(factory, 'grok.provides', None)
        if provides is None:
            util.check_implements_one(factory)
        name = util.class_annotation(factory, 'grok.name', '')

        config.action( 
            discriminator=('adapter', adapter_context, provides, name),
            callable=component.provideAdapter,
            args=(factory, (adapter_context,), provides, name),
            )
        return True

class MultiAdapterGrokker(martian.ClassGrokker):
    component_class = grok.MultiAdapter

    def grok(self, name, factory, module_info, config, **kw):
        provides = util.class_annotation(factory, 'grok.provides', None)
        if provides is None:
            util.check_implements_one(factory)
        check_adapts(factory)
        name = util.class_annotation(factory, 'grok.name', '')
        for_ = component.adaptedBy(factory)

        config.action(
            discriminator=('adapter', for_, provides, name),
            callable=component.provideAdapter,
            args=(factory, None, provides, name),
            )
        return True


class GlobalUtilityGrokker(martian.ClassGrokker):
    component_class = grok.GlobalUtility

    # This needs to happen before the FilesystemPageTemplateGrokker grokker 
    # happens, since it relies on the ITemplateFileFactories being grokked.
    priority = 1100

    def grok(self, name, factory, module_info, config, **kw):
        provides = util.class_annotation(factory, 'grok.provides', None)
        if provides is None:
            util.check_implements_one(factory)
        name = util.class_annotation(factory, 'grok.name', '')
        direct = util.class_annotation(factory, 'grok.direct', False)
        if not direct:
            factory = factory()

        config.action(
            discriminator=('utility', provides, name),
            callable=component.provideUtility,
            args=(factory, provides, name),
            )
        return True


class XMLRPCGrokker(martian.ClassGrokker):
    component_class = grok.XMLRPC

    def grok(self, name, factory, module_info, config, **kw):
        context = module_info.getAnnotation('grok.context', None)
        view_context = util.determine_class_context(factory, context)
        # XXX We should really not make __FOO__ methods available to
        # the outside -- need to discuss how to restrict such things.
        methods = util.methods_from_class(factory)

        default_permission = get_default_permission(factory)

        for method in methods:
            name = method.__name__
            if name.startswith('__'):
                continue

            # Make sure that the class inherits MethodPublisher, so that the
            # views have a location
            method_view = type(
                factory.__name__, (factory, MethodPublisher),
                {'__call__': method}
                )

            adapts = (view_context, IXMLRPCRequest)
            config.action(
                discriminator=('adapter', adapts, interface.Interface, name),
                callable=component.provideAdapter,
                args=(method_view, adapts, interface.Interface, name),
                )

            # Protect method_view with either the permission that was
            # set on the method, the default permission from the class
            # level or zope.Public.
            permission = getattr(method, '__grok_require__',
                                 default_permission)

            config.action(
                discriminator=('protectName', method_view, '__call__'),
                callable=make_checker,
                args=(factory, method_view, permission),
                )
        return True

class RESTGrokker(martian.ClassGrokker):
    component_class = grok.REST
    
    def grok(self, name, factory, module_info, config, **kw):
        context = module_info.getAnnotation('grok.context', None)
        view_context = util.determine_class_context(factory, context)
        # XXX We should really not make __FOO__ methods available to
        # the outside -- need to discuss how to restrict such things.
        methods = util.methods_from_class(factory)

        default_permission = get_default_permission(factory)

        # grab layer from class or module
        view_layer = determine_class_directive('grok.layer', factory,
                                               module_info,
                                               default=grok.IRESTLayer)
        
        for method in methods:
            name = method.__name__
            if name.startswith('__'):
                continue

            # Make sure that the class inherits RestPublisher, so that the
            # views have a location
            method_view = type(
                factory.__name__, (factory, RestPublisher),
                {'__call__': method }
                )

            adapts = (view_context, view_layer)
            config.action(
                discriminator=('adapter', adapts, interface.Interface, name),
                callable=component.provideAdapter,
                args=(method_view, adapts, interface.Interface, name),
                )

            # Protect method_view with either the permission that was
            # set on the method, the default permission from the class
            # level or zope.Public.
            permission = getattr(method, '__grok_require__',
                                 default_permission)
            config.action(
                discriminator=('protectName', method_view, '__call__'),
                callable=make_checker,
                args=(factory, method_view, permission),
                )
        return True
    
    
class ViewGrokker(martian.ClassGrokker):
    component_class = grok.View

    def grok(self, name, factory, module_info, config, **kw):
        context = module_info.getAnnotation('grok.context', None)
        view_context = util.determine_class_context(factory, context)

        factory.module_info = module_info
        factory_name = factory.__name__.lower()

        if util.check_subclass(factory, components.GrokForm):
            # setup form_fields from context class if we've encountered a form
            if getattr(factory, 'form_fields', None) is None:
                factory.form_fields = formlib.get_auto_fields(view_context)

            if not getattr(factory.render, 'base_method', False):
                raise GrokError(
                    "It is not allowed to specify a custom 'render' "
                    "method for form %r. Forms either use the default "
                    "template or a custom-supplied one." % factory,
                    factory)

        # find templates
        templates = module_info.getAnnotation('grok.templates', None)
        if templates is not None:
            config.action(
                discriminator=None,
                callable=templates.checkTemplates,
                args=(module_info, factory, factory_name)
            )

        # safety belt: make sure that the programmer didn't use
        # @grok.require on any of the view's methods.
        methods = util.methods_from_class(factory)
        for method in methods:
            if getattr(method, '__grok_require__', None) is not None:
                raise GrokError('The @grok.require decorator is used for '
                                'method %r in view %r. It may only be used '
                                'for XML-RPC methods.'
                                % (method.__name__, factory), factory)

        # grab layer from class or module
        view_layer = determine_class_directive('grok.layer',
                                               factory, module_info,
                                               default=IDefaultBrowserLayer)

        view_name = util.class_annotation(factory, 'grok.name',
                                          factory_name)
        # __view_name__ is needed to support IAbsoluteURL on views
        factory.__view_name__ = view_name
        adapts = (view_context, view_layer)

        config.action(
            discriminator=('adapter', adapts, interface.Interface, view_name),
            callable=component.provideAdapter,
            args=(factory, adapts, interface.Interface, view_name),
            )

        permission = get_default_permission(factory)
        config.action(
            discriminator=('protectName', factory, '__call__'),
            callable=make_checker,
            args=(factory, factory, permission),
            )

        return True

def view__getitem__(self, key):
    return self.template.macros[key]


class JSONGrokker(martian.ClassGrokker):
    component_class = grok.JSON

    def grok(self, name, factory, module_info, config, **kw):
        context = module_info.getAnnotation('grok.context', None)
        view_context = util.determine_class_context(factory, context)
        methods = util.methods_from_class(factory)

        default_permission = get_default_permission(factory)

        for method in methods:
            # Create a new class with a __view_name__ attribute so the
            # JSON class knows what method to call.
            method_view = type(
                factory.__name__, (factory,),
                {'__view_name__': method.__name__}
                )
            adapts = (view_context, IDefaultBrowserLayer)
            name = method.__name__

            config.action(
                discriminator=('adapter', adapts, interface.Interface, name),
                callable=component.provideAdapter,
                args=(method_view, adapts, interface.Interface, name),
                )

            # Protect method_view with either the permission that was
            # set on the method, the default permission from the class
            # level or zope.Public.

            permission = getattr(method, '__grok_require__',
                                 default_permission)

            config.action(
                discriminator=('protectName', method_view, '__call__'),
                callable=make_checker,
                args=(factory, method_view, permission),
                )
        return True


class TraverserGrokker(martian.ClassGrokker):
    component_class = grok.Traverser

    def grok(self, name, factory, module_info, config, **kw):
        context = module_info.getAnnotation('grok.context', None)
        factory_context = util.determine_class_context(factory, context)
        adapts = (factory_context, IBrowserRequest)

        config.action(
            discriminator=('adapter', adapts, IBrowserPublisher, ''),
            callable=component.provideAdapter,
            args=(factory, adapts, IBrowserPublisher),
            )            
        return True


class TemplateGrokker(martian.GlobalGrokker):
    # this needs to happen before any other grokkers execute that use
    # the template registry
    priority = 1001

    def grok(self, name, module, module_info, config, **kw):
        module.__grok_templates__ = templatereg.TemplateRegistry()
        return True


class ModulePageTemplateGrokker(martian.InstanceGrokker):
    # this needs to happen before any other grokkers execute that actually
    # use the templates
    priority = 1000

    component_class = grok.components.BaseTemplate

    def grok(self, name, instance, module_info, config, **kw):
        templates = module_info.getAnnotation('grok.templates', None)
        if templates is None:
            return False
        config.action(
            discriminator=None,
            callable=templates.register,
            args=(name, instance)
        )
        config.action(
            discriminator=None,
            callable=instance._annotateGrokInfo,
            args=(name, module_info.dotted_name)
        )
        return True
        

class FilesystemPageTemplateGrokker(martian.GlobalGrokker):
    # do this early on, but after ModulePageTemplateGrokker, as
    # findFilesystem depends on module-level templates to be
    # already grokked for error reporting
    priority = 999

    def grok(self, name, module, module_info, config, **kw):
        templates = module_info.getAnnotation('grok.templates', None)
        if templates is None:
            return False
        config.action(
            discriminator=None,
            callable=templates.findFilesystem,
            args=(module_info,)
        )
        return True


class UnassociatedTemplatesGrokker(martian.GlobalGrokker):
    priority = -1001

    def grok(self, name, module, module_info, config, **kw):
        templates = module_info.getAnnotation('grok.templates', None)
        if templates is None:
            return False
        
        config.action(
            discriminator=None,
            callable=templates.checkUnassociated,
            args=(module_info,)
        )
        return True


class SubscriberGrokker(martian.GlobalGrokker):

    def grok(self, name, module, module_info, config, **kw):
        subscribers = module_info.getAnnotation('grok.subscribers', [])

        for factory, subscribed in subscribers:
            config.action( 
                discriminator=None,
                callable=component.provideHandler,
                args=(factory, subscribed),
                )

            for iface in subscribed:
                config.action(
                    discriminator=None,
                    callable=zope.component.interface.provideInterface,
                    args=('', iface)
                    )
        return True


class AdapterDecoratorGrokker(martian.GlobalGrokker):

    def grok(self, name, module, module_info, config, **kw):
        context = module_info.getAnnotation('grok.context', None)
        implementers = module_info.getAnnotation('implementers', [])
        for function in implementers:
            interfaces = getattr(function, '__component_adapts__', None)
            if interfaces is None:
                # There's no explicit interfaces defined, so we assume the
                # module context to be the thing adapted.
                util.check_context(module_info.getModule(), context)
                interfaces = (context, )
            
            config.action( 
                discriminator=('adapter', interfaces, function.__implemented__),
                callable=component.provideAdapter,
                args=(function, interfaces, function.__implemented__),
                )
        return True


class StaticResourcesGrokker(martian.GlobalGrokker):

    def grok(self, name, module, module_info, config, **kw):
        # we're only interested in static resources if this module
        # happens to be a package
        if not module_info.isPackage():
            return False

        resource_path = module_info.getResourcePath('static')
        if os.path.isdir(resource_path):
            static_module = module_info.getSubModuleInfo('static')
            if static_module is not None:
                if static_module.isPackage():
                    raise GrokError(
                        "The 'static' resource directory must not "
                        "be a python package.",
                        module_info.getModule())
                else:
                    raise GrokError(
                        "A package can not contain both a 'static' "
                        "resource directory and a module named "
                        "'static.py'", module_info.getModule())

        resource_factory = components.DirectoryResourceFactory(
            resource_path, module_info.dotted_name)
        component.provideAdapter(
            resource_factory, (IDefaultBrowserLayer,),
            interface.Interface, name=module_info.dotted_name)
        return True


class GlobalUtilityDirectiveGrokker(martian.GlobalGrokker):

    def grok(self, name, module, module_info, config, **kw):
        infos = module_info.getAnnotation('grok.global_utility', [])

        for info in infos:
            if info.provides is None:
                util.check_implements_one(info.factory)
            if info.direct:
                obj = info.factory
            else:
                obj = info.factory()
            component.provideUtility(obj,
                                     provides=info.provides,
                                     name=info.name)
        return True


class SiteGrokker(martian.ClassGrokker):
    component_class = grok.Site
    priority = 500

    def grok(self, name, factory, module_info, config, **kw):
        infos = util.class_annotation_list(factory, 'grok.local_utility', None)
        if infos is None:
            return False

        for info in infos:
            if info.public and not IContainer.implementedBy(factory):
                raise GrokError(
                    "Cannot set public to True with grok.local_utility as "
                    "the site (%r) is not a container." %
                    factory, factory)
            if info.provides is None:
                if util.check_subclass(info.factory, grok.LocalUtility):
                    baseInterfaces = interface.implementedBy(grok.LocalUtility)
                    utilityInterfaces = interface.implementedBy(info.factory)
                    provides = list(utilityInterfaces - baseInterfaces)

                    if len(provides) == 0 and len(list(utilityInterfaces)) > 0:
                        raise GrokError(
                            "Cannot determine which interface to use "
                            "for utility registration of %r in site %r. "
                            "It implements an interface that is a specialization "
                            "of an interface implemented by grok.LocalUtility. "
                            "Specify the interface by either using grok.provides "
                            "on the utility or passing 'provides' to "
                            "grok.local_utility." % (info.factory, factory),
                            info.factory)
                else:
                    provides = list(interface.implementedBy(info.factory))

                util.check_implements_one_from_list(provides, info.factory)
                info.provides = provides[0]

        # raise an error in case of any duplicate registrations
        # on the class level (subclassing overrides, see below)
        used = set()
        class_infos = util.class_annotation(factory, 'grok.local_utility',
                                            [])
        for info in class_infos:
            key = (info.provides, info.name)
            if key in used:
                raise GrokError(
                    "Conflicting local utility registration %r in "
                    "site %r. Local utilities are registered multiple "
                    "times for interface %r and name %r." %
                    (info.factory, factory, info.provides, info.name),
                    factory)
            used.add(key)

        # Make sure that local utilities from subclasses override
        # utilities from base classes if the registration (provided
        # interface, name) is identical.
        overridden_infos = []
        used = set()
        for info in reversed(infos):
            key = (info.provides, info.name)
            if key in used:
                continue
            used.add(key)
            overridden_infos.append(info)
        overridden_infos.reverse()

        # store infos on site class
        factory.__grok_utilities_to_install__ = overridden_infos
        adapts = (factory, grok.IObjectAddedEvent)

        config.action( 
            discriminator=None,
            callable=component.provideHandler,
            args=(localUtilityRegistrationSubscriber, adapts),
            )
        return True


def localUtilityRegistrationSubscriber(site, event):
    """A subscriber that fires to set up local utilities.
    """
    installed = getattr(site, '__grok_utilities_installed__', False)
    if installed:
        return

    for info in util.class_annotation(site.__class__,
                                      'grok.utilities_to_install', []):
        setupUtility(site, info.factory(), info.provides, name=info.name,
                     name_in_container=info.name_in_container,
                     public=info.public, setup=info.setup)

    # we are done. If this subscriber gets fired again, we therefore
    # do not register utilities anymore
    site.__grok_utilities_installed__ = True


def setupUtility(site, utility, provides, name=u'',
                 name_in_container=None, public=False, setup=None):
    """Set up a utility in a site.

    site - the site to set up the utility in
    utility - the utility to set up
    provides - the interface the utility should be registered with
    name - the name the utility should be registered under, default
      the empty string (no name)
    name_in_container - if given it will be used to add the utility
      object to its container. Otherwise a name will be made up
    public - if False, the utility will be stored in the site manager. If
      True, the utility will be storedin the site (it is assumed the
      site is a container)
    setup - if not None, it will be called with the utility as its first
       argument. This function can then be used to further set up the
       utility.
    """
    site_manager = site.getSiteManager()

    if not public:
        container = site_manager
    else:
        container = site

    if name_in_container is None:
        name_in_container = INameChooser(container).chooseName(
            utility.__class__.__name__, utility)
    container[name_in_container] = utility

    if setup is not None:
        setup(utility)

    site_manager.registerUtility(utility, provided=provides,
                                 name=name)

class PermissionGrokker(martian.ClassGrokker):
    component_class = grok.Permission
    priority = 1500

    def grok(self, name, factory, module_info, config, **kw):
        id = util.class_annotation(factory, 'grok.name', None)
        if id is None:
            raise GrokError(
                "A permission needs to have a dotted name for its id. Use "
                "grok.name to specify one.", factory)
        # We can safely convert to unicode, since the directives make sure
        # it is either unicode already or ASCII.
        id = unicode(id)
        permission = factory(
            id,
            unicode(util.class_annotation(factory, 'grok.title', id)),
            unicode(util.class_annotation(factory, 'grok.description', '')))

        config.action( 
            discriminator=('utility', IPermission, name),
            callable=component.provideUtility,
            args=(permission, IPermission, id),
            order=self.priority
            )
        return True

class RoleGrokker(martian.ClassGrokker):
    component_class = grok.Role
    priority = PermissionGrokker.priority - 1

    def grok(self, name, factory, module_info, config, **kw):
        id = util.class_annotation(factory, 'grok.name', None)
        if id is None:
            raise GrokError(
                "A role needs to have a dotted name for its id. Use "
                "grok.name to specify one.", factory)
        # We can safely convert to unicode, since the directives makes sure
        # it is either unicode already or ASCII.
        id = unicode(id)
        role = factory(
            id,
            unicode(util.class_annotation(factory, 'grok.title', id)),
            unicode(util.class_annotation(factory, 'grok.description', '')))

        config.action( 
            discriminator=('utility', IRole, name),
            callable=component.provideUtility,
            args=(role, IRole, id),
            )

        permissions = util.class_annotation(factory, 'grok.permissions', ())
        for permission in permissions:
            config.action(
                discriminator=('grantPermissionToRole', permission, id),
                callable=rolePermissionManager.grantPermissionToRole,
                args=(permission, id),
                )
        return True

class AnnotationGrokker(martian.ClassGrokker):
    component_class = grok.Annotation

    def grok(self, name, factory, module_info, config, **kw):
        context = module_info.getAnnotation('grok.context', None)
        adapter_context = util.determine_class_context(factory, context)
        provides = util.class_annotation(factory, 'grok.provides', None)
        if provides is None:
            base_interfaces = interface.implementedBy(grok.Annotation)
            factory_interfaces = interface.implementedBy(factory)
            real_interfaces = list(factory_interfaces - base_interfaces)
            util.check_implements_one_from_list(real_interfaces, factory)
            provides = real_interfaces[0]

        key = util.class_annotation(factory, 'grok.name', None)
        if key is None:
            key = factory.__module__ + '.' + factory.__name__

        @component.adapter(adapter_context)
        @interface.implementer(provides)
        def getAnnotation(context):
            annotations = IAnnotations(context)
            try:
                result = annotations[key]
            except KeyError:
                result = factory()
                annotations[key] = result

            # Containment has to be set up late to allow containment
            # proxies to be applied, if needed. This does not trigger
            # an event and is idempotent if containment is set up
            # already.
            contained_result = contained(result, context, key)
            return contained_result

        config.action(
            discriminator=('adapter', adapter_context, provides, ''),
            callable=component.provideAdapter,
            args=(getAnnotation,),
            )
        return True


class ApplicationGrokker(martian.ClassGrokker):
    component_class = grok.Application
    priority = 500

    def grok(self, name, factory, module_info, config, **kw):
        # XXX fail loudly if the same application name is used twice.
        provides = grok.interfaces.IApplication
        name = '%s.%s' % (module_info.dotted_name, name)
        config.action(
            discriminator=('utility', provides, name),
            callable=component.provideUtility,
            args=(factory, provides, name),
            )
        return True


class IndexesGrokker(martian.InstanceGrokker):
    component_class = components.IndexesClass

    def grok(self, name, factory, module_info, config, **kw):
        site = util.class_annotation(factory, 'grok.site', None)
        if site is None:
            raise GrokError("No site specified for grok.Indexes "
                            "subclass in module %r. "
                            "Use grok.site() to specify." % module_info.getModule(),
                            factory)
        indexes = util.class_annotation(factory, 'grok.indexes', None)
        if indexes is None:
            return False
        context = module_info.getAnnotation('grok.context', None)
        context = util.determine_class_context(factory, context)
        catalog_name = util.class_annotation(factory, 'grok.name', u'')

        subscriber = IndexesSetupSubscriber(catalog_name, indexes,
                                            context, module_info)
        subscribed = (site, grok.IObjectAddedEvent)
        config.action( 
            discriminator=None,
            callable=component.provideHandler,
            args=(subscriber, subscribed),
            )
        return True


class IndexesSetupSubscriber(object):

    def __init__(self, catalog_name, indexes, context, module_info):
        self.catalog_name = catalog_name
        self.indexes = indexes
        self.context = context
        self.module_info = module_info

    def __call__(self, site, event):
        # make sure we have an intids
        self._createIntIds(site)
        # get the catalog
        catalog = self._createCatalog(site)
        # now install indexes
        for name, index in self.indexes.items():
            try:
                index.setup(catalog, name, self.context, self.module_info)
            except DuplicationError:
                raise GrokError(
                    "grok.Indexes in module %r causes "
                    "creation of catalog index %r in catalog %r, "
                    "but an index with that name is already present." %
                    (self.module_info.getModule(), name, self.catalog_name),
                    None)

    def _createCatalog(self, site):
        """Create the catalog if needed and return it.

        If the catalog already exists, return that.

        """
        catalog = zope.component.queryUtility(
            ICatalog, name=self.catalog_name, context=site, default=None)
        if catalog is not None:
            return catalog
        catalog = Catalog()
        setupUtility(site, catalog, ICatalog, name=self.catalog_name)
        return catalog

    def _createIntIds(self, site):
        """Create intids if needed, and return it.
        """
        intids = zope.component.queryUtility(
            IIntIds, context=site, default=None)
        if intids is not None:
            return intids
        intids = IntIds()
        setupUtility(site, intids, IIntIds)
        return intids


class SkinGrokker(martian.ClassGrokker):
    component_class = grok.Skin

    def grok(self, name, factory, module_info, config, **kw):
        layer = determine_class_directive('grok.layer', factory, module_info,
                                          default=IBrowserRequest)
        name = grok.util.class_annotation(factory, 'grok.name',
                                          factory.__name__.lower())
        config.action(
            discriminator=None,
            callable=zope.component.interface.provideInterface,
            args=(name, layer, IBrowserSkinType)
            )
        return True

class RESTProtocolGrokker(martian.ClassGrokker):
    component_class = grok.RESTProtocol

    def grok(self, name, factory, module_info, config, **kw):
        layer = determine_class_directive('grok.layer', factory, module_info,
                                          default=IBrowserRequest)
        name = grok.util.class_annotation(factory, 'grok.name',
                                          factory.__name__.lower())
        config.action(
            discriminator=None,
            callable=zope.component.interface.provideInterface,
            args=(name, layer, IRESTSkinType)
            )
        return True
