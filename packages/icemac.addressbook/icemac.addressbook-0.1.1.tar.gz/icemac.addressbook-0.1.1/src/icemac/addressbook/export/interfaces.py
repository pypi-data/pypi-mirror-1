# -*- coding: latin-1 -*-
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: interfaces.py 776 2008-11-01 14:54:11Z mac $

import zope.interface

class IExporter(zope.interface.Interface):
    """Exporting facility."""

    description = zope.interface.Attribute(
        u'Short description of the exporter.')
    file_extension = zope.interface.Attribute(
        u'Extension (without the leading dot!) to be set on export file name.')
    mime_type = zope.interface.Attribute(u'Mime-type of the export file.')

    def export(*persons):
        """Export the `persons` to a file.

        Returns a file or file-like-object.

        """
