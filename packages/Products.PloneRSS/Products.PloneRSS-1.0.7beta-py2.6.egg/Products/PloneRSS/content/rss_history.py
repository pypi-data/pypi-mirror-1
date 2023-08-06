# -*- coding: utf-8 -*-
#
# File: rss_history.py
#
# Copyright (c) 2008 by Encryptec Limited (c) 2007
# Generator: ArchGenXML Version 2.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Gareth Bult <gareth@encryptec.net>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.PloneRSS.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    DateTimeField(
        name='last_date',
        widget=DateTimeField._properties['widget'](
            label='Last_date',
            label_msgid='PloneRSS_label_last_date',
            i18n_domain='PloneRSS',
        ),
    ),
    IntegerField(
        name='last_count',
        widget=IntegerField._properties['widget'](
            label='Last_count',
            label_msgid='PloneRSS_label_last_count',
            i18n_domain='PloneRSS',
        ),
    ),
    IntegerField(
        name='last_status',
        widget=IntegerField._properties['widget'](
            label='Last_status',
            label_msgid='PloneRSS_label_last_status',
            i18n_domain='PloneRSS',
        ),
    ),
    StringField(
        name='body',
        widget=StringField._properties['widget'](
            label='Body',
            label_msgid='PloneRSS_label_body',
            i18n_domain='PloneRSS',
        ),
    ),
    StringField(
        name='url',
        widget=StringField._properties['widget'](
            label='Url',
            label_msgid='PloneRSS_label_url',
            i18n_domain='PloneRSS',
        ),
    ),
    StringField(
        name='feedID',
        widget=StringField._properties['widget'](
            label='Feedid',
            label_msgid='PloneRSS_label_feedID',
            i18n_domain='PloneRSS',
        ),
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

rss_history_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class rss_history(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.Irss_history)

    meta_type = 'rss_history'
    _at_rename_after_creation = True

    schema = rss_history_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(rss_history, PROJECTNAME)
# end of class rss_history

##code-section module-footer #fill in your manual code here
##/code-section module-footer



