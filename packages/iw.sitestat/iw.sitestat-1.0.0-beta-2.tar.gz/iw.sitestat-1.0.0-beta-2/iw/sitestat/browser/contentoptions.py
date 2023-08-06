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

# $Id: contentoptions.py 45 2008-09-30 16:23:05Z glenfant $
"""
Content Sitestat options management
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from zope.interface import Interface, Attribute
from zope.interface import implements
from zope.component import adapts
from zope.component import getAdapter
from zope.annotation.interfaces import IAnnotations
from zope.schema import Bool, ASCIILine, Tuple
from zope.schema import ValidationError
from zope.app.form.browser.textwidgets import ASCIIWidget
from zope.formlib import form
from Persistence import Persistent
from Products.Five.formlib import formbase
from Products.CMFCore.interfaces import IContentish
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone import PloneMessageFactory as p_
from iw.sitestat.interfaces import ISitestatConfigSchema
from iw.sitestat.config import ANNOTATIONS_KEY, BLACKLISTED_LABELS
from iw.sitestat.utils import getSite, validateSitestatName
from iw.sitestat import IwSitestatMessageFactory as _
from iw.sitestat import logger

###
## Errors and validators
###

class InvalidCounterError(ValidationError):
    __doc__ = _(u'error_invalid_counter', default=u"This counter is invalid")


def validateCounters(value):
    counters = value.strip().split('.')
    for counter in counters:
        if not bool(counter):
            raise InvalidCounterError
        if not validateSitestatName(counter.lower()):
            raise InvalidCounterError
    return True


class InvalidLabelsError(ValidationError):
    __doc__ = _(u'error_invalid_labels', default=u"One (or more) label is invalid")


class DuplicateLabelError(ValidationError):
    __doc__ = _(u'error_duplicate_label', default=u"Don't duplicate a label name")


class BlacklistedLabelError(ValidationError):
    __doc__ = _(u'error_blacklisted_label', default=u"A label is blacklisted.")


def validateLabels(labels):
    valid_labels = []
    for label_value in labels:
        # Testing "label=value" correctness
        try:
            label, value = [x.strip() for x in label_value.split('=')]
        except ValueError, e:
            raise InvalidLabelsError
        if not validateSitestatName(label):
            raise InvalidLabelsError
        if not validateSitestatName(value):
            raise InvalidLabelsError
        # Testing unicity
        if label in valid_labels:
            raise DuplicateLabelError
        if label in BLACKLISTED_LABELS:
            raise BlacklistedLabelError
        valid_labels.append(label)
    return True

###
## Interface for content item adapter and form
###

class IContentOptions(Interface):

    is_clickin_target = Bool(
        title=_(u'label_is_clickin_target', default=u"Clickin target?"),
        description=_(u'help_is_clickin_target', default=u"Is this content a clickin target?"
            u" If checked, all links to this item's view will be transformed into Sitestat clickin URLs."),
        default=False)

    override_counters = Bool(
        title=_(u'label_override_counters', default=u"Override standard counters"),
        description=_(u'help_override_counters', default=u"Do we override global counter rules for this item?"),
        default=False)

    counters = ASCIILine(
        title=_(u'label_custom_counters', default=u"Custom counters"),
        description=_(u'help_custom_counters', default=u"Use these counters for this item if you override global counters."
            u" Multiple counters must be separated with a dot. Non ASCII characters may not be supported by Sitestat."
            u" Example: \"Company.Contact\"."),
        constraint = validateCounters,
        required=False)

    labels = Tuple(
        # This is ugly due to an i18n bug in formlib: button don't translate the title
        title=_(u'label', default=u"Labels"),
        description=_(u'help_labels', default=u"Labels for this item. Watch your Sitestat labels list."
            u" By default, Sitestat has only the \"category\" label."
            u" Enter label and values in the form \"<label>=<value>\". Example: \"category=sport\"."),
        value_type=ASCIILine(),
        constraint=validateLabels,
        required=False)


###
## Adapter to annotations storage on context
###

class OptionsStorage(Persistent):
    """Settings for context local options (stored in context annotations)"""

    override_counters = False
    counters = ''
    labels = {}


class ContentOptionsManager(object):
    """Adapter for content object that manages local Sitestat options"""

    adapts(IContentish)
    implements(IContentOptions)

    def __init__(self, context):
        self.context = context
        self.global_config = getAdapter(getSite(), ISitestatConfigSchema)
        return


    @property
    def local_options(self):
        """Proxy to context annotations stored options"""
        annotations = IAnnotations(self.context)
        return annotations.setdefault(ANNOTATIONS_KEY, OptionsStorage())


    @apply
    def is_clickin_target():
        """Proxy on storage, use as a property"""

        def get(self):
            clickin_uids = self.global_config.clickin_uids
            this_uid = self.context.UID()
            return this_uid in clickin_uids

        def set(self, value):
            if get(self) != value:
                # We are changing the status
                clickin_uids = list(self.global_config.clickin_uids)
                if value:
                    # We add this UID
                    clickin_uids.append(self.context.UID())
                else:
                    # We remove the UID
                    clickin_uids.remove(self.context.UID())
                self.global_config.clickin_uids = clickin_uids
                compileClickinPaths()
            return

        return property(get, set)


    @apply
    def override_counters():
        """Proxy on storage, use as a property"""

        def get(self):
            return self.local_options.override_counters

        def set(self, value):
            self.local_options.override_counters = bool(value)
            return

        return property(get, set)


    @apply
    def counters():
        """Proxy on storage, use as a property"""

        def get(self):
            return self.local_options.counters

        def set(self, value):
            if value is None:
                value = ''
            self.local_options.counters = value.strip()
            return

        return property(get, set)


    @apply
    def labels():
        """Proxy on storage, use as a property"""

        def get(self):
            labels = self.local_options.labels
            out = ["%s=%s" % (k, v) for k, v in labels.items()]
            out.sort()
            return tuple(out)

        def set(self, value):
            d_values = {}
            for label in value:
                k, v = [x.strip() for x in label.split('=')]
                d_values[k] = v
            self.local_options.labels = d_values
            return

        return property(get, set)


    @apply
    def raw_labels():
        """Dict raw value of labels"""

        def get(self):
            return self.local_options.labels
        def set(self, value):
            self.local_options.labels = value
        return property(get, set)


###
## Our form and special widgets
###

class CountersWidget(ASCIIWidget):
    displayWidth = 40


class ContentOptionsForm(formbase.EditForm):
    """Our form"""

    label = _(u'content_options_title', default=u"Item specific settings for Sitestat")
    description = _(u'content_options_help', default=u"Change or add Sitestat features for this content item.")
    form_fields = form.FormFields(IContentOptions)
    form_fields['counters'].custom_widget = CountersWidget

    @form.action(p_(u'label_save'))
    def handleApply(self, action, data):
        storage = getAdapter(self.context, IContentOptions)
        is_clickin_target = data['is_clickin_target']
        if storage.is_clickin_target != is_clickin_target:
            # Changed mode
            global_config = getAdapter(getSite(), ISitestatConfigSchema)

        storage.is_clickin_target = is_clickin_target
        storage.override_counters = data['override_counters']
        storage.counters = data['counters']
        storage.labels = data['labels']
        IStatusMessage(self.request).addStatusMessage(p_(u'Changes made.'), type='info')
        self.request.RESPONSE.redirect(self.request.URL)
        # Uh, when returning something else, the status message doesn't show!
        return ''

###
## Updating property sheet's global clickin_path on changes
## (see events.py too)
###

def compileClickinPaths():
    portal = getSite()
    global_config = getAdapter(portal, ISitestatConfigSchema)
    catalog = portal.uid_catalog
    paths = []
    for uid in global_config.clickin_uids:
        brains = catalog.searchResults(UID=uid)
        try:
            paths.append(brains[0].getPath())
        except IndexError:
            logger.error("Object with UID %s is gone.", uid)
    global_config.clickin_paths = paths
    return
