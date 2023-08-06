## Script (Python) "batch_attributes_process"
##bind container=container
##parameters=attribute_batch

from Products.CMFCore.utils import getToolByName

pu = getToolByName(context, 'plone_utils')
for att in attribute_batch.split('\n'):
    title = att.strip()
    if len(title) == 0:
        continue
    id = pu.normalizeString(title)
    context.invokeFactory('Attribute', id, title=title)

container.REQUEST.RESPONSE.redirect(context.absolute_url())
