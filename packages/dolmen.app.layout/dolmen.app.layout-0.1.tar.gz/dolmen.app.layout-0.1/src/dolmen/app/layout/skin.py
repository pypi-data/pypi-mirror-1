# -*- coding: utf-8 -*-

import grok

from zope.interface import moduleProvides
from zope.publisher.interfaces import browser

from dolmen.forms.base import IFormLayer
from dolmen.app.layout import interfaces as API


class IBaseLayer(IFormLayer, browser.IDefaultBrowserLayer):
    """Base layer for a dolmen application
    """


class IBaseSkin(IBaseLayer, browser.IBrowserSkinType):
    """A very basic skin, implementing the needed layers to have a fully
    functional display : forms and other components.
    """
    grok.skin("basic_dolmen_skin")


moduleProvides(API.ISkin)
__all__ = list(API.ISkin)
