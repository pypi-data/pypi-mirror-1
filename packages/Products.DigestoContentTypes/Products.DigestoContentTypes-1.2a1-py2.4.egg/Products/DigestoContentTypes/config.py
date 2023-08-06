# -*- coding: utf-8 -*-
#
# File: DigestoContentTypes.py
#
# Copyright (c) 2009 by Menttes SRL
# Generator: ArchGenXML Version 2.4.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Emanuel Sartor <emanuel@menttes.com>, Santiago Bruno <unknown>"""
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


PROJECTNAME = "DigestoContentTypes"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner', 'Contributor'))
ADD_CONTENT_PERMISSIONS = {
    'Attachment': 'DigestoContentTypes: Add Attachment',
    'Normativa': 'DigestoContentTypes: Add Normativa',
    'Area': 'DigestoContentTypes: Add Area',
}

setDefaultRoles('DigestoContentTypes: Add Attachment', ('Manager','Owner'))
setDefaultRoles('DigestoContentTypes: Add Normativa', ('Manager','Owner'))
setDefaultRoles('DigestoContentTypes: Add Area', ('Manager','Owner'))

product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []

##code-section config-bottom #fill in your manual code here
PLACEFUL_WORKFLOW_POLICY = 'area_placeful_workflow'
ABBREVIATIONS_KEY = 'DigestoContentTypesAbbreviationsKey'
##/code-section config-bottom


# Load custom configuration not managed by archgenxml
try:
    from Products.DigestoContentTypes.AppConfig import *
except ImportError:
    pass
