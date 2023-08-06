# -*- coding: utf-8 -*-
#
# File: rss_feed.py
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

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.PloneRSS.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    StringField(
        name='frequency',
        widget=SelectionWidget(
            label="Update frequency",
            description="How often should we update the feed from the RSS source",
            label_msgid='PloneRSS_label_frequency',
            description_msgid='PloneRSS_help_frequency',
            i18n_domain='PloneRSS',
        ),
        vocabulary=['1 day','12 hours','8 hours','4 hours','2 hours','1 hour','30 minutes','15 minutes','5 minutes'],
    ),
    StringField(
        name='rssID',
        widget=StringField._properties['widget'](
            visible=False,
            label='Rssid',
            label_msgid='PloneRSS_label_rssID',
            i18n_domain='PloneRSS',
        ),
    ),
    StringField(
        name='maxage',
        widget=SelectionWidget(
            label="Maximum item age",
            description="How long we should keep news items in the database",
            label_msgid='PloneRSS_label_maxage',
            description_msgid='PloneRSS_help_maxage',
            i18n_domain='PloneRSS',
        ),
        vocabulary=['Unlimited','1 week','2 weeks','1 month','2 months','4 months','8 months','16 months'],
    ),
    StringField(
        name='remoteURL',
        widget=StringField._properties['widget'](
            label="Feed URL",
            size=80,
            maxlength=1024,
            label_msgid='PloneRSS_label_remoteURL',
            i18n_domain='PloneRSS',
        ),
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

rss_feed_schema = ATFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class rss_feed(ATFolder):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.Irss_feed)

    meta_type = 'rss_feed'
    _at_rename_after_creation = True

    schema = rss_feed_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(rss_feed, PROJECTNAME)
# end of class rss_feed

##code-section module-footer #fill in your manual code here
##/code-section module-footer



