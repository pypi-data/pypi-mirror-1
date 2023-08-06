# -*- coding: iso-8859-15 -*-

################################################################
# collective.calendarwidget
# (C) 2009, ZOPYX Ltd. & Co. KG 
################################################################

import time
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from DateTime.DateTime import DateTime
from Products.Archetypes.public import CalendarWidget
from Products.Archetypes.Registry import registerWidget

class CalendarWidget(CalendarWidget):
    """ A widget für DateTime fields"""

    _properties = CalendarWidget._properties.copy()
    _properties.update({
        'macro' : 'collective_calendarwidget',
        'dateformat' : '%d.%m.%Y',
        'with_time' : False,
        'default_hour' : 0,
        'default_minute' : 0,
        })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None, emptyReturnsMarker=False):
        fieldname = field.getName()
        datestr = form.get(fieldname)
        if not datestr:
            return empty_marker
        date_format = form.get(fieldname + '-date-format')
        hours = int(form.get(fieldname + '_hour', 0))
        minutes = int(form.get(fieldname + '_minute', 0))
        datestr = '%s %s:%s:00' % (datestr, hours, minutes)
        tp = time.strptime(datestr, date_format + ' %H:%M:%S')
        return DateTime(time.mktime(tp)), {}

InitializeClass(CalendarWidget)

registerWidget(CalendarWidget,
               title='CalendarWidget',
               description='A simple calendar widget',
               used_for=('Products.Archetypes.Field.DateTimeField',)
               )

