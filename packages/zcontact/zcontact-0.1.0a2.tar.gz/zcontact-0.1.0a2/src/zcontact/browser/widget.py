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
import os
import os.path
from zope.app.pagetemplate import ViewPageTemplateFile
from z3c.form.interfaces import IWidget, IFormLayer, INPUT_MODE, IFieldWidget
from z3c.form import button, field, form, widget, converter
import zope.component
import zope.interface
from zcontact import interfaces
from z3c.form.widget import WidgetTemplateFactory

class IListWidget(IWidget):
    """List widget."""


class ListWidget(widget.Widget):
    """Input type radio widget implementation."""

    zope.interface.implementsOnly(IListWidget)

    css = u'radioWidget'
    alt = None
    readonly = None
    accesskey = None

    def __init__(self, *args, **kw):
        super(ListWidget, self).__init__(*args, **kw)
        # we are assuming here that the value_type is of zope.schema.Object
        # so it should have a schema attribute.
        #self.schema = self.field.value_type.schema

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(ListWidget, self).update()
        self.form = ListWidgetForm(self.context, self.request, self)
        self.form.prefix = self.name+'.'
        self.form.update()

    def render(self):
        return self.form.render()


class ListWidgetForm(form.Form):
    """The Form with multiple inputs used for the list widget."""
    template = ViewPageTemplateFile('templates/list_input.pt')
    layout = None
    contentName = None
    label = u''
    fields = field.Fields()

    addform = u"There was no add form specified"
    showAddForm = False

    def __init__(self, context, request, widget):
        super(ListWidgetForm, self).__init__(context, request)
        self.widget = widget
        self.value_type = widget.field.value_type
        self.interface = self.value_type.schema

    @button.buttonAndHandler(u'Add', name='add')
    def handleAddButton(self, action):
        self.showAddForm = True

    def update(self):
        super(ListWidgetForm, self).update()


class ListDataConverter(converter.FieldDataConverter):
    """A data converter using the field's ``fromUnicode()`` method."""
    zope.component.adapts(
        zope.schema.interfaces.IList, IListWidget)

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        return value

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        return value


@zope.component.adapter(zope.schema.List, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def ListFieldWidget(field, object, request):
    """IFieldWidget factory for ListWidget."""
    return widget.FieldWidget(field, ListWidget(request))


factory = WidgetTemplateFactory(os.path.join(os.path.dirname(__file__), 'templates/list_input.pt'),
                                widget=ListWidget)
zope.component.provideAdapter(factory, name=INPUT_MODE)
