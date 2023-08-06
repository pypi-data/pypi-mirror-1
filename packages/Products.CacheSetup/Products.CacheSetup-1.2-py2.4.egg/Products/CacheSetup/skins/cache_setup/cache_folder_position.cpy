## Controller Python Script "folder_position"
##title=Move objects in a ordered folder
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=position, id, template_id='folder_contents'
##

from Products.CMFPlone import PloneMessageFactory as _
from Products.CacheSetup import config

position=position.lower()

if   position=='up':
    context.moveObjectsUp(id)
elif position=='down':
    context.moveObjectsDown(id)
elif position=='top':
    context.moveObjectsToTop(id)
elif position=='bottom':
    context.moveObjectsToBottom(id)
# order folder by field
# id in this case is the field
elif position=='ordered':
    context.orderObjects(id)

context.plone_utils.reindexOnReorder(context)

msg=_(u'Item\'s position has changed.')
context.plone_utils.addPortalMessage(msg)

new_context = context.portal_cache_settings
pt = context.portal_type
path = ''

if pt == config.TOOL_TYPE:
    path = 'cache_policy_config'
else:
    new_context = new_context.getDisplayPolicy()
    if pt == config.RULEFOLDER_TYPE:
        path = 'rules'
    elif pt == config.HEADERSETFOLDER_TYPE:
        path = 'headersets'

target = '%s/%s' %(new_context.absolute_url(), path)
return context.REQUEST.RESPONSE.redirect(target)

