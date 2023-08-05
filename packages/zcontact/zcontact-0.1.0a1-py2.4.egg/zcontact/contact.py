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
import zope.interface
import zope.app.container.btree
import zope.app.container.contained
import persistent
from persistent.list import PersistentList
from zope.schema.fieldproperty import FieldProperty
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.app import container
from zope.app.component import site, hooks
from zope.interface import implements
from zope.app.authentication import authentication, session
from zope.app.authentication.interfaces import ICredentialsPlugin
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager, IRolePermissionManager
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.location.location import LocationProxy
from zope.publisher.interfaces import NotFound, IPublishTraverse
from zope.location.location import LocationProxy, locate

from zcontact import interfaces
from zcontact import person

import interfaces


class ContactFieldContainer(zope.app.container.btree.BTreeContainer):
    """The implementation for IContactFieldContainer."""

    zope.interface.implements(interfaces.IContactFieldContainer)

    title = FieldProperty(interfaces.IContactFieldContainer['title'])

    def __init__(self, title):
        super(ContactFieldContainer, self).__init__()
        self.title = title


class AddressContainer(ContactFieldContainer):
    """The interface for a contact container."""
    zope.interface.implements(interfaces.IAddressContainer)


class PhoneNumberContainer(ContactFieldContainer):
    """The interface for a contact container."""
    zope.interface.implements(interfaces.IPhoneNumberContainer)


class WebsiteContainer(ContactFieldContainer):
    """The interface for a contact container."""
    zope.interface.implements(interfaces.IWebsiteContainer)


class EmailAddressContainer(ContactFieldContainer):
    """The interface for a contact container."""
    zope.interface.implements(interfaces.IEmailAddressContainer)


class ExtraContainer(ContactFieldContainer):
    """The interface for a contact container."""
    zope.interface.implements(interfaces.IExtraContainer)


class ContactField(persistent.Persistent):
    """Implemetnation of IContactField"""
    zope.interface.implements(interfaces.IContactField)

    title = FieldProperty(interfaces.IContactField['title'])    

    def __init__(self, **kw):
        for keyword in kw:
            setattr(self, keyword, kw[keyword])


class Address(ContactField):
    """Implementation of IAddress."""
    zope.interface.implements(interfaces.IAddress)

    address1 = FieldProperty(interfaces.IAddress['address1'])
    address2 = FieldProperty(interfaces.IAddress['address2'])
    postalCode = FieldProperty(interfaces.IAddress['postalCode'])
    city = FieldProperty(interfaces.IAddress['city'])
    state = FieldProperty(interfaces.IAddress['state'])
    country = FieldProperty(interfaces.IAddress['country'])
    alternate = FieldProperty(interfaces.IAddress['alternate'])


class PhoneNumber(ContactField):
    """Implementation of IExtra."""
    zope.interface.implements(interfaces.IPhoneNumber)

    areaCode = FieldProperty(interfaces.IPhoneNumber['areaCode'])
    countryCode = FieldProperty(interfaces.IPhoneNumber['countryCode'])
    number = FieldProperty(interfaces.IPhoneNumber['number'])
    alternate = FieldProperty(interfaces.IPhoneNumber['alternate'])

class Website(ContactField):
    """Implementation of IExtra."""
    zope.interface.implements(interfaces.IWebsite)

    url = FieldProperty(interfaces.IWebsite['url'])


class EmailAddress(ContactField):
    """Implementation of IExtra."""
    zope.interface.implements(interfaces.IEmailAddress)

    address = FieldProperty(interfaces.IEmailAddress['address'])


class Extra(ContactField):
    """Implementation of IExtra."""
    zope.interface.implements(interfaces.IExtra)

    info = FieldProperty(interfaces.IExtra['info'])
    

class Contact(zope.app.container.btree.BTreeContainer):
    """Implementation of IContact"""
    zope.interface.implements(interfaces.IContact)

    title = FieldProperty(interfaces.IContact['title'])
    description = FieldProperty(interfaces.IContact['description'])

    def __init__(self, title=u""):
        super(Contact, self).__init__()
        self.title = title
        self['addresses'] = AddressContainer(u'Addresses')
        self['phoneNumbers'] = PhoneNumberContainer(u'Phone Numbers')
        self['faxNumbers'] = PhoneNumberContainer(u'Fax Numbers')
        self['emailAddresses'] = EmailAddressContainer(u'Email Addresses')
        self['websites'] = WebsiteContainer(u'Websites')
        self['extra'] = ExtraContainer(u'Extra Information')

    def __repr__(self):
        """Returns programmer representation of Contact."""
        return '<%s "%s">' % (self.__class__.__name__,
                              self.title)

class ContactApplicationSettings(zope.app.container.contained.Contained):
    """Settings Manager for Contact Application."""
    zope.interface.implements(interfaces.IContactApplicationSettings)

    _mode = FieldProperty(interfaces.IContactApplicationSettings['mode'])

    def setMode(self, mode):
        modeObj = zope.component.queryUtility(interfaces.IContactApplicationMode,
                                              name=mode)
        if modeObj is None:
            raise AttributeError(mode)
        modeObj.apply(self.__parent__)
        self._mode = mode

    mode = property(lambda self: self._mode, setMode)
        

class BaseApplicationMode(object):
    """Base class for applicaiton modes."""
    zope.interface.implements(interfaces.IContactApplicationMode)

    permissions = {}

    def _unsetAllPermissions(self, app):
        rpm = IRolePermissionManager(app)
        for permission in ['zcontact.View',
                           'zcontact.Edit',
                           'zcontact.ManageSettings',
                           'zcontact.ManageUsers',
                           'zcontact.ViewUsers']:
            for role in ['zcontact.Manager',
                         'zcontact.Member',
                         'zope.Anonymous']:
                rpm.unsetPermissionFromRole(permission, role)

    def apply(self, app):
        self._unsetAllPermissions(app)
        rpm = IRolePermissionManager(app)
        for role in self.permissions.keys():
            for permission in self.permissions[role]:
                rpm.grantPermissionToRole(permission, role)


class WikiApplicationMode(BaseApplicationMode):
    """The wiki mode for zcontact."""
    zope.interface.implements(interfaces.IContactApplicationMode)

    permissions = {'zope.Anonymous':('zcontact.View',
                                     'zcontact.Edit'),
                   'zcontact.Member':('zcontact.View',
                                      'zcontact.Edit',
                                      'zcontact.ViewUsers'),
                   'zcontact.Manager':('zcontact.View',
                                       'zcontact.Edit',
                                       'zcontact.ViewUsers',
                                       'zcontact.ManageSettings',
                                       'zcontact.ManageUsers',
                                       'zcontact.ViewUsers')
                   }


class PersonalApplicationMode(BaseApplicationMode):
    """The wiki mode for zcontact."""
    zope.interface.implements(interfaces.IContactApplicationMode)

    permissions = {'zope.Anonymous':(),
                   'zcontact.Member':('zcontact.View',
                                      'zcontact.ViewUsers'),
                   'zcontact.Manager':('zcontact.View',
                                       'zcontact.Edit',
                                       'zcontact.ViewUsers',
                                       'zcontact.ManageSettings',
                                       'zcontact.ManageUsers',
                                       'zcontact.ViewUsers')
                   }


class CommunityApplicationMode(BaseApplicationMode):
    """The wiki mode for zcontact."""
    zope.interface.implements(interfaces.IContactApplicationMode)

    permissions = {'zope.Anonymous':('zcontact.View'),
                   'zcontact.Member':('zcontact.View',
                                      'zcontact.Edit',
                                      'zcontact.ViewUsers'),
                   'zcontact.Manager':('zcontact.View',
                                       'zcontact.Edit',
                                       'zcontact.ViewUsers',
                                       'zcontact.ManageSettings',
                                       'zcontact.ManageUsers',
                                       'zcontact.ViewUsers')
                   }



class ContactApplication(zope.app.container.btree.BTreeContainer,
                         site.SiteManagerContainer):
    """Implementation of IContactContainer."""
    zope.interface.implements(interfaces.IContactApplication,
                              IPublishTraverse,
                              IAttributeAnnotatable)

    title = u''

    def __repr__(self):
        """Returns programmer representation of ContactContainer."""
        return '<%s "%s", %s contact(s)>' % (self.__class__.__name__,
                                          self.title, len(self))

    def __init__(self, title=u''):
        super(ContactApplication, self).__init__()
        self.title = title
        self.settings = ContactApplicationSettings()
        locate(self.settings, self, '+settings')
        self.users = person.PersonContainer()
        locate(self.users, self, '+users')

        # Since we want this to be a site, we need to register a site manager.
        # We want a local site manager here so we will have to create
        # one locally.
        sm = site.LocalSiteManager(self)
        self.setSiteManager(sm)

        # Next we want to set up authentication for our site.
        pau = authentication.PluggableAuthentication()
        sm['authentication'] = pau
        sm.registerUtility(pau, IAuthentication)
        # Set Up Authenticator Plugin with PrincipalContainer (self.users)
        pauUsers = LocationProxy(self.users, pau, 'users')
        pau['users'] = pauUsers
        sm.registerUtility(pauUsers, IAuthenticatorPlugin, name="Users")
        # Set up Credentials Plugin with SessionCredentialsPlugin
        pauCredentials = session.SessionCredentialsPlugin()
        pau['credentials'] = pauCredentials
        sm.registerUtility(pauCredentials, ICredentialsPlugin, name="Session Credentials")
        #make the pluggable authentication use these plugins.
        pau.authenticatorPlugins = (pauUsers.__name__,)
        pau.credentialsPlugins = ("No Challenge if Authenticated",
                                  "Session Credentials")

        #Now we will add the manager user

        self.users['manager'] = person.Person(u'manager',u'zcontact',
                                              u'Z Contact Manager',
                                              description=u"The site manager",
                                              passwordManagerName='SHA1')
        IPrincipalRoleManager(self).assignRoleToPrincipal('zcontact.Manager', 'manager')

    def __setitem__(self, key, value):
        if key.startswith('+'):
            raise ValueError("You cannot store a contact with a key that starts with '+'")
        return super(ContactApplication, self).__setitem__(key, value)

    def publishTraverse(self, request, name):
        if name.startswith('+'):
            key = name[1:]
            if hasattr(self, key):
                return LocationProxy(getattr(self, key), self, name)
        else:
            if name in self.keys():
                return self[name]
        raise NotFound(self, name, request) 

    def _newContainerData(self):
        '''to make is persistent?'''
        return PersistentDict()


def getZContactApplication(context=None):
    site = hooks.getSite()
    if interfaces.IContactApplication.providedBy(site):
        return site
    else:
        return None
