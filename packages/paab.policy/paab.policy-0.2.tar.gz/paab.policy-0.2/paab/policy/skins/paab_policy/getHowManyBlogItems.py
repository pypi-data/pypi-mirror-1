## Script (Python) "getHowManyBlogItems"
##title=Helper
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=


path = '/'.join(context.getPhysicalPath())

blogTypes = ['Document','News Item','Link','Event','Image']
l = 0

for klass in blogTypes:
    l = l + len(context.portal_catalog.searchResults(sort_on="id",portal_type=klass,sort_order="reverse",path=path) )
    
return l
