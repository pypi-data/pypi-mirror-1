# -*- coding: utf-8 -*-

import grok
import dolmen.content

from dolmen.app import security, layout
from zope.security.management import checkPermission
from zope.container.interfaces import IContainer
from zope.container.constraints import checkFactory
from zope.component import getUtilitiesFor, getMultiAdapter

grok.templatedir("templates")


class AddMenu(grok.Viewlet):
    grok.order(60)
    grok.view(layout.IDisplayView)
    grok.context(IContainer)
    grok.require(security.CanAddContent)
    grok.viewletmanager(layout.AboveBody)

    def checkFactory(self, name, factory):
        """Verifies the factory and the right of the logged user against
        the container and the required permission of the content type.
        """
        if not checkFactory(self.context, name, factory):
            return False

        permission = dolmen.content.require.bind().get(factory.factory)
        return checkPermission(permission, self.context)

    def update(self):
        """Gathers the factories allowed for the context container
        in a list of factories information useable by the template.
        """
        self.factories = []
        self.contexturl = self.view.url(self.context)

        for name, factory in getUtilitiesFor(dolmen.content.IFactory):
            # We iterate and check the factories
            if self.checkFactory(name, factory):
                factory_class = factory.factory
                icon_view = getMultiAdapter((factory_class, self.request),
                                            name='contenttype_icon')

                self.factories.append(dict(
                    name=name,
                    id=name.replace(".", "-"),
                    icon=icon_view(),
                    url='%s/++add++%s' % (self.contexturl, name),
                    title=factory_class.__content_type__,
                    description=(factory.description or
                                 factory_class.__doc__),
                    ))
