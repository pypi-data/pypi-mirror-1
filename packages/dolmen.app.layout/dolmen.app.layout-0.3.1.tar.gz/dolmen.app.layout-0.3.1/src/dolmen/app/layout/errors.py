# -*- coding: utf-8 -*-

import grok
from dolmen.app.layout import Page
from zope.publisher.interfaces import INotFound

grok.templatedir("templates")


class NotFound(Page):
    grok.name("index.html")
    grok.context(INotFound)
    grok.require("zope.Public")
        
    def update(self):
        self.request.response.setStatus(404)

    def application_url(self, name=None):
        obj = self.context.ob
        while obj is not None:
            if isinstance(obj, grok.Application):
                return self.url(obj, name)
            obj = obj.__parent__
        return self.request.URL.get(0)
