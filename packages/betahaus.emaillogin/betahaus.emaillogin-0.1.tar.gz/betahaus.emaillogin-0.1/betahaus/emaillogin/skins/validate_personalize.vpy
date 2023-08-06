## Controller Python Script "validate_personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=email=''
##title=validates user preferences

from Products.CMFPlone import PloneMessageFactory as _

portal = context.portal_url.getPortalObject()

def isMemberEmailAllowed(email):
    if len(email) < 1:
        return False
    acl = portal.acl_users
    for user in acl.getUsers():
        if email == user.getProperty('email'):
            return False
    return True

if not isMemberEmailAllowed(email):
    state.setError('email',
                   _(u'The email you selected is already in use or is not valid. Please use another.'),
                   'email_invalid' )

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')

return state
