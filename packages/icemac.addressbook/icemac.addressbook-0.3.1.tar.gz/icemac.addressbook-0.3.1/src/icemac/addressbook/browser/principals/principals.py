# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt
# $Id: principals.py 1079 2009-03-23 20:52:14Z mac $

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.browser.base
import icemac.addressbook.browser.table
import icemac.addressbook.principals.interfaces
import icemac.addressbook.principals.principals
import transaction
import z3c.form.button
import z3c.form.field
import z3c.pagelet.browser
import z3c.table.table
import z3c.table.value
import zope.app.authentication.principalfolder
import zope.interface
import zope.schema
import zope.schema.interfaces
import zope.security
import zope.traversing.browser.interfaces

class Overview(z3c.pagelet.browser.BrowserPagelet,
               icemac.addressbook.browser.table.Table):

    no_rows_message = _(
        u'No users defined yet or you are not allowed to access any.')

    update = icemac.addressbook.browser.table.Table.update

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, icemac.addressbook.browser.table.TitleLinkColumn,
                'user', weight=1),
            z3c.table.column.addColumn(
                self, z3c.table.column.GetAttrColumn, 'login', weight=2,
                header=_(u'Login'), attrName='login'),
            z3c.table.column.addColumn(
                self, icemac.addressbook.browser.table.TruncatedContentColumn,
                'notes', weight=3,
                header=_(u'Notes'), attrName='description', length=50),
            ]

    @property
    def values(self):
        for principal in self.context.values():
            if zope.security.canAccess(principal, 'login'):
                yield principal


class PersonFieldDataManager(z3c.form.datamanager.AttributeField):
    """Person is a readonly field which should be written once."""

    zope.component.adapts(
        icemac.addressbook.principals.interfaces.IPrincipal,
        zope.schema.interfaces.IChoice)

    def set(self, value):
        if self.context.person is not None:
            # was already set --> get error message from parent class
            super(PersonFieldDataManager, self).set(value)
        self.context.person = value


class AddForm(icemac.addressbook.browser.base.BaseAddForm):

    label = _(u'Add new user')
    class_ = icemac.addressbook.principals.principals.Principal
    next_url = 'parent'
    fields = (
        z3c.form.field.Fields(
            icemac.addressbook.principals.interfaces.IPrincipal).select(
            'person')
        +
        z3c.form.field.Fields(
            icemac.addressbook.principals.interfaces.IRequiredPasswordFields)
        +
        z3c.form.field.Fields(
            icemac.addressbook.principals.interfaces.IRoles)
        +
        z3c.form.field.Fields(
            icemac.addressbook.principals.interfaces.IPrincipal).omit(
            'login', 'person')
        )

    def add(self, obj):
        try:
            return super(AddForm, self).add(obj)
        except zope.container.interfaces.DuplicateIDError, e:
            transaction.doom()
            raise z3c.form.interfaces.ActionExecutionError(
                zope.interface.Invalid(_(e.args[0])))


class EditForm(icemac.addressbook.browser.base.BaseEditFormWithCancel):

    next_url = 'parent'
    fields = (
        z3c.form.field.Fields(
            icemac.addressbook.principals.interfaces.IPrincipal).select(
            'person', 'login')
        +
        z3c.form.field.Fields(
            icemac.addressbook.principals.interfaces.IPasswordFields)
        +
        z3c.form.field.Fields(
            icemac.addressbook.principals.interfaces.IRoles)
        +
        z3c.form.field.Fields(
            icemac.addressbook.principals.interfaces.IPrincipal).omit(
            'person', 'login')
        )

    @z3c.form.button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        # because we define a new action we have to duplicate the
        # existing action because otherwise we'll loose it.
        super(EditForm, self).handleApply(self, action)

    @z3c.form.button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        super(EditForm, self).handleCancel(self, action)

    @z3c.form.button.buttonAndHandler(
        _(u'Delete user'), name='delete_user',
        condition=icemac.addressbook.browser.base.can_access(
            '@@delete_user.html'))
    def handleDeleteUser(self, action):
        url = zope.component.getMultiAdapter(
            (self.context, self.request),
            zope.traversing.browser.interfaces.IAbsoluteURL)()
        self.request.response.redirect(url + '/@@delete_user.html')

    def applyChanges(self, data):
        try:
            super(EditForm, self).applyChanges(data)
        except ValueError, e:
            transaction.doom()
            raise z3c.form.interfaces.ActionExecutionError(
                zope.interface.Invalid(_(e.args[0])))


class DeleteUserForm(icemac.addressbook.browser.base.BaseDeleteForm):
    label = _(u'Do you really want to delete this user?')
    interface = icemac.addressbook.principals.interfaces.IPrincipal
    field_names = ('person', 'login')
