#
# Copyright 2008-2009, Blue Dynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from datetime import datetime
from DateTime import DateTime
from AccessControl import ClassSecurityInfo

from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Field import DateTimeField

from widget import IntelliDateTimeWidget

class IntelliDateTimeField(DateTimeField):
    
    _properties = DateTimeField._properties.copy()
    _properties.update({
        'type': 'intellidatetime',
        'widget': IntelliDateTimeWidget,
    })

    security  = ClassSecurityInfo()
    
    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """
        Check if value is an actual date/time value. If not, attempt
        to convert it to one; otherwise, set to None. Assign all
        properties passed as kwargs to object.
        """
        if not value:
            value = None
#        elif not isinstance(value, DateTime) :
#            try:
#                value = DateTime(value)
#            except DateTime.DateTimeError:
#                value = None

        ObjectField.set(self, instance, value, **kwargs)    