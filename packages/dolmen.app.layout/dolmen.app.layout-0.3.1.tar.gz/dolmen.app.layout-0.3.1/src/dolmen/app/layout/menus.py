# -*- coding: utf-8 -*-

import grok
import megrok.menu

from dolmen.app.layout import interfaces as API

from zope.component import getUtility
from zope.interface import moduleProvides
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.browsermenu.interfaces import IBrowserMenu


class ContextualMenu(megrok.menu.Menu):
    grok.name('contextual-actions')
    grok.title('Contextual actions')


class ContextualMenuEntry(object):
    """Defines an contextual actions menu entry.
    """
    grok.baseclass()
    megrok.menu.menuitem(ContextualMenu)


class MenuViewlet(grok.Viewlet):
    grok.baseclass()
    grok.require("dolmen.content.View")

    template = grok.PageTemplateFile("templates/genericmenu.pt")

    menu_class = u"menu"
    entry_class = u"entry"
    actions = []

    @property
    def menu_name(self):
        raise NotImplementedError("You need to specify a menu name.")

    def get_context(self):
        return self.context

    def get_actions(self, context):
        menu = getUtility(IBrowserMenu, self.menu_name)
        actions = menu.getMenuItems(context, self.request)
        return menu.title, actions

    def update(self):
        """Gets the actions and determines which is the selected one.
        """
        context = self.get_context()
        self.title, actions = self.get_actions(context)
        
        if actions:
            url = absoluteURL(context, self.request)
            selected = getattr(self.view, '__name__', None)
            self.actions = [{'url': "%s/%s" % (url, action['action']),
                             'title': action['title'],
                             'selected': action['action'] == selected,
                             'css': (action['action'] == selected
                                     and self.entry_class + ' selected'
                                     or self.entry_class)}
                            for action in actions]


moduleProvides(API.IMenus)
__all__ = list(API.IMenus)
