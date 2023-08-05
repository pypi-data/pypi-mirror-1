# ZContact - Web Based Contact Manager
# Copyright (C) 2007 Paul Carduner
#
# ZContact is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ZContact is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
import urllib
import zope.component
from zope.app import zapi
from zope.app.security.interfaces import IAuthentication
from zope.publisher.browser import applySkin
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.security.browser.auth import HTTPAuthenticationLogin, HTTPAuthenticationLogout
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.security.interfaces import ILogoutSupported

from z3c.formui import layout
from z3c.form import form, field, button

from zcontact.contact import getZContactApplication
from zcontact import skin, interfaces


def skinApply(event):
    if '++skin++' in event.request.getURL(): return
    if getZContactApplication() is not None:
        applySkin(event.request, skin.IZContactBrowserSkin)


class LogoutView(HTTPAuthenticationLogout):
    """Logout view"""

    confirmation = ViewPageTemplateFile('templates/logout.pt')

    redirect = ViewPageTemplateFile('templates/logout_redirect.pt')


class LoginView(HTTPAuthenticationLogin):
    """Login View"""

    confirmation = ViewPageTemplateFile('templates/login.pt')

    failed = ViewPageTemplateFile('templates/login_failed.pt')

class LoginForm(layout.FormLayoutSupport, form.Form):
    """Log in Form"""

class LoginLogout(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if IUnauthenticatedPrincipal.providedBy(self.request.principal):
            return u'<a class="login-button" href="@@login.html?nextURL=%s">%s</a>' % (
                urllib.quote(self.request.getURL()), 'Login')
        elif ILogoutSupported(self.request, None) is not None:
            return u'<a class="logout-button" href="@@logout.html?nextURL=%s">%s</a>' % (
                urllib.quote(self.request.getURL()), 'Logout')
        else:
            return None


class ContactApplicationSettingsForm(layout.FormLayoutSupport, form.Form):
    """Placeholder for a form yet to be implemented."""

    template = None
    layout = None
    contentName = None
    label = u'Application Settings'
    fields = field.Fields(interfaces.IContactApplicationSettings)

    @button.buttonAndHandler(u'Update', name='update')
    def handleUpdate(self, action):
        data, errors = self.widgets.extract()
        if errors:
            self.status = self.formErrorsMessage
            return
        try:
            self.context.mode = data['mode']
        except AttributeError:
            self.status = 'The mode "%s" could not be applied.' % data['mode']
            return
        self.status = 'The mode "%s" was successfully applied.' % data['mode']

    @property
    def currentMode(self):
        return zope.component.queryUtility(interfaces.IContactApplicationMode,
                                           name=self.context.mode)


class PermissionForm(layout.FormLayoutSupport, form.Form):
    """Form for handling permission of individual objects."""

    template = None
    layout = None
    contentName = None
    label = u'Permissions'
    fields = field.Fields()
