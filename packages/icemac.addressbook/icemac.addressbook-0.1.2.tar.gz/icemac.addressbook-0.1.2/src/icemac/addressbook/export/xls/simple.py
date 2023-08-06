# -*- coding: latin-1 -*-
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: simple.py 776 2008-11-01 14:54:11Z mac $

import datetime
import xlwt
import zope.interface

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import icemac.addressbook.export.interfaces
import icemac.addressbook.interfaces

from icemac.addressbook.i18n import MessageFactory as _

# fonts
head_font = xlwt.Font()
head_font.name = 'Courier'

group_font = xlwt.Font()
group_font.name = 'Courier'
group_font.bold = True

# styles
default_style = xlwt.XFStyle()

head_style = xlwt.XFStyle()
head_style.font = head_font

group_style = xlwt.XFStyle()
group_style.font = group_font

date_style = xlwt.XFStyle()
date_style.num_format_str = 'DD.MM.YY'


value_style_mapping = {
    datetime.date: date_style
    }


class DefaultsExport(object):
    
    zope.interface.implements(icemac.addressbook.export.interfaces.IExporter)

    description = _(u'Export persons data, the default postal address, email '
                    u'addres, home page and phone number.')
    file_extension = 'xls'
    mime_type = 'application/vnd.ms-excel'

    def export(self, *persons):
        self.persons = persons

        wb = xlwt.Workbook()
        self.sheet = wb.add_sheet(_(u'Address book - Export'))
        self.col = 0

        self.write_block(icemac.addressbook.interfaces.IPerson, lambda x:x, 
                         _('Person'))
        self.write_block(icemac.addressbook.interfaces.IPostalAddress,
                         lambda x:x.default_postal_address, _('Postal address'))
        self.write_block(icemac.addressbook.interfaces.IEMailAddress,
                         lambda x:x.default_email_address, _('E-Mail address'))
        self.write_block(icemac.addressbook.interfaces.IHomePageAddress,
                         lambda x:x.default_home_page_address, 
                         _('Home page address'))
        self.write_block(icemac.addressbook.interfaces.IPhoneNumber,
                         lambda x:x.default_phone_number, _('Phone number'))

        io = StringIO()
        wb.save(io)
        return io.getvalue()

    def write_block(self, interface, obj_getter, headline):
        self.sheet.write(0, self.col, headline, group_style)
        for name, field in zope.schema.getFieldsInOrder(interface):
            self.sheet.write(1, self.col, field.title, head_style)
            row = 2
            for person in self.persons:
                obj = obj_getter(person)
                if obj is None:
                    value = None
                else:
                    value = getattr(obj, name)
                style = value_style_mapping.get(value.__class__, default_style)
                self.sheet.write(row, self.col, convert_value(value), style)
                row += 1
            self.col += 1
        

def convert_value(value):
    """Convert the value for xls export."""
    if value is None:
        return value
    if value.__class__ in (str, unicode, float, int, datetime.date):
        return value
    if hasattr(value, '__iter__'):
        return ', '.join(convert_value(v) for v in value)
    return icemac.addressbook.interfaces.ITitle(value)
