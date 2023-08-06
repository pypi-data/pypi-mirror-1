# -*- coding: utf-8 -*-
#
# File: PloneRSS.py
#
# Copyright (c) 2008 by []
# Generator: ArchGenXML Version 2.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'


# Product configuration.
#
# The contents of this module will be imported into __init__.py, the
# workflow configuration and every content type module.
#
# If you wish to perform custom configuration, you may put a file
# AppConfig.py in your product's root directory. The items in there
# will be included (by importing) in this file if found.

from Products.CMFCore.permissions import setDefaultRoles
##code-section config-head #fill in your manual code here
##/code-section config-head


PROJECTNAME = "PloneRSS"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))
ADD_CONTENT_PERMISSIONS = {
    'rss_manager': 'rss: Add rss_manager',
    'rss_feed': 'PloneRSS: Add rss_feed',
    'rss_item': 'rss: Add rss_item',
    'rss_instance': 'PloneRSS: Add rss_instance',
    'rss_history': 'rss: Add rss_item',
}

setDefaultRoles('rss: Add rss_manager', '("Manager",)')
setDefaultRoles('PloneRSS: Add rss_feed', ('Manager','Owner'))
setDefaultRoles('rss: Add rss_item', '("Manager",)')
setDefaultRoles('PloneRSS: Add rss_instance', ('Manager','Owner'))

product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []

##code-section config-bottom #fill in your manual code here
##/code-section config-bottom


# Load custom configuration not managed by archgenxml
try:
    from Products.PloneRSS.AppConfig import *
except ImportError:
    pass
