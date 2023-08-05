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
from z3c.form import form, field
from z3c.formui import layout
from zope.app.zapi import absoluteURL
from zope.app.pagetemplate import ViewPageTemplateFile

from zcontact import person, interfaces

class PersonContainerEditForm(object):
    """Person Container Edit Form."""



class PersonAddForm(layout.FormLayoutSupport, form.AddForm):

    template = ViewPageTemplateFile('templates/form.pt')
    label = "Add User"
    layout = None
    contentName = None
    fields = field.Fields(interfaces.IPerson).omit('passwordManagerName')

    def create(self, data):
        obj = person.Person(data['login'], data['password'], data['title'],
                            description=data['description'],
                            passwordManagerName='SHA1')
        return obj

    def add(self, object):
        name = object.login
        self.context[name] = object
        return object

    def nextURL(self):
        return absoluteURL(self.context, self.request)


class PersonDisplayForm(layout.FormLayoutSupport, form.EditForm):

    template = ViewPageTemplateFile('templates/form.pt')
    layout = None
    contentname = None

    @property
    def label(self):
        return self.context.title

    fields = field.Fields(interfaces.IPerson).omit('passwordManagerName', 'password')
