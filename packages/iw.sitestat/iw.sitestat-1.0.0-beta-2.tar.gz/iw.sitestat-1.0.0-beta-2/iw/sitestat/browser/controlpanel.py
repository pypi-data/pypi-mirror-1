# -*- coding: utf-8 -*-
## Copyright (C) 2008 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file LICENSE.txt. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# $Id: controlpanel.py 45 2008-09-30 16:23:05Z glenfant $
"""
Sitestat global options control panel
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

import urlparse
from zope.interface import Interface, Attribute
from zope.interface import implements
from zope.component import adapts
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import ASCIILine
from zope.schema import Tuple
from zope.schema import ValidationError
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from plone.fieldsets.fieldsets import FormFieldsets
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import getSiteEncoding
from Products.CMFPlone import PloneMessageFactory as p_

from plone.app.controlpanel.form import ControlPanelForm

from iw.sitestat.formlib import URLLine
from iw.sitestat.config import PROPERTYSHEET
from iw.sitestat.utils import getSite, validateSitestatName
from iw.sitestat import IwSitestatMessageFactory as _

###
## Validators and form validaiton errors
###

class InvalidASCIILabel(ValidationError):
    __doc__ = _(u'error_invalid_label', default=u"Label has unauthorized characters.")


def validateASCIILabel(value):
    if not validateSitestatName(value):
        raise InvalidASCIILabel(value)
    return True


class InvalidURL(ValidationError):
    __doc__ = _(u'error_invalid_url', default=u"Invalid URL form.")


def validateOptionalURL(value):
    if len(value) == 0:
        # Empty URL ignored
        return True
    parsed = urlparse.urlparse(value)
    if parsed[0] not in ('http', 'https'):
        raise InvalidURL(value)
    unparsed = urlparse.urlunparse(parsed)
    if unparsed != value:
        raise InvalidURL(value)
    return True

###
## Site adapter and form interfaces
###

class ISitestatGlobalConfigSchema(Interface):
    """Site wide configuration for iw.sitestat"""

    sitestat_enabled = Bool(
        title=_(u'label_sitestat_enabled', default=u"Enable sitestat?"),
        description=_(u'help_sitestat_enabled', default=u"Will provide your Sitestat service relevant information."
            u" <strong>Please check that your Sitestat server is active otherwise this site will unusable</stong>."
            u" If unchecked, all options below as well as content local options wil be ignored"),
        default=False,
        required=False)

    country_code = Choice(
        title=_(u'label_country_code', default=u"Your country code"),
        description=_(u'help_country_code', default=u"Choose your country in this list"),
        vocabulary='iw.sitestat.vocabularies.CountryNamesVocabulary',
        required=True)

    company_code = ASCIILine(
        title=_(u'label_company_code', default=u"Company code"),
        description=_(u'help_company_code', default=u"The company code, as in your Sitestat settings. Only ASCII lowercases."),
        required=True,
        constraint=validateASCIILabel)

    site_code = ASCIILine(
        title=_(u'label_site_code', default=u"Site code"),
        description=_(u'help_site_code', default=u"The site code, as in your Sitestat settings. Only ASCII lowercases."),
        required=True,
        constraint=validateASCIILabel)

    sitestat_private_url = URLLine(
        title=_(u'label_sitestat_url', default=u"Sitestat private URL"),
        description=_(u'help_sitestat_url', default=u"If you have a private Sitestat server, please fill-in its URL."),
        required=False)

    counter_name_mode = Choice(
        title=_(u'label_counter_name_mode', default=u"Counter name composition mode"),
        description=_(u'help_counter_name_mode', default=u"Choose what policy we use to build counter names."),
        vocabulary='iw.sitestat.vocabularies.CounterNameModeVocabulary',
        required=True,
        default='id')

    pdf_marking = Bool(
        title=_(u'label_pdf_marking', default=u"Mark links to PDF files?"),
        description=_(u'help_pdf_marking', default=u"Make special Sitestat URLs to PDF files."),
        default=False,
        required=False)

    files_as_pdf = Bool(
        title=_(u'label_files_as_pdf', default=u"Mark all files links as PDF?"),
        description=_(u'help_files_as_pdf', default=u"Do we mark all links to files (word, excel, ...) as PDF?"
            u" <strong>This option will be ignored if previous option is unchecked</strong>."),
        default=False,
        required=False)

    dltime_enabled = Bool(
        title=_(u'label_dltime_enabled', default=u"Include page download time"),
        description=_(u'help_dltime_enabled', default=u"Sitestat will have download time information for each page."),
        default=False,
        required=False)

    https_enabled = Bool(
        title=_(u'label_https_enabled', default=u"Enable https://... links on secure pages?"),
        description=_(u'help_https_enabled', default=u"Do <strong>not</strong> check this if your Sitestat settings"
            u" do not allow https pages, otherwise links from secure pages could be broken."),
        default=False,
        required=False)

    # Don't need it in the form but in the adapter
    clickin_uids = Attribute("The item UIDs of clickin target")
    clickin_paths = Attribute("The item paths for clickin targets")



class ISitestatClickInOutSchema(Interface):
    """cickin & clickout global config for iw.sitestat"""

    clickin_enabled = Bool(
        title=_(u'label_clickin_enabled', default=u"Enable clickin?"),
        description=_(u'help_clickin_enabled', default=u"Links to clickin target wil be transformed into Sitestat clickin URLS."),
        default=False,
        required=False)

    clickout_urls = Tuple(
        title=_(u'label_clickout_urls', default=u"Clickout URLs"),
        description=_(u'help_clickout_urls', default=u"URLs of links to other sites to be transformed to Sitestat clickouts."),
        value_type=URLLine(),
        required=False)


class ISitestatConfigSchema(ISitestatGlobalConfigSchema, ISitestatClickInOutSchema):
    """Combined schema"""
    pass


###
## Adapter that proxies to a propertysheet
###

class SitestatControlPanelAdapter(SchemaAdapterBase):
    """Access to iw.sitestat global options
    """

    adapts(IPloneSiteRoot)
    implements(ISitestatConfigSchema)

    def __init__(self, context):
        super(SitestatControlPanelAdapter, self).__init__(context)
        self.portal = context
        pprop = getToolByName(self.portal, 'portal_properties')
        self.context = getattr(pprop, PROPERTYSHEET)
        self.encoding = getSiteEncoding(context)
        return

    # Assume read/write in our property sheet
    sitestat_enabled = ProxyFieldProperty(ISitestatConfigSchema['sitestat_enabled'])
    country_code = ProxyFieldProperty(ISitestatConfigSchema['country_code'])
    company_code = ProxyFieldProperty(ISitestatConfigSchema['company_code'])
    site_code = ProxyFieldProperty(ISitestatConfigSchema['site_code'])
    sitestat_private_url = ProxyFieldProperty(ISitestatConfigSchema['sitestat_private_url'])
    counter_name_mode = ProxyFieldProperty(ISitestatConfigSchema['counter_name_mode'])
    pdf_marking = ProxyFieldProperty(ISitestatConfigSchema['pdf_marking'])
    files_as_pdf = ProxyFieldProperty(ISitestatConfigSchema['files_as_pdf'])
    dltime_enabled = ProxyFieldProperty(ISitestatConfigSchema['dltime_enabled'])
    https_enabled = ProxyFieldProperty(ISitestatConfigSchema['https_enabled'])
    clickin_enabled = ProxyFieldProperty(ISitestatConfigSchema['clickin_enabled'])
    clickout_urls = ProxyFieldProperty(ISitestatConfigSchema['clickout_urls'])

    @apply
    def clickin_uids():
        def get(self):
            return self.context.getProperty('clickin_uids')
        def set(self, value):
            self.context.manage_changeProperties(clickin_uids=value)
        return property(get, set)

    @apply
    def clickin_paths():
        def get(self):
            return self.context.getProperty('clickin_paths')
        def set(self, value):
            self.context.manage_changeProperties(clickin_paths=value)
        return property(get, set)

###
## Our form in 2 thumbnails
###

baseset = FormFieldsets(ISitestatGlobalConfigSchema)
baseset.id = 'baseset'
baseset.label = _(u'label_base_subform', default=u"Base features")

clickinoutset = FormFieldsets(ISitestatClickInOutSchema)
clickinoutset.id = 'clickinoutset'
clickinoutset.label = _(u'label_clickinckickout_subform', default="Clickin and Clickout")

class SitestatControlPanel(ControlPanelForm):

    label = _(u'label_controlpanel', default=u"Sitestat settings")
    description = _(u'help_controlpanel', default="Sitestat site-wide settings.")
    form_name = label

    form_fields = FormFieldsets(baseset, clickinoutset)

###
## Vocabularies
###

class CounterNameModeVocabulary(object):
    """Vocabulary for 'counter_name_mode'. Get it in interface Choice fields
    with the name 'iw.sitestat.vocabularies.CounterNameModeVocabulary' """

    implements(IVocabularyFactory)

    def __call__(self, context):
        terms = (
            SimpleTerm('id', 'id', _(u'obj_identifiers', default=u"Content identifiers (from URL)")),
            SimpleTerm('title', 'title', _(u'obj_titles', default=u"Content titles"))
            )
        return SimpleVocabulary(terms)


CounterNameModeVocabularyFactory = CounterNameModeVocabulary()


class CountryNamesVocabulary(object):
    """Vocabulary for choosing a country"""

    implements(IVocabularyFactory)

    def __call__(self, context):
        portal_languages = getToolByName(getSite(), 'portal_languages')
        # countries_tuples = [(u'de', u'Deutschland'), ...]
        countries_tuples = [(x, y[u'name']) for x, y in portal_languages.getAvailableCountries().items()]
        countries_tuples.sort(lambda x, y: cmp(x[1], y[1]))
        terms = [SimpleTerm(c[0], c[0], p_(c[1])) for c in countries_tuples]
        return SimpleVocabulary(terms)


CountryNamesVocabularyFactory = CountryNamesVocabulary()
