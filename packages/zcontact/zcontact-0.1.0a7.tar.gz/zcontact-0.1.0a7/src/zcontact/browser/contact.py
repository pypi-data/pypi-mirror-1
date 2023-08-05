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
from string import Template
from zope.interface import Interface
from zope import schema
import zope.component
import zope.event
from zope.traversing.api import getParents
from zope.traversing.browser import absoluteURL
from zope.pagetemplate.interfaces import IPageTemplate
from zope.viewlet.viewlet import JavaScriptViewlet
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.location.location import locate
from zope.app.container.interfaces import INameChooser

from z3c.pagelet.browser import BrowserPagelet
from z3c.form import button, field, form, widget
from z3c.form.interfaces import IAddForm, IWidgets, DISPLAY_MODE

from z3c.formui import layout
from z3c.formjs import jsaction, jsevent

from zcontact import interfaces
from zcontact import contact
from zcontact.layer import IZContactNoScriptBrowserLayer


class ContactApplicationDisplayView(layout.FormLayoutSupport, form.DisplayForm):
    pass


class ISearchFields(Interface):

    allFields = schema.TextLine(
        title=u"In Any Field",
        required=False)

    title = schema.TextLine(
        title=u"Title",
        required=False)


class ContactSearchForm(form.Form):
    """ A Contact Search Form. """
    template = None
    layout = None
    contentName = None
    label = u'Search Contacts'
    id = "zcontact-ContactSearchForm"
    fields = field.Fields(ISearchFields)
    action = '@@contacts.html'

    @button.buttonAndHandler(u'Search', name='search')
    def handleSearch(self, action):
        pass

    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.ignoreContext = True
        self.widgets.update()


class ContactListView(BrowserPagelet):
    @property
    def contacts(self):
        title = self.request.get('form.widgets.title','')
        for contact in  sorted(self.context.values(), lambda a,b: cmp(a.title, b.title)):
            if title in contact.title:
                yield contact

    #make it an inline pagelet
    __call__ = BrowserPagelet.render


class ContactListWidget(object):
    """Contact List widget"""
    pass

### ================ INLINE FIELD ADD FORMS ================

class ContactFieldAddForm(form.AddForm):

    template = ViewPageTemplateFile('templates/addFieldForm.pt')
    layout = None
    contentName = None
    _canceled = False

    @property
    def action(self):
        return absoluteURL(self, self.request)

    @button.buttonAndHandler(u'Submit', name='add')
    def handleSubmit(self, action):
        super(ContactFieldAddForm, self).handleAdd(self, action)

    @button.buttonAndHandler(u'Cancel', name='cancel')
    def handleCancel(self, action):
        self._canceled = True

    def create(self, data):
        obj = self.factory(**data)
        return obj

    def add(self, object):
        name = u'default'
        if object.title:
            name = object.title.lower().replace(' ','-')
        self.newObjectName = INameChooser(self.context).chooseName(name, object)
        self.context[self.newObjectName] = object
        return object

    def nextURL(self):
        if IZContactNoScriptBrowserLayer.providedBy(self.request):
            url = absoluteURL(self.context.__parent__, self.request)
        else:
            url = absoluteURL(self.context[self.newObjectName], self.request) + '/@@inline.html'
        return url

    def render(self):
        if self._canceled:
            if IZContactNoScriptBrowserLayer.providedBy(self.request):
                self.request.response.redirect(self.nextURL())
            return ""
        else:
            return super(ContactFieldAddForm, self).render()

    def javascript(self):
        if IZContactNoScriptBrowserLayer.providedBy(self.request):
            return ""
        return Template('''$("#${id}").ready(function(){
                           $("#${id}").ajaxForm(function(data){
                             $("#${id}").parent().parent().parent().css("min-height", $("#${id}").parent().parent().parent().height());
                             $("#${id}").parent().slideUp("slow", function(){
                               var parent = $("#${id}").parent();
                               parent.html(data);
                               parent.slideDown("slow", function(){
                                 parent.parent().parent().css("min-height",0);
                               });
                             });
                           }); });''').safe_substitute({'id':self.id})



class PhoneNumberAddForm(ContactFieldAddForm):
    """A form for adding phone numbers to a contact."""

    template = ViewPageTemplateFile('templates/addPhoneNumberForm.pt')
    label = u'Add a Phone Number.'
    id = "zcontact-PhoneNumberAddForm"

    fields = field.Fields(interfaces.IPhoneNumber)
    factory = contact.PhoneNumber

    def updateWidgets(self):
        super(PhoneNumberAddForm, self).updateWidgets()
        for key in ['areaCode','countryCode','number']:
            self.widgets[key].css = None
        self.widgets['areaCode'].size = 1
        self.widgets['countryCode'].size = 1
        self.widgets['number'].size = 9


class AddressAddForm(ContactFieldAddForm):
    """A form for adding phone numbers to a contact."""

    label = u'Add an Address.'
    id = "zcontact-AddressAddForm"

    fields = field.Fields(interfaces.IAddress).select('title',
                                                      'address1',
                                                      'address2',
                                                      'city',
                                                      'state',
                                                      'postalCode',
                                                      'country',
                                                      'alternate')
    factory = contact.Address

    def updateWidgets(self):
        super(AddressAddForm, self).updateWidgets()
        for key in ['title', 'address1','address2','city','state','postalCode','country']:
            self.widgets[key].css = None
            self.widgets[key].size = 40


class EmailAddressAddForm(ContactFieldAddForm):
    """A form for adding email addresses to a contact."""

    label = u'Add an Email Address.'
    id = "zcontact-EmailAddressAddForm"

    fields = field.Fields(interfaces.IEmailAddress)
    factory = contact.EmailAddress


class NoteAddForm(ContactFieldAddForm):
    """A form for adding notes to a contact."""

    label = u'Add a Note.'
    id = "zcontact-NoteAddForm"

    fields = field.Fields(interfaces.IExtra)
    factory = contact.Extra


class WebsiteAddForm(ContactFieldAddForm):
    """A form for adding phone numbers to a contact."""

    label = u'Add a Website.'
    id = "zcontact-WebsiteAddForm"

    fields = field.Fields(interfaces.IWebsite)
    factory = contact.Website

    def updateWidgets(self):
        super(WebsiteAddForm, self).updateWidgets()
        for key in ['title', 'url']:
            self.widgets[key].css = None
            self.widgets[key].size = 40

### ================ INLINE FIELD VIEWS ================

class ContactFieldInlineView(form.EditForm):
    """Browser View for inline address page."""
    form.extends(form.EditForm)
    deleted = False
    editing = False
    content = '' #content to be displayed

    @property
    def prefix(self):
        if self.deleted:
            return 'deleted' #don't try to look up non-existent parents
        result = str('-'.join([s.__name__
                               for s in reversed([self.context]+getParents(self.context))
                               if s.__name__][-3:]))
        return str(hash(result))

    id = prefix

    @property
    def action(self):
        if IZContactNoScriptBrowserLayer.providedBy(self.request):
            return '.'#absoluteURL(self.context.__parent__.__parent__, self.request)
        return absoluteURL(self, self.request)

    @property
    def availableActions(self):
        #XXX: this is kind of a lowsy way to do this...
        if self.editing:
            return [self.actions['apply']]
        else:
            return [a for a in self.actions.values() if a.__name__ != 'apply']

    @button.buttonAndHandler(u'Edit', name='editsubmit')
    def handleEdit(self, action):
        self.editing = True

    @button.buttonAndHandler(u'Remove', name='removesubmit')
    def handleRemove(self, action):
        fieldContainer = self.context.__parent__
        del fieldContainer[self.context.__name__]
        self.deleted = True
        if IZContactNoScriptBrowserLayer.providedBy(self.request):
            self.request.response.redirect(absoluteURL(fieldContainer.__parent__, self.request))

    def javascript(self):
        if IZContactNoScriptBrowserLayer.providedBy(self.request):
            return ""
        return Template('''$("#${id}").ready(function(){
                           $("#${id}").ajaxForm(function(data){
                             $("#${id}").parent().parent().parent().css("min-height", $("#${id}").parent().parent().parent().height());
                             $("#${id}").parent().slideUp("slow", function(){
                               $("#${id}").parent().html(data);
                               $("#${id}").parent().slideDown("slow", function(){
                                 $("#${id}").parent().parent().parent().css("min-height",0);
                               });
                             });
                           }); });''').safe_substitute({'id':self.id})


class AddressInlineView(ContactFieldInlineView):
    """Browser View for inline address page."""

    fields = field.Fields(interfaces.IAddress)

    def googleMapsLink(self):
        searchStr = (self.context.address1 or '').strip()
        searchStr += ' '+(self.context.address2 or '').strip()
        searchStr += ' '+(self.context.city or '').strip()
        searchStr += ' '+(self.context.state or '').strip()
        searchStr += ' '+(self.context.postalCode or '').strip()
        searchStr += ' '+(self.context.country or '').strip()
        searchStr = searchStr.replace(' ', '+')
        link = "http://maps.google.com/maps?f=q&hl=en&q=%s" % searchStr
        return link


class EmailAddressInlineView(ContactFieldInlineView):
    """Browser View for inline email address page."""

    fields = field.Fields(interfaces.IEmailAddress)

    @property
    def content(self):
        address = self.context.address
        return '<a href="mailto:%s">%s</a>' % (address, address)


class PhoneNumberInlineView(ContactFieldInlineView):
    """Browser View for inline phone number page."""

    fields = field.Fields(interfaces.IPhoneNumber)

    @property
    def content(self):
        result = ""
        if self.context.countryCode:
            result += "+%s " % self.context.countryCode
        if self.context.areaCode:
            result += "(%s) " % self.context.areaCode
        result += self.context.number
        if self.context.alternate:
            result += "<i>%s</i>" % self.context.alternate
        return result


class WebsiteInlineView(ContactFieldInlineView):
    """Browser View for inline website page."""

    fields = field.Fields(interfaces.IWebsite)

    @property
    def content(self):
        url = self.context.url
        return '<a href="%s">%s</a>' % (url, url)

class NoteInlineView(ContactFieldInlineView):
    """Browser View for inline note page."""

    fields = field.Fields(interfaces.IExtra)

    @property
    def content(self):
        return self.context.info


class ContactAddForm(form.AddForm):
    """ A sample add form."""

    template = None
    layout = None
    contentName = None
    label = u'Add a Contact'
    id = "zcontact-ContactAddForm"

    fields = field.Fields(interfaces.IContact).select('title',
                                                      'description')

    def create(self, data):
        obj = contact.Contact(data['title'])
        obj.description = data['description']
        return obj

    def add(self, object):
        #strip non-alphabet characters from title to use for name.
        name = filter(lambda a: a.isalpha(), object.title)
        name = INameChooser(self.context).chooseName(name, object)
        self.context[name] = object
        return object

    def nextURL(self):
        return absoluteURL(self.context, self.request)


class ContactAddFormPage(layout.FormLayoutSupport, ContactAddForm):
    """add form with layout support."""

class ContactRemoveForm(form.Form):
    """Form for removing a contact."""
    layout = None
    contentName = None
    fields = field.Fields()
    action = ''

    _delete = False

    @property
    def label(self):
        return u'Confirm Removal of Contact %s' % self.context.title

    @property
    def prefix(self):
        return str(self.context.__name__)

    @button.buttonAndHandler(u'Remove Contact', name='removesubmit')
    def removeContactHandler(self, action):
        parent = self.context.__parent__
        del parent[self.context.__name__]
        self.request.response.redirect(absoluteURL(parent, self.request))

    @button.buttonAndHandler(u'Cancel', name='cancelsubmit')
    def cancelHandler(self, action):
        self.request.response.redirect(absoluteURL(self.context, self.request))


class ContactRemoveFormPage(layout.FormLayoutSupport, ContactRemoveForm):
    """Remove form with layout support."""

class ContactEditForm(form.EditForm):
    """Form for removing a contact."""
    fields = field.Fields(interfaces.IContact).select('title','description')
    action = ''

    @property
    def label(self):
        return u'Edit Contact %s' % self.context.title

    @property
    def prefix(self):
        return str(self.context.__name__)

    @button.buttonAndHandler(u'Cancel', name='cancel')
    def handleCancel(self, action):
        self.request.response.redirect(absoluteURL(self.context, self.request))

    @button.buttonAndHandler(u'Apply', name='apply')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        if changes:
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage
        self.request.response.redirect(absoluteURL(self.context, self.request))


class ContactEditFormPage(layout.FormLayoutSupport, ContactEditForm):
    """Edit form with layout support."""


class ContactInlineForm(form.Form):
    """ A Contact Inline Display/Edit Form. """
    template = ViewPageTemplateFile("templates/inlinecontact.pt")
    contentName = None
    label = u''
    fields = field.Fields(interfaces.IContact, mode=DISPLAY_MODE).select('title','description')

    @property
    def action(self):
        return absoluteURL(self, self.request)

    @button.buttonAndHandler(u'Delete Contact', name='removesubmit')
    def handleRemove(self, action):
        self.request.response.redirect(absoluteURL(self.context, self.request)+'/@@removeContact.html')

    @button.buttonAndHandler(u'Edit Contact', name='editsubmit')
    def handleEdit(self, action):
        self.request.response.redirect(absoluteURL(self.context, self.request)+'/@@editContact.html')

    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.mode = DISPLAY_MODE
        self.widgets.update()

    @property
    def subitems(self):
        for key in self.context.keys():
            yield self.context[key]


class ContactForm(layout.FormLayoutSupport, ContactInlineForm):
    """ A contact Display/Edit Form. """

    @property
    def label(self):
        return self.context.title

class ContactFieldContainerInlineForm(form.Form):
    """ A contact field container inline form. """

    layout = None
    contentName = None
    label = u''
    fields = field.Fields()
    action = '.'

    showAddForm = False

    addButton = jsaction.JSButton(title=u'Add')
    addButton.__name__ = 'add'
    buttons = button.Buttons(addButton)

    @property
    def prefix(self):
        return str(self.context.__name__)

    @button.buttonAndHandler(u'Add', name='addsubmit')
    def addSubmithandler(self, action):
        self.showAddForm = True

    @jsaction.handler(addButton)
    def addJSHandler(self, event, selector):
        return Template('''$.get("${url}/@@add.html",
                    function(data){
                      $("#${prefix}-newdata").after("<div></div>");
                      $("#${prefix}-newdata").next().hide();
                      $("#${prefix}-newdata").next().html(data);
                      $("#${prefix}-newdata").next().slideDown("slow");
                    });
        ''').safe_substitute({'url': absoluteURL(self.context, self.request),
                              'prefix':self.prefix})

ZContactJavaScriptViewlet = JavaScriptViewlet('zcontact.js')
