from Products.PopupCalendarWidget import PopupCalendarWidget as ats 
from Products.Archetypes import public as atapi

BaseSchemaCopy = atapi.BaseSchema.copy()
schema = BaseSchemaCopy + atapi.Schema((
    atapi.DateTimeField(
                'calendarWidgetDemo',
                required = True,
                widget = ats.PopupCalendarWidget(
                    label = 'Demo Field',
                    description = """<p>Enter a date or select from the calendar. 
                                     You can type in a date in any format DateTime understands. 
                                     The date will be formatted by default like the localLongTimeFormat in site_properties.</p>
                                     <p><b>Examples:</b></p>
                                     December 25, 2005 12:00<br />
                                     12/25/05 12:00<br />
                                     12-25-2005 12:00<br /><br />
                                   """,
                    'ifFormat'    : '%Y-%m-%d %H:%M',
                    'showsTime'   : 'true',
                    'timeFormat'  : "24",
                    'weekNumbers' : 'false',
                    'firstDay'    : '0',
                    'range'       : [1999, 2050],
                    'singleClick' : 'true',
                    'electric'    : 'true',
                    'step'        : '1',
                    'showOthers'  : 'false',
                    'calendar_icon' : 'popup_calendar.gif',
                    'macro'       : 'popup_calendar',
                    'helper_css'  : 'jscalendar/calendar-system.css',
                    'helper_js'   : ('jscalendar/calendar_stripped.js',
                                     'jscalendar/calendar-en.js',
                                     'jscalendar/calendar-setup.js'),
                ),
          ),
))

class PopupCalendarType(atapi.BaseContent):
      """
      A Simple type to test popup calendar widget
      """
      schema=schema
      global_allow=0
      archetype_name = portal_type = meta_type = "Popup Calendar Widget Demo"
          
atapi.registerType(PopupCalendarType)
