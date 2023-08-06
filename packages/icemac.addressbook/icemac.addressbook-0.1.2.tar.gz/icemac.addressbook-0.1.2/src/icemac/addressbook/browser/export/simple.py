# -*- coding: utf-8 -*-
# Copyright (c) 2008 Michael Howitz
# See also LICENSE.txt
# $Id: simple.py 776 2008-11-01 14:54:11Z mac $

import icemac.addressbook.export.xls.simple


class SimpleExport(object):

    def __call__(self):
        person_ids = self.request.form['persons']
        persons = [self.context[id] for id in person_ids]
        exporter = icemac.addressbook.export.xls.simple.DefaultsExport()

        self.request.response.setHeader('Content-Type', exporter.mime_type)
        self.request.response.setHeader(
            'Content-Disposition', 
            'attachment; filename=addressbook_export.%s' % (
                exporter.file_extension))

        return exporter.export(*persons)
