About

    The PopupCalendarWidget is meant to replace the default calendar widget
    with a javascript popup calendar based on The DHTML Calendar that is
    included with Plone.

Usage

    You can set up the popup calendar using these options in your widget:

    ifFormat
    
        date format that will be stored in the input field.  The default value
        is localLongTimeFormat from site_properties.
        
        default: '%Y-%m-%d %H:%M'

    showsTime
    
        if true the calendar will include a time selector
        
        default: 'true'

    timeFormat
    
        the time format can be "12" or "24"
        
        default: '24'

    weekNumbers
    
        if it's true the calendar will display week numbers
        
        default: 'false'

    firstDay
    
        numeric: 0 to 6.  "0" means display Sunday first, "1" means display
        Monday first, etc.
        
        default: '0'

    range
    
        range of years in an array, ex. [1999,2010].  The default value is
        derived from site_properties calendar_starting_year and
        calendar_starting_year + calendar_future_years_available.
        
        default (in the year 2007): [1999, 2012]

    singleClick
    
        whether the calendar is in single click mode or not
        
        default: 'true'

    electric
    
        if true (default) then given fields/date areas are updated for each move
        otherwise they're updated only on close
        
        default: 'true'

    step
    
        configures the step of the years in drop-down boxes
        
        default: '1'

    showOthers
    
        if "true" it will show days from other months too
        
        default: 'false'
        
    calendar_icon
    
        select an icon for the edit page popup button
        
        default: 'popup-calendar.gif'

    helper_css
    
        the css used to render the calendar.  some of the other stock css are
        calendar-green.css, calendar-blue.css, calendar-brown.css
        
        default: 'jscalendar/calendar-system.css'

Dependencies
    
    Plone 2.0.5 - Plone 2.5.x
    
Author

    Clayton Parker (clayton AT sixfeetup DOT com) for Six Feet Up, Inc.
    
    http://www.sixfeetup.com
    
    claytron on #plone IRC channel on Freenode (irc.freenode.net)
