# -*- coding: latin-1 -*-
# Copyright (c) 2008 Michael Howitz
# See also LICENSE.txt
# $Id: sources.py 696 2008-10-06 18:17:20Z mac $

import stabledict
import zc.sourcefactory.basic
import zope.component

from icemac.addressbook.i18n import MessageFactory as _


class TitleMappingSource(zc.sourcefactory.basic.BasicSourceFactory):
    "Abstract base class for sources using a mapping between value and title."
    
    _mapping = None # to be set in child class

    def getValues(self):
        return self._mapping.keys()

    def getTitle(self, value):
        return self._mapping[value]


class SexSource(TitleMappingSource):
    _mapping = stabledict.StableDict(
        ((u'male', _(u'male')),
         (u'female', _(u'female'))))


class SalutationSource(TitleMappingSource):
    _mapping = stabledict.StableDict(
        ((u'male', _(u'Mr.')), 
         (u'female', _(u'Ms.'))))

salutation_source = SalutationSource()

class PhoneNumberKindSource(TitleMappingSource):
    _mapping = {
        u'cell phone': _(u'cell phone'),
        u'work phone': _(u'work phone'),
        u'work fax': _(u'work fax'),
        u'private phone': _(u'private phone'),
        u'private fax': _(u'private fax'),
        u'other': _(u'other'),
        }

class WorkPrivateKindSource(TitleMappingSource):
    _mapping = stabledict.StableDict(
        ((u'private', _(u'private')),
         (u'work', _(u'work')),
         (u'other', _(u'other'))))

class KeywordSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        import icemac.addressbook.interfaces # avoid circular import
        keywords = zope.component.getUtility(
            icemac.addressbook.interfaces.IKeywords)
        return keywords.get_keywords()

    def getTitle(self, value):
        return value.title

keyword_source = KeywordSource()
