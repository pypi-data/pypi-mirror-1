# -*- coding: utf-8 -*-
#
# File: rss_item.py
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

from Products.ATContentTypes.content.newsitem import ATNewsItem
from Products.ATContentTypes.content.newsitem import ATNewsItemSchema
from Products.PloneRSS.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    StringField(
        name='rssKey',
        widget=StringField._properties['widget'](
            label='Rsskey',
            label_msgid='PloneRSS_label_rssKey',
            i18n_domain='PloneRSS',
        ),
    ),
    StringField(
        name='rssID',
        widget=StringField._properties['widget'](
            label='Rssid',
            label_msgid='PloneRSS_label_rssID',
            i18n_domain='PloneRSS',
        ),
    ),
    DateTimeField(
        name='rssDate',
        widget=DateTimeField._properties['widget'](
            label='Rssdate',
            label_msgid='PloneRSS_label_rssDate',
            i18n_domain='PloneRSS',
        ),
    ),
    StringField(
        name='remoteUrl',
        widget=StringField._properties['widget'](
            label="URL",
            description="Actual location of source news item",
            label_msgid='PloneRSS_label_remoteUrl',
            description_msgid='PloneRSS_help_remoteUrl',
            i18n_domain='PloneRSS',
        ),
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

rss_item_schema = ATNewsItemSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class rss_item(ATNewsItem):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.Irss_item)

    meta_type = 'rss_item'
    _at_rename_after_creation = True

    schema = rss_item_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(rss_item, PROJECTNAME)
# end of class rss_item

##code-section module-footer #fill in your manual code here
##/code-section module-footer



