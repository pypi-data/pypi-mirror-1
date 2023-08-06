# -*- coding: utf-8 -*-

import grokcore.viewlet as grok
from dolmen.app.layout import master
from zope.interface import Interface
from zope.component import getMultiAdapter


class Breadcrumbs(grok.Viewlet):
    grok.context(Interface)
    grok.name('dolmen.breadcrumbs')
    grok.viewletmanager(master.Top)
    grok.order(30)

    def update(self):
        self.crumbs = getMultiAdapter((self.context, self.request),
                                      name="absolute_url").breadcrumbs()
