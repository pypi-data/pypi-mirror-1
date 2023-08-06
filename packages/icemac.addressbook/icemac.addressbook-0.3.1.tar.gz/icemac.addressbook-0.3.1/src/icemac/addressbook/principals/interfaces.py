# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt
# $Id: interfaces.py 1061 2009-03-19 21:09:55Z mac $

import copy
import zope.interface
import zope.schema

import icemac.addressbook.principals.sources

from icemac.addressbook.i18n import MessageFactory as _


class IRequiredPasswordFields(zope.interface.Interface):
    """Required password fields to enter and check password."""

    password = zope.schema.Password(
        title=_(u'Password'), min_length=8,
        description=_(u'The password for the user.'))

    password_repetition = zope.schema.Password(
        title=_(u'Password repetition'), min_length=8,
        description=_(u'Please repeat the password.'))

    @zope.interface.invariant
    def password_eq_repetition(obj):
        if obj.password != obj.password_repetition:
            raise zope.interface.Invalid(
                _(u'Entry in password field was not equal to entry in password '
                  u'repetition field.'))


class IPasswordFields(IRequiredPasswordFields):
    """Not-required Password fields to enter and check password."""

    password = copy.copy(IRequiredPasswordFields['password'])
    password_repetition = copy.copy(
        IRequiredPasswordFields['password_repetition'])

IPasswordFields['password'].required = False
IPasswordFields['password_repetition'].required = False


class IPrincipal(zope.interface.Interface):
    "Derived from zope.app.authentication.principalfolder.IInternalPrincipal."

    person = zope.schema.Choice(
        title=_(u'Person'), readonly=True,
        source=icemac.addressbook.principals.sources.persons)

    login = zope.schema.TextLine(
        title=_(u'Login'),
        description=_(u'The Login/Username of the user. '
                      u'This value can change.'))

    description = zope.schema.Text(
        title=_('Notes'),
        description=_('Provides notes for the user.'),
        required=False, missing_value='', default=u'')


class IRoles(zope.interface.Interface):
    "Roles"

    roles = zope.schema.Tuple(
        title=_(u'Roles'), required=False,
        value_type=zope.schema.Choice(
            source=icemac.addressbook.principals.sources.role_source))


class IRoot(zope.interface.Interface):
    """Root object where on which global roles are stored.

    You have to provide an adapter from the root object to this interface.
    """
