# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.browser.base
import icemac.addressbook.browser.interfaces
import icemac.addressbook.file.file
import icemac.addressbook.file.interfaces
import os.path
import z3c.form.field
import z3c.form.interfaces
import z3c.form.validator
import z3c.form.widget
import zope.component
import zope.mimetype.interfaces
import zope.security.proxy


def cleanup_filename(filename):
    if filename is None:
        return _('<no name>')
    return filename.split('\\')[-1].split('/')[-1]


def update_blob(widget, file):
    """Update the mime type of the file.

    widget ... file upload widget
    file ... IFile instance to set the mime type on

    """
    if not widget.value:
        # no file uploaded
        return

    # At first we should try to replace the blob file with the one
    # uploaded, as this does not require reading and copying the file.
    # Zope stores the path to the file in the FileUpload in the `name`
    # attribute, but in tests it is stored in `filename` attribute, so
    # we have to differentiate.
    file_name = getattr(widget.value, 'name', widget.value.filename)

    if os.path.exists(file_name):
        # If the file exists, use it.
        file.replace(file_name)
    else:
        # If not (python stores small files in a StringIO instead of a
        # real file on hard disk) update the contents.
        widget.value.seek(0)
        file.data = widget.value.read()

    # get a sample of the file contents for fingerprinting
    fd = zope.security.proxy.removeSecurityProxy(file.open())
    data = fd.read(100)
    fd.close()

    content_type = widget.headers.get('Content-Type')
    mime_type_getter = zope.component.getUtility(
        zope.mimetype.interfaces.IMimeTypeGetter)
    mime_type = mime_type_getter(data=data, content_type=content_type,
                                 name=cleanup_filename(widget.filename))
    if not mime_type:
        mime_type = 'application/octet-stream'
    file.mimeType = mime_type


class Add(icemac.addressbook.browser.base.BaseAddForm):
    "Add a file."

    class_ = icemac.addressbook.file.file.File
    next_url = 'parent'

    @property
    def fields(self):
        fields = z3c.form.field.Fields(
            icemac.addressbook.file.interfaces.IFile).select('data', 'notes')
        return fields

    def create(self, data):
        file = super(Add, self).create(data)
        file_widget = self.widgets['data']
        file.name = cleanup_filename(file_widget.filename)
        update_blob(file_widget, file)
        return file

# in the Add form file upload is required ...
IFile_data_required = z3c.form.widget.StaticWidgetAttribute(
    True, context=None, request=None, view=Add,
    field=icemac.addressbook.file.interfaces.IFile['data'], widget=None)

# ... but not in all other forms
IFile_data_not_required = z3c.form.widget.StaticWidgetAttribute(
    False, context=icemac.addressbook.file.interfaces.IFile,
    request=None, view=None,
    field=icemac.addressbook.file.interfaces.IFile['data'], widget=None)


class AddForm_data_Field_Validator(z3c.form.validator.SimpleFieldValidator):
    """Validator for data field in add form."""

    zope.component.adapts(
        None, icemac.addressbook.browser.interfaces.IAddressBookLayer,
        Add, zope.schema.Bytes, z3c.form.interfaces.IFileWidget)

    def validate(self, value):
        if value is z3c.form.interfaces.NOT_CHANGED:
            # no file uploaded --> tread as missing value
            value = self.field.missing_value
        return super(AddForm_data_Field_Validator, self).validate(value)


class EditForm_data_Field_Validator(z3c.form.validator.SimpleFieldValidator):
    """Validator for data field in add form."""

    zope.component.adapts(
        None, None, None, zope.schema.Bytes, z3c.form.interfaces.IFileWidget)

    def validate(self, value):
        if value is z3c.form.interfaces.NOT_CHANGED:
            # no file uploaded --> last upload has already been validated
            return
        return super(EditForm_data_Field_Validator, self).validate(value)


class DeleteFileForm(icemac.addressbook.browser.base.BaseDeleteForm):

    next_url = 'parent'
    label = _(u'Do you really want to delete this file?')
    interface = icemac.addressbook.file.interfaces.IFile
    field_names = ('name', 'notes')
