
import martian
import five.grok
import grokcore.security

from zope import interface, component
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from five.grok import components
from martian.error import GrokError

from Products.Five.security import protectClass
from Globals import InitializeClass as initializeClass

import os.path

class ViewSecurityGrokker(martian.ClassGrokker):
    martian.component(five.grok.View)
    martian.directive(grokcore.security.require, name='permission')
    
    def execute(self, factory, config, permission, **kw):
        if permission is None:
            permission = 'zope.Public'

        config.action(
            discriminator = ('five:protectClass', factory),
            callable = protectClass,
            args = (factory, permission)
            )

        # Protect the class
        config.action(
            discriminator = ('five:initialize:class', factory),
            callable = initializeClass,
            args = (factory,)
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

            # FIXME: This is public, we need to set security on resources ?
            name = module_info.dotted_name
            resource_factory = components.DirectoryResourceFactory(
                name, resource_path)
            adapts = (IDefaultBrowserLayer,)
            provides = interface.Interface

            config.action(
                discriminator=('adapter', adapts, provides, name),
                callable=component.provideAdapter,
                args=(resource_factory, adapts, provides, name),
                )
            return True

        return False