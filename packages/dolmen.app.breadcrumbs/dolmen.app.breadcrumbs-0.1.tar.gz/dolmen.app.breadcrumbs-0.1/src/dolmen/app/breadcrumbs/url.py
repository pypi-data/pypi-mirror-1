# -*- coding: utf-8 -*-

import urllib
import grokcore.view as grok

from dolmen.content import IBaseContent
from zope.proxy import sameProxiedObjects
from zope.component import getMultiAdapter
from zope.traversing.browser import absoluteurl


class TitleAwareAbsoluteURL(absoluteurl.AbsoluteURL, grok.View):
    grok.name('absolute_url')
    grok.context(IBaseContent)

    render = absoluteurl.AbsoluteURL.__call__

    def breadcrumbs(self):
        context = self.context
        request = self.request

        # We do this here do maintain the rule that we must be wrapped
        container = getattr(context, '__parent__', None)
        if container is None:
            raise TypeError(absoluteurl._insufficientContext)


        # We need to check for the name
        name = getattr(context, '__name__', None)
        if name is None:
            raise TypeError(absoluteurl._insufficientContext)


        # We try to use the title instead of the name here.
        title = context.title or name

        if sameProxiedObjects(context, request.getVirtualHostRoot()) or \
               isinstance(context, Exception):
            return ({'name': title,
                     'url': self.request.getApplicationURL()}, )

        base = tuple(getMultiAdapter((container, request),
                                     name='absolute_url').breadcrumbs())
        if name:
            base += ({'name': title,
                      'url': ("%s/%s" % (base[-1]['url'],
                                         urllib.quote(name.encode('utf-8'),
                                                      absoluteurl._safe)))
                      }, )

        return base
