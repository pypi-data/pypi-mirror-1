## Script (Python) "batch_categories_process"
##bind container=container
##parameters=category_batch

from Products.CMFCore.utils import getToolByName

pu = getToolByName(context, 'plone_utils')
for cat in category_batch.split('\n'):
    title = cat.strip()
    if len(title) == 0:
        continue
    id = pu.normalizeString(title)
    context.invokeFactory('Category', id, title=title)

container.REQUEST.RESPONSE.redirect(context.absolute_url())
