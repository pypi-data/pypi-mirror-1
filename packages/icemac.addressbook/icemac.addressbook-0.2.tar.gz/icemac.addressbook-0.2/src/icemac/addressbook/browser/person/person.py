# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: person.py 917 2009-01-02 19:34:06Z mac $

import z3c.form.button
import z3c.form.datamanager
import z3c.form.group
import zc.sourcefactory.contextual
import zope.component

import icemac.addressbook.browser.base
import icemac.addressbook.interfaces
import icemac.addressbook.person
import icemac.addressbook.sources
import icemac.addressbook.utils

from icemac.addressbook.i18n import MessageFactory as _
from icemac.addressbook.address import interface_title_prefix_class_mapping


def prefix_to_class(prefix):
    mapping = dict((x[2], x[3]) for x in interface_title_prefix_class_mapping)
    return mapping[prefix]


class AddGroup(icemac.addressbook.browser.base.PrefixGroup):
    "PrefixGroup for AddForm."

    def __init__(self, context, request, parent, interface, label, prefix):
        super(AddGroup, self).__init__(context, request, parent)
        self.interface = interface
        self.label = label
        self.prefix = prefix


class EditGroup(AddGroup):
    "PrefixGroup for EditForm."

    def __init__(
        self, context, request, parent, interface, label, prefix, index, key):
        super(EditGroup, self).__init__(
            context, request, parent, interface, label, prefix)
        self.prefix = "%s_%s" % (prefix, index)
        self.key = key

    def getContent(self):
        return self.context[self.key]

class DefaultSelectGroup(icemac.addressbook.browser.base.PrefixGroup):
    """Group to select the default addresses."""

    interface = icemac.addressbook.interfaces.IPersonDefaults
    label = _(u'main adresses and numbers')
    prefix = 'defaults'


class PersonAddForm(z3c.form.group.GroupForm,
                    icemac.addressbook.browser.base.BaseAddForm):

    label = _(u'Add new person')
    interface = icemac.addressbook.interfaces.IPerson
    next_url = 'parent'

    def __init__(self, *args, **kw):
        super(PersonAddForm, self).__init__(*args, **kw)
        context = self.context
        request = self.request
        groups = [AddGroup(context, request, self, iface, _(title), prefix)
                  for iface, title, prefix, dummy in
                      interface_title_prefix_class_mapping]
        self.groups = tuple(groups)

    def createAndAdd(self, data):
        person = icemac.addressbook.browser.base.create(
            self, icemac.addressbook.person.Person, data)
        self._name = icemac.addressbook.utils.add(self.context, person)
        for group in self.groups:
            obj = icemac.addressbook.browser.base.create(
                group, prefix_to_class(group.prefix), data)
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
    interface = icemac.addressbook.interfaces.IPerson
    next_url = 'parent'

    def __init__(self, *args, **kw):
        super(PersonEditForm, self).__init__(*args, **kw)
        groups = [DefaultSelectGroup]
        for iface, title, prefix, dummy in interface_title_prefix_class_mapping:
            index = 0
            default_obj = getattr(self.context, 'default_%s' % prefix)
            for obj in icemac.addressbook.utils.iter_by_interface(
                    self.context, iface):
                if obj == default_obj:
                    obj_title = u'main ' + title
                else:
                    obj_title = u'other ' + title
                group = EditGroup(
                    self.context, self.request, self, iface, _(obj_title),
                    prefix, index, obj.__name__)
                groups.append(group)
                index += 1
        self.groups = tuple(groups)

    @z3c.form.button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        # because we define a new action we have to duplicate the
        # existing action because otherwise we'll loose it.
        super(PersonEditForm, self).handleApply(self, action)

    @z3c.form.button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        self.status = self.noChangesMessage

    @z3c.form.button.buttonAndHandler(
        _(u'Delete person'), name='delete_person',
        condition=icemac.addressbook.browser.base.can_access(
            '@@delete_person.html'))
    def handleDeletePerson(self, action):
        url = zope.component.getMultiAdapter(
            (self.context, self.request), name="absolute_url")()
        self.request.response.redirect(url + '/@@delete_person.html')

    @z3c.form.button.buttonAndHandler(
        _(u'Delete address or number'), name='delete_address',
        condition=icemac.addressbook.browser.base.can_access(
            '@@delete_address.html'))
    def handleDeleteAddress(self, action):
        url = zope.component.getMultiAdapter(
            (self.context, self.request), name="absolute_url")()
        self.request.response.redirect(url + '/@@delete_address.html')


class KeywordDataManager(z3c.form.datamanager.AttributeField):
    """Datamanager which converts the list of keywords in the view into a
    set of keywords on the model."""

    def get(self):
        return sorted(super(KeywordDataManager, self).get(),
                      key=lambda x: x.title)

    def set(self, value):
        return super(KeywordDataManager, self).set(set(value))


class DeletePersonForm(icemac.addressbook.browser.base.BaseDeleteForm):
    label = _(u'Do you really want to delete this person?')
    interface = icemac.addressbook.interfaces.IPerson
    field_names = ('first_name', 'last_name')


class PersonEntriesSource(
    zc.sourcefactory.contextual.BasicContextualSourceFactory):
    "Source to select entries from person."

    def getValues(self, context):
        for interface, d, d, d in interface_title_prefix_class_mapping:
            for value in icemac.addressbook.sources.ContextByInterfaceSource(
                interface).factory.getValues(context):
                yield value

    def getTitle(self, context, value):
        title_prefix = icemac.addressbook.address.object_to_title(value)
        title = icemac.addressbook.interfaces.ITitle(value)
        if title_prefix:
            title = '%s -- %s' % (title_prefix, title)
        return title


class IPersonEntries(zope.interface.Interface):
    """Content entries of an object."""

    entry = zope.schema.Choice(
        title=_(u'Entries'), source=PersonEntriesSource())


class DeleteAddressForm(icemac.addressbook.browser.base.BaseEditForm):

    label = _(u'Please choose an entry for deletion:')
    interface = IPersonEntries
    ignoreContext = True
    next_url = 'object'

    @z3c.form.button.buttonAndHandler(_(u'Delete entry'), name='delete_entry')
    def handleDeleteEntry(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        selected_entry = data['entry']

        url = zope.component.getMultiAdapter(
            (selected_entry, self.request), name="absolute_url")()
        self.request.response.redirect(url + '/@@delete.html')

    @z3c.form.button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        self.status = self.noChangesMessage
