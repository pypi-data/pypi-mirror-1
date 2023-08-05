from zope.viewlet.interfaces import IViewletManager
from zope.viewlet.viewlet import CSSViewlet
from zope.viewlet.viewlet import JavaScriptViewlet
from zope.viewlet.manager import ViewletManager
from z3c.pagelet import browser
from z3c.formui import interfaces
from z3c.menu.simple.menu import GlobalMenuItem
from z3c.menu.simple.menu import ContextMenuItem
from z3c.viewlet.manager import WeightOrderedViewletManager
from zcontact import layer


class IZContactBrowserSkin(interfaces.IDivFormLayer, layer.IZContactWithScriptBrowserLayer):
    """The ``ZContact`` browser skin."""

class IZContactNoScriptBrowserSkin(interfaces.IDivFormLayer, layer.IZContactNoScriptBrowserLayer):
    """The ``ZContact`` browser skin for non-javascript support."""


class ICSS(interfaces.ICSS):
    """CSS viewlet manager."""


class IJavaScript(IViewletManager):
    """JavaScript viewlet manager."""


ZContactCSSViewlet = CSSViewlet('zcontact.css')
JQueryJavaScriptViewlet = JavaScriptViewlet('jquery.js')
JQueryFormJavaScriptViewlet = JavaScriptViewlet('jquery.form.js')

class IMessageArea(IViewletManager):
    """Message Box Viewlet manager."""

ZContactMessageArea = ViewletManager('zcontact-message-area', IMessageArea,
                                     bases=(WeightOrderedViewletManager,))

## Menus!!! ##

class IActionMenu(IViewletManager):
    """Action Menu thingymabob."""

ZContactActionMenu = ViewletManager('zcontact-actions', IActionMenu,
                                    bases=(WeightOrderedViewletManager,))


class INavigationMenu(IViewletManager):
    """Navigation menu."""

ZContactNavigationMenu = ViewletManager('zcontact-navigation', INavigationMenu,
                                        bases=(WeightOrderedViewletManager,))


class NavigationMenuItem(GlobalMenuItem):

    urlHas = None
    urlEndsWith = None

    @property
    def selected(self):
        requestURL = self.request.getURL()
        if (self.urlHas is not None
            and self.urlHas in requestURL or
            (self.urlEndsWith is not None
             and requestURL.endswith(self.urlEndsWith))):
            return True
        return False

class ActionMenuItem(ContextMenuItem):

    @property
    def url(self):
        try:
            return super(ActionMenuItem, self).url
        except TypeError:
            return ''
