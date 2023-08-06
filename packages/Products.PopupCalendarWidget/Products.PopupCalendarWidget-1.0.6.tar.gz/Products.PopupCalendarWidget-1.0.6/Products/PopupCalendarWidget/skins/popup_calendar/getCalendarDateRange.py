## Script (Python) "getCalendarDateRange"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get the date, or return an empty string
##

from DateTime import DateTime

site_props = context.portal_properties.site_properties
# setup year range array
past_date = site_props.calendar_starting_year
current_year = DateTime().year()
future_date = current_year + int(site_props.calendar_future_years_available)

return [past_date, future_date]
