# -*- coding: utf-8 -*-

import grok
import megrok.menu
import megrok.layout
import megrok.z3ctable

from zope.component import getUtility
from zope.interface import moduleProvides
from zope.i18nmessageid import MessageFactory

from megrok.z3cform import composed
from z3c.flashmessage.interfaces import IMessageSource

from dolmen.forms import crud
from dolmen.forms.base import PageForm, cancellable

from dolmen.app.site import IDolmen
from dolmen.app.layout import interfaces as API
from dolmen.app.layout import IDisplayView, ContextualMenuEntry

_ = MessageFactory("dolmen")


class ApplicationAwareView(object):
    """A mixin allowing to access the application url 
    """
    def application_url(self, name=None):
        """Return the URL of the nearest Dolmen site.
        """
        obj = self.context
        while obj is not None:
            if IDolmen.providedBy(obj):
                return self.url(obj, name)
            obj = obj.__parent__
        raise ValueError("No application found.")


    def flash(self, message, type='message'):
        """Send a short message to the user.
        """
        source = getUtility(IMessageSource, name='session')
        source.send(message, type)


class Page(megrok.layout.Page, ApplicationAwareView):
    """A dolmen site page.
    """
    grok.baseclass()
    grok.require("dolmen.content.View")
    grok.implements(IDisplayView)

    
class TablePage(megrok.z3ctable.TablePage, ApplicationAwareView):
    """A table rendered as a page.
    """
    grok.baseclass()
        

class Index(Page, ContextualMenuEntry):
    """A simple index for dolmen objects.
    """
    grok.baseclass()
    grok.name('index')
    grok.title(_(u"View"))
    grok.require("dolmen.content.View")
    grok.implements(IDisplayView)


class DefaultView(crud.Display, ContextualMenuEntry, ApplicationAwareView):
    """The view per default for dolmen contents.
    """
    grok.name('index')
    grok.implements(IDisplayView)
    grok.require("dolmen.content.View")


class Form(PageForm, ApplicationAwareView):
    """A simple dolmen form.
    """
    grok.baseclass()
    cancellable(True)
    grok.require("dolmen.content.View")
    ignoreContext = True


class SubForm(composed.SubForm, ApplicationAwareView):
    """A SubForm base class with a nice template.
    """
    grok.baseclass()

    
class Add(crud.Add, ApplicationAwareView):
    """A generic form to add contents.
    """
    cancellable(True)
    

class Edit(crud.Edit, ContextualMenuEntry, ApplicationAwareView):
    """A generic form to edit contents.
    """
    grok.order(20)
    cancellable(True)
    grok.require("dolmen.content.Edit")


class Delete(crud.Delete, ContextualMenuEntry, ApplicationAwareView):
    """A delete form.
    """
    grok.order(30)
    cancellable(True)
    grok.require("dolmen.content.Delete")
    
    def nextURL(self):
        if self._deleted == False:
            self.flash(_("The object could not be deleted."))
            return self.url(self.context)
        self.flash(_("The object has been deleted."))
        self.redirect(self.url(self.context))


moduleProvides(API.IModels, API.IBaseViews)
__all__ = list(API.IModels) + list(API.IBaseViews)
