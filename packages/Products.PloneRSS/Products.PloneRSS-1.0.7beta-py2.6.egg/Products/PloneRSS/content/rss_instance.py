# -*- coding: utf-8 -*-
#
# File: rss_instance.py
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

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import \
    ReferenceBrowserWidget
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.PloneRSS.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    StringField(
        name='active',
        default="Yes",
        widget=SelectionWidget(
            label="Portlet active",
            description="Is this portlet currently to be displayed",
            label_msgid='PloneRSS_label_active',
            description_msgid='PloneRSS_help_active',
            i18n_domain='PloneRSS',
        ),
        vocabulary=['Yes','No'],
    ),
    ReferenceField(
        name='rss_feeds',
        widget=ReferenceBrowserWidget(
            label="Feeds",
            description="The feeds that will appear in this instance",
            label_msgid='PloneRSS_label_rss_feeds',
            description_msgid='PloneRSS_help_rss_feeds',
            i18n_domain='PloneRSS',
        ),
        allowed_types=('rss_feed',),
        multiValued=1,
        relationship='feeds',
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

rss_instance_schema = ATFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class rss_instance(ATFolder):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.Irss_instance)

    meta_type = 'rss_instance'
    _at_rename_after_creation = True

    schema = rss_instance_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(rss_instance, PROJECTNAME)
# end of class rss_instance

##code-section module-footer #fill in your manual code here
##/code-section module-footer



