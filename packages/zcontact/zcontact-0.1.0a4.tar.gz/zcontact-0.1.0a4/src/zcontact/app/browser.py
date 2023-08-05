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
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.schema import TextLine, Bool
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app.container.interfaces import INameChooser

from z3c.pagelet.browser import BrowserPagelet
from z3c.form import form, button, field
from z3c.form.field import Fields
from z3c.form.interfaces import INPUT_MODE
from z3c.form.interfaces import IWidgets
from z3c.formui.layout import FormLayoutSupport
from z3c.form.browser.checkbox import CheckBoxFieldWidget

from zcontact.interfaces import IContactApplication
from zcontact.contact import ContactApplication


class FrontPageView(BrowserPagelet):
    template = ViewPageTemplateFile("frontpage.pt")


class AboutView(BrowserPagelet):
    template = ViewPageTemplateFile("about.pt")


class HelpView(BrowserPagelet):
    template = ViewPageTemplateFile("help.pt")


class ManageView(FormLayoutSupport, form.Form):
    template = ViewPageTemplateFile("manage.pt")
    
    @button.buttonAndHandler(u'Add a new contact list')
    def handleAddButton(self, form):
        url = absoluteURL(self.context, self.request) + '/@@addContactList.html'
        self.request.response.redirect(url)

    @button.buttonAndHandler(u'Delete')
    def handleDeleteButton(self, form):
        for key in self.request:
            if key.startswith('delete.'):
                name = key.split('delete.')[1]
                if name in self.context.keys():
                    del self.context[name]


class IObjectAddFields(Interface):

    name = TextLine(title=u"Id",
                    description=u"The id which makes the url.",
                    required=False)


class AddContactListView(FormLayoutSupport, form.AddForm):
    fields = field.Fields(IContactApplication) + field.Fields(IObjectAddFields)

    def create(self, data):
        self.addName = data.get('name')
        return ContactApplication(title=data.get('title'))

    def add(self, object):
        if not self.addName:
            self.addName = object.title.replace(' ','')
        name = INameChooser(self.context).chooseName(self.addName, object)
        self.context[name] = object

    def nextURL(self):
        return absoluteURL(self.context, self.request) + '/manage'
