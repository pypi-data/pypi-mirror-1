## Script (Python) "getLastUpdate"
##title=Helper
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=


path = '/'.join(context.getPhysicalPath())
r = context.portal_catalog.searchResults(sort_on="Date",  path=path)

try:
    result = r[0].getObject().modification_date.Date()
except:
    result = context.modification_date.Date() 

return result 
