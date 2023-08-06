## Script (Python) "getSubcategoryUIDs.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

query = {}
query['path'] = '/'.join(context.getPhysicalPath())
query['portal_type'] = 'Category'
query['review_state'] = 'published'

return [c.UID for c in context.portal_catalog(query)]
