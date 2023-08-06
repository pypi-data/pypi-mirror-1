# -*- coding: utf-8 -*-

import grok
import megrok.layout
import megrok.z3ctable

from megrok.z3cform import composed
from dolmen.forms import crud
from dolmen.forms.base import PageForm, cancellable
from dolmen.app.layout import interfaces as API
from dolmen.app.layout import IDisplayView, ContextualMenuEntry
from zope.interface import moduleProvides


class Page(megrok.layout.Page):
    """A dolmen site page.
    """
    grok.baseclass()
    grok.require("dolmen.content.View")
    grok.implements(IDisplayView)


class TablePage(megrok.z3ctable.TablePage):
    """A table rendered as a page.
    """
    grok.baseclass()


class Index(Page, ContextualMenuEntry):
    """A simple index for dolmen objects.
    """
    grok.baseclass()
    grok.name('index')
    grok.title(crud.i18n(u"View"))
    grok.require("dolmen.content.View")
    grok.implements(IDisplayView)


class DefaultView(crud.Display, ContextualMenuEntry):
    """The view per default for dolmen contents.
    """
    grok.name('index')
    grok.implements(IDisplayView)
    grok.require("dolmen.content.View")


class Form(PageForm):
    """A simple dolmen form.
    """
    grok.baseclass()
    cancellable(True)
    grok.require("dolmen.content.View")
    ignoreContext = True


class SubForm(composed.SubForm):
    """A SubForm base class with a nice template.
    """
    grok.baseclass()


class Add(crud.Add):
    """A generic form to add contents.
    """
    cancellable(True)


class Edit(crud.Edit, ContextualMenuEntry):
    """A generic form to edit contents.
    """
    grok.order(20)
    cancellable(True)
    grok.require("dolmen.content.Edit")


class Delete(crud.Delete, ContextualMenuEntry):
    """A delete form.
    """
    grok.order(30)
    cancellable(True)
    grok.require("dolmen.content.Delete")

    @property
    def successMessage(self):
        self.flash(crud.Delete.successMessage)
        return crud.Delete.successMessage.fget(self)

    @property
    def failureMessage(self):
        self.flash(crud.Delete.failureMessage)
        return crud.Delete.failureMessage


moduleProvides(API.IModels, API.IBaseViews)
__all__ = list(API.IModels) + list(API.IBaseViews)
