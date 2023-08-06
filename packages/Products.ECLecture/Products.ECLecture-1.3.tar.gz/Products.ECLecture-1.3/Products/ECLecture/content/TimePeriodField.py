# -*- coding: utf-8 -*-
# $Id: TimePeriodField.py 1281 2009-09-24 15:03:08Z amelung $
#
# Copyright (c) 2006-2009 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECLecture.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

import re

from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import ObjectField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.Registry import registerField

from Products.validation import validation


from validators import TimePeriodValidator

# -- register time period validator -------------------------------------------
isTimePeriod = TimePeriodValidator("isTimePeriod")
validation.register(isTimePeriod)


class TimePeriodField(ObjectField):
    """
    A field that stores a list of two integer values representing 
    a time period
    """

    __implements__ = ObjectField.__implements__

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type' : 'integer',
        'size' : '5',
        'widget' : StringWidget,
        'default' : [],
        'validators' : ('isTimePeriod'),
        })

    security  = ClassSecurityInfo()

    security.declarePrivate('validate_required')
    def validate_required(self, instance, value, errors):
        """
        Tests if all elements in value are not None. If one is None a 
        error message will be returned.
        
        @see ObjectField.validate_required
        """
        result = True
        
        for item in value:
            if not item:
                result = False
                break

        return ObjectField.validate_required(self, instance, result, errors)

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """
        Tests if all elements in value are numbers and save them as minutes.
        
        @see ObjectField.set
        """
        result = []
        
        for item in value:
            if self.required or item:
                m = re.match('^(\d\d)[.:]?(\d\d)$', item.strip())
                result.append((int(m.group(1)) * 60 ) + int(m.group(2)))
            else:
                result = []
                break
        
        ObjectField.set(self, instance, result, **kwargs)


registerField(TimePeriodField,
              title='TimePeriod',
              description=('Stores a list of two integer values representing '
                           'a time period')
    )
