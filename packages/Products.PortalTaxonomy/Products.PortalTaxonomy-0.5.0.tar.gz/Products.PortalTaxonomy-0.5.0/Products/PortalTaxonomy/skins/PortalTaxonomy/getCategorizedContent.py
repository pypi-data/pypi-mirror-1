## Script (Python) "getCategorizedContent.py"
##parameters=category_uids

from Products.CMFCore.utils import getToolByName

pc = getToolByName(context, 'portal_catalog')

return pc.searchResults(portal_type=['TaxonomyType',], review_state='published', getCategories=category_uids, sort_on='sortable_title')

