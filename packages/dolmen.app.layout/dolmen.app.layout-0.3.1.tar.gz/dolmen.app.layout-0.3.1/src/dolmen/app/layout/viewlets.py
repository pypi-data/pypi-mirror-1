# -*- coding: utf-8 -*-

import grok

from dolmen.content import IBaseContent
from dolmen.app.layout import interfaces as API
from dolmen.app.layout import MenuViewlet, AboveBody, Top

from zope.component import getUtility
from zope.interface import Interface, moduleProvides
from z3c.flashmessage.interfaces import IMessageReceiver


class FlashMessages(grok.Viewlet):
    grok.order(10)
    grok.context(Interface)
    grok.name('dolmen.messages')
    grok.viewletmanager(AboveBody)
    
    def update(self):
        source = getUtility(IMessageReceiver)
        self.messages = list(source.receive())


class ContextualActions(MenuViewlet):
    grok.context(IBaseContent)
    grok.viewletmanager(Top)
    grok.order(50)

    menu_name = u'contextual-actions'

    def get_actions(self, context):
        title, actions = MenuViewlet.get_actions(self, context)
        if len(actions) <= 1:
            return title, []
        return title, actions


moduleProvides(API.IContextualUI)
__all__ = list(API.IContextualUI)
