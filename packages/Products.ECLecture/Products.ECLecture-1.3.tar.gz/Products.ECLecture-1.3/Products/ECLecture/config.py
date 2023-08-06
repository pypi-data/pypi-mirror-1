# -*- coding: utf-8 -*-
# $Id: config.py 1281 2009-09-24 15:03:08Z amelung $
#
# Copyright (c) 2006-2009 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECLecture.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
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


PROJECTNAME = "ECLecture"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))
ADD_CONTENT_PERMISSIONS = {
    'ECLecture': 'ECLecture: Add ECLecture',
}

setDefaultRoles('ECLecture: Add ECLecture', ('Manager','Owner'))

product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []


# Load custom configuration not managed by archgenxml
try:
    from Products.ECLecture.AppConfig import *
except ImportError:
    pass
