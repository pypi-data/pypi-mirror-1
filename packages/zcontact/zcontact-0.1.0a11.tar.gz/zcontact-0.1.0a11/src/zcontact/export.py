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
import cStringIO
import csv

from zope.component import adapts
from zope.interface import implements

import interfaces


class CSVContactsExporter(object):
    """export a contact list into a csv format."""
    adapts(interfaces.IContactContainer)
    implements(interfaces.ICSVExportable)

    def __init__(self, context):
        self.context = context

    def export(self):
        rows = []
        for contact in sorted(self.context.values(), lambda a,b: cmp(a.title, b.title)):
            rows.append([contact.title,])
            for fieldContainer in contact.values():
                fields = list(fieldContainer.values())
                if len(fields) > 0:
                    field = fields[0]
                    rows.append(['', fieldContainer.title, field.title or u'', unicode(field)])
                for field in fields[1:]:
                    rows.append(['', '', field.title or u'', unicode(field)])

        for row in xrange(len(rows)):
            for col in xrange(len(rows[row])):
                rows[row][col] = unicode(rows[row][col]).encode("utf-8")

        outputFile = cStringIO.StringIO()
        writer = csv.writer(outputFile)
        writer.writerows(rows)
        outputFile.seek(0)
        return outputFile.read()


class VCardPropertyBaseExporter(object):

    groupingPrefix = ''
    propertyName = ''

    def __init__(self, context):
        self.context = context

    @property
    def propertyValue(self):
        return unicode(self.context)

    def export(self):
        if self.context.title:
            self.groupingPrefix = '%s%s.' % (self.context.__parent__.__name__,
                                             self.context.__name__.replace('.',''))
            note = '%sNOTE:%s\n' % (self.groupingPrefix, self.context.title)
        else:
            note = ''
        return '%s%s:%s\n%s' % (self.groupingPrefix,
                                self.propertyName,
                                self.propertyValue,
                                note)


class VCardAddressExporter(VCardPropertyBaseExporter):
    """Export a contacts address to the appropriate vCard format."""
    adapts(interfaces.IAddress)
    implements(interfaces.IVCardExportable)

    propertyName = 'ADR'

    @property
    def propertyValue(self):
        return ';'.join([self.context.address1 or '',
                         '', #skip "Extended Address" See vCard2.1 spec
                         self.context.address2 or '',
                         self.context.city or '',
                         self.context.state or '',
                         self.context.postalCode or '',
                         self.context.country or ''])


class VCardPhoneNumberExporter(VCardPropertyBaseExporter):
    """Export a contacts address to the appropriate vCard format."""
    adapts(interfaces.IPhoneNumber)
    implements(interfaces.IVCardExportable)

    propertyName = 'TEL'


class VCardEmailAddressExporter(VCardPropertyBaseExporter):
    """Export a contacts address to the appropriate vCard format."""
    adapts(interfaces.IEmailAddress)
    implements(interfaces.IVCardExportable)

    propertyName = 'EMAIL'


class VCardWebsiteExporter(VCardPropertyBaseExporter):
    """Export a contacts address to the appropriate vCard format."""
    adapts(interfaces.IWebsite)
    implements(interfaces.IVCardExportable)

    propertyName = 'URL'


class VCardNoteExporter(VCardPropertyBaseExporter):
    """Export a contacts address to the appropriate vCard format."""
    adapts(interfaces.IExtra)
    implements(interfaces.IVCardExportable)

    propertyName = 'NOTE'

    @property
    def propertyValue(self):
        return unicode(self.context).replace('\n','=0D=0A=')


class VCardFieldContainerExporter(object):
    """Export a whole set of fields in the vCard format."""
    adapts(interfaces.IContactFieldContainer)
    implements(interfaces.IVCardExportable)

    def __init__(self, context):
        self.context = context

    def export(self):
        return ''.join([interfaces.IVCardExportable(item).export()
                        for item in self.context.values()])


class VCardContactExporter(object):
    """Export a whole contact in the vCard format."""
    adapts(interfaces.IContact)
    implements(interfaces.IVCardExportable)

    def __init__(self, context):
        self.context = context

    def export(self):
        body = ''.join([interfaces.IVCardExportable(item).export()
                        for item in self.context.values()])
        return 'BEGIN:VCARD\nN:%s\n%sEND:VCARD' % (self.context.title, body)

class VCardContactContainerExporter(object):
    """Export a whole set of contact in the vCard format."""
    adapts(interfaces.IContactContainer)
    implements(interfaces.IVCardExportable)

    def __init__(self, context):
        self.context = context

    def export(self):
        return '\n'.join([interfaces.IVCardExportable(item).export()
                          for item in self.context.values()])
