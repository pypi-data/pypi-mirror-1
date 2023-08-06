#  Copyright (c) 2006 Six Feet Up, Inc.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
"""
from Products.Archetypes.Widget import TypesWidget
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget,registerPropertyType

class PopupCalendarWidget(TypesWidget):
    """
    Use the jscalendar for date entry. See the README for details.
    """
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'description' : 'Click the blank field to select a date from the calendar',
        'ifFormat'    : '',
        'showsTime'   : 'true',
        'timeFormat'  : "24",
        'weekNumbers' : 'false',
        'firstDay'    : '0',
        'range'       : '',
        'singleClick' : 'true',
        'electric'    : 'true',
        'step'        : '1',
        'showOthers'  : 'false',
        'calendar_icon' : 'popup_calendar.gif',
        'macro'       : 'popup_calendar',
        'helper_css'  : ('jscalendar/calendar-system.css',),
        'helper_js'   : ('jscalendar/calendar_stripped.js',
                         'jscalendar/calendar-en.js',
                         'jscalendar/calendar-setup.js'),
        })

    security = ClassSecurityInfo()

registerWidget(PopupCalendarWidget,
               title='Popup Calendar Widget',
               description=('A calendar widget that uses a popup javascript calendar.'),
               used_for=('Products.Archetypes.Field.DateTimeField',)
               )

registerPropertyType('ifFormat', 'string', PopupCalendarWidget)
registerPropertyType('showsTime', 'string', PopupCalendarWidget)
registerPropertyType('timeFormat', 'string', PopupCalendarWidget)
registerPropertyType('weekNumbers', 'string', PopupCalendarWidget)
registerPropertyType('range', 'string', PopupCalendarWidget)
registerPropertyType('singleClick', 'string', PopupCalendarWidget)
registerPropertyType('electric', 'string', PopupCalendarWidget)
registerPropertyType('step', 'string', PopupCalendarWidget)
registerPropertyType('showOthers', 'string', PopupCalendarWidget)
registerPropertyType('calendar_icon', 'string', PopupCalendarWidget)
registerPropertyType('validators', 'validators', PopupCalendarWidget)
