# -*- coding: utf-8 -*-
# $Id: __init__.py 1281 2009-09-24 15:03:08Z amelung $
#
# Copyright (c) 2006-2009 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECLecture.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'


# There are three ways to inject custom code here:
#
#   - To set global configuration variables, create a file AppConfig.py.
#       This will be imported in config.py, which in turn is imported in
#       each generated class and in this file.
#   - To perform custom initialisation after types have been registered,
#       use the protected code section at the bottom of initialize().

import logging
logger = logging.getLogger('ECLecture')
logger.debug('Installing Product')

import os
import os.path
from Globals import package_home
from zope.i18nmessageid import MessageFactory
import Products.CMFPlone.interfaces
from Products.Archetypes import listTypes
from Products.Archetypes.atapi import *
from Products.Archetypes.utils import capitalize
from Products.CMFCore import DirectoryView
from Products.CMFCore import permissions as cmfpermissions
from Products.CMFCore import utils as cmfutils
from Products.CMFPlone.utils import ToolInit
from config import *

DirectoryView.registerDirectory('skins', product_globals)

ECLMessageFactory = MessageFactory('eXtremeManagement')

def initialize(context):
    """initialize product (called by zope)"""
    ##code-section custom-init-top #fill in your manual code here
    ##/code-section custom-init-top

    # imports packages and types for registration
    import content


    # Initialize portal content
    all_content_types, all_constructors, all_ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = all_content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = all_constructors,
        fti                = all_ftis,
        ).initialize(context)

    # Give it some extra permissions to control them on a per class limit
    for i in range(0,len(all_content_types)):
        klassname=all_content_types[i].__name__
        if not klassname in ADD_CONTENT_PERMISSIONS:
            continue

        context.registerClass(meta_type   = all_ftis[i]['meta_type'],
                              constructors= (all_constructors[i],),
                              permission  = ADD_CONTENT_PERMISSIONS[klassname])

    ##code-section custom-init-bottom #fill in your manual code here
    ##/code-section custom-init-bottom

