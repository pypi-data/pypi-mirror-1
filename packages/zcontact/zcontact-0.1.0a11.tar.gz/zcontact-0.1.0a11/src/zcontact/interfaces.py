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
import os.path
import zope.interface
import zope.schema
import zope.publisher.interfaces.browser
from zope.app.container.interfaces import IContainer
from zope.app.container.interfaces import IContained
from zope.app.component.interfaces import IPossibleSite
from zope.app.authentication.principalfolder import IInternalPrincipal
from zope.app.container.constraints import contains, containers

class IPerson(IInternalPrincipal):
    """A Person object and principal"""

class IPersonContainer(zope.app.container.interfaces.IContainer):
    """A container for people"""
    contains(IPerson)

class IPersonContained(IContained):
    """A Person contained in a IPersonContainer"""
    containers(IPersonContainer)


class IContactField(zope.interface.Interface):

    title = zope.schema.TextLine(
        title=u"Title",
        required=False)

    def __unicode__():
        """Returns a unicode represetation of the field.

        for example, a phone number field with multiple attributes
        like area code, country code, etc would present it as. +34 (523)-331-2312.
        """


class IContactFieldContainer(zope.app.container.interfaces.IContainer):
    """The interface for a container of contact fields."""

    title = zope.schema.TextLine(
        title=u"Title",
        required=True)


class IAddressContainer(IContactFieldContainer):
    """The interface for a contact container."""


class IPhoneNumberContainer(IContactFieldContainer):
    """The interface for a contact container."""


class IWebsiteContainer(IContactFieldContainer):
    """The interface for a contact container."""


class IEmailAddressContainer(IContactFieldContainer):
    """The interface for a contact container."""


class IExtraContainer(IContactFieldContainer):
    """The interface for a contact container."""


class IAddress(IContactField):
    """The interface for an address."""

    address1 = zope.schema.TextLine(
        title=u"Address 1",
        required=False)

    address2 = zope.schema.TextLine(
        title=u"Address 2",
        required=False)

    postalCode = zope.schema.TextLine(
        title=u"Postal/Zip Code",
        required=False)

    city = zope.schema.TextLine(
        title=u"City",
        required=False)

    state = zope.schema.TextLine(
        title=u"State/Provence",
        required=False)

    country = zope.schema.TextLine(
        title=u"Country",
        required=False)

    alternate = zope.schema.Text(
        title=u"Arbitrary Address Form",
        required=False)


class IPhoneNumber(IContactField):
    """The interface for a phone number."""

    countryCode = zope.schema.TextLine(
        title=u"Country Code",
         required=False,
        default=u"1")

    areaCode = zope.schema.TextLine(
        title=u"Area Code",
        required=False)

    number = zope.schema.TextLine(
        title=u"Number",
        required=False)

    alternate = zope.schema.TextLine(
        title=u"Arbitrary Phone Number Form",
        required=False)


class IWebsite(IContactField):

    url = zope.schema.ASCIILine(
        title=u"URL",
        default="http://",
        required=False)


class IEmailAddress(IContactField):

    address = zope.schema.ASCIILine(
        title=u"Address",
        required=False)


class IExtra(IContactField):

    info = zope.schema.Text(
        title=u"Notes",
        required = False)


class IContact(zope.app.container.interfaces.IContainer):
    """The interface for a contact."""

    title = zope.schema.TextLine(
        title=u"Title",
        description=u"Title for the Contact",
        required=True,
        default=u"")

    description = zope.schema.Text(
        title=u"Description",
        required=False)

    contains(IContactField)


class IContactContainer(zope.app.container.interfaces.IContainer):
    """The interface for something that contains contacts."""

    contains(IContact)


class IContactApplicationSettings(zope.interface.Interface):
    """The Settings manager for Z Contact."""

    mode = zope.schema.Choice(
        title=u"Mode",
        description=u"The overall mode of Z Contact.",
        required=True,
        values=['Wiki','Personal','Community'],
        default='Personal')


class IContactApplication(zope.app.container.interfaces.IContainer, IPossibleSite):
    """The interface for a contact container."""

    title = zope.schema.TextLine(
        title=u"Title",
        description=u"Title for the container of Contacts.",
        default=u"Z Contact",
        required=True)

class IContactApplicationMode(zope.interface.Interface):
    """A overall mode for the application."""

    permissions = zope.schema.Dict(
        title=u"Permissions Mapping",
        required=True)

    def apply(app):
        """Apply the mode to the given applicaiton."""

class IZContactSkin(zope.publisher.interfaces.browser.IDefaultBrowserLayer):
    """The ZContact skin."""


class IExportable(zope.interface.Interface):
    """Something that can be exported."""

    def export():
        """export object to some text based data format."""

class ICSVExportable(IExportable):
    """Exporter for the VCard format."""

class IVCardExportable(IExportable):
    """Exporter for the VCard format."""
