# -*- coding: utf-8 -*-
# $Id: interfaces.py 1281 2009-09-24 15:03:08Z amelung $
#
# Copyright (c) 2006-2009 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECLecture.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

from zope.interface import Interface

class IECLecture(Interface):
    """
    Marker interface for .ECLecture.ECLecture
    """
