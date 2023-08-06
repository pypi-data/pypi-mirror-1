## Script (Python) "checkForDate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=value, format
##title=Get the date, or return an empty string
##

from DateTime import DateTime
test_value = value  

if value:
    try:
        d = DateTime(value)
        return d.strftime(format)
    except DateTime.DateError: 
        return value
else:
    return value