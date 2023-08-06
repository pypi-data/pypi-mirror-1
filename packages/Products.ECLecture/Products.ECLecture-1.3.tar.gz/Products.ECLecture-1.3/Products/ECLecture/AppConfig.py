# -*- coding: utf-8 -*-
# $Id: AppConfig.py 1282 2009-09-24 18:10:56Z amelung $
#
# Copyright (c) 2006-2009 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECLecture.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'


from Products.ATContentTypes.configuration.config import zconf

try: # New CMF 
    from Products.CMFCore import permissions
except: # Old CMF 
    from Products.CMFCore import CMFCorePermissions as permissions


# i18n 
I18N_DOMAIN = 'eduComponents'

# dependencies of products to be installed by quick-installer
DEPENDENCIES = ['DataGridField']

# supported mime types for textfields
#EC_MIME_TYPES = ('text/x-web-intelligent',)
EC_MIME_TYPES = zconf.ATDocument.allowed_content_types
#EC_MIME_TYPES = ('text/plain', 'text/structured', 'text/x-rst', 'text/x-web-intelligent', 'text/html', )

# default mime type for textfields
#EC_DEFAULT_MIME_TYPE = 'text/x-web-intelligent'
EC_DEFAULT_MIME_TYPE = zconf.ATDocument.default_content_type
#EC_DEFAULT_MIME_TYPE = 'text/plain'

# default output format of textfields
#EC_DEFAULT_FORMAT = 'text/html'
EC_DEFAULT_FORMAT = 'text/x-html-safe'
