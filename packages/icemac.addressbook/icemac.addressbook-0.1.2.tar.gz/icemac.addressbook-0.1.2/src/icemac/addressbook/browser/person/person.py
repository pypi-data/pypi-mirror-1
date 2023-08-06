# -*- coding: latin-1 -*-
# Copyright (c) 2008 Michael Howitz
# See also LICENSE.txt
# $Id: person.py 753 2008-10-24 18:11:39Z mac $

import z3c.form.button
import z3c.form.datamanager
import z3c.form.group
import zope.component

import icemac.addressbook.address
import icemac.addressbook.browser.base
import icemac.addressbook.interfaces
import icemac.addressbook.person
import icemac.addressbook.utils
from icemac.addressbook.i18n import MessageFactory as _


class DefaultEditGroup(object):

    def getContent(self):
        return getattr(self.context, 'default_' + self.prefix)


class PostalAddressGroupAdd(icemac.addressbook.browser.base.PrefixGroup):
    label = _(u'Postal address')
    prefix = 'postal_address'
    interface = icemac.addressbook.interfaces.IPostalAddress


class PostalAddressGroupEdit(DefaultEditGroup, PostalAddressGroupAdd):
    pass


class EMailAddressGroupAdd(icemac.addressbook.browser.base.PrefixGroup):
    label = _(u'E-Mail address')
    prefix = 'email_address'
    interface = icemac.addressbook.interfaces.IEMailAddress


class EMailAddressGroupEdit(DefaultEditGroup, EMailAddressGroupAdd):
    pass


class HomePageAddressGroupAdd(icemac.addressbook.browser.base.PrefixGroup):
    label = _(u'Home page address')
    prefix = 'home_page_address'
    interface = icemac.addressbook.interfaces.IHomePageAddress


class HomePageAddressGroupEdit(DefaultEditGroup, HomePageAddressGroupAdd):
    pass


class PhoneNumberGroupAdd(icemac.addressbook.browser.base.PrefixGroup):
    label = _(u'Phone number')
    prefix = 'phone_number'
    interface = icemac.addressbook.interfaces.IPhoneNumber


class PhoneNumberGroupEdit(DefaultEditGroup, PhoneNumberGroupAdd):
    pass


class PersonAddForm(z3c.form.group.GroupForm,
                    icemac.addressbook.browser.base.BaseAddForm):

    label = _(u'Add new person')
    interface = icemac.addressbook.interfaces.IPerson
    groups = (PostalAddressGroupAdd, EMailAddressGroupAdd, 
              HomePageAddressGroupAdd, PhoneNumberGroupAdd)
    next_url = 'parent'
    prefix_class_map = dict(
        postal_address=icemac.addressbook.address.PostalAddress,
        email_address=icemac.addressbook.address.EMailAddress,
        home_page_address=icemac.addressbook.address.HomePageAddress,
        phone_number=icemac.addressbook.address.PhoneNumber,
        )

    def createAndAdd(self, data):
        person = icemac.addressbook.browser.base.create(
            self, icemac.addressbook.person.Person, data)
        self._name = icemac.addressbook.utils.add(self.context, person)
        for group in self.groups:
            obj = icemac.addressbook.browser.base.create(
                group, self.prefix_class_map[group.prefix], data)
            icemac.addressbook.utils.add(person, obj)
            # handling of default addresses: the first address is
            # saved as default
            default_attrib = 'default_%s' % group.prefix
            if getattr(person, default_attrib, None) is None:
                setattr(person, default_attrib, obj)
        return person

class PersonEditForm(
    z3c.form.group.GroupForm, icemac.addressbook.browser.base.BaseEditForm):

    label = _(u'Edit person data')
    groups = (PostalAddressGroupEdit, EMailAddressGroupEdit, 
              HomePageAddressGroupEdit, PhoneNumberGroupEdit)
    interface = icemac.addressbook.interfaces.IPerson
    next_url = 'parent'

    @z3c.form.button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        # because we define a new action we have to duplicate the
        # existing action because otherwise we'll loose it.
        super(PersonEditForm, self).handleApply(self, action)

    @z3c.form.button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        self.status = self.noChangesMessage

    @z3c.form.button.buttonAndHandler(
        _(u'Delete'), name='delete',
        condition=icemac.addressbook.browser.base.can_access('@@delete.html'))
    def handleDelete(self, action):
        url = zope.component.getMultiAdapter(
            (self.context, self.request), name="absolute_url")()
        self.request.response.redirect(url + '/@@delete.html')


class DeleteForm(icemac.addressbook.browser.base.BaseDeleteForm):
    label = _(u'Do you really want to delete this person?')
    interface = icemac.addressbook.interfaces.IPerson
    field_names = ('first_name', 'last_name')


class KeywordDataManager(z3c.form.datamanager.AttributeField):
    """Datamanager which converts the list of keywords in the view into a
    set of keywords on the model."""

    def get(self):
        return sorted(super(KeywordDataManager, self).get(),
                      key=lambda x: x.title)

    def set(self, value):
        return super(KeywordDataManager, self).set(set(value))
