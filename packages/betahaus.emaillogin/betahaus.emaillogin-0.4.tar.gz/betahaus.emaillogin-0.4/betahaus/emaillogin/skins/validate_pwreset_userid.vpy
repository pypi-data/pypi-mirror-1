## Script (Python) "validate_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##bind state=state
##parameters=userid=None, password=None, password2=None, email=None
##title=Validate password
from Products.CMFCore.utils import getToolByName

found_userid = ''
if email:
    ec = getToolByName(context, 'email_catalog', None)
    if ec != None:
        user = ec({'email': email})
        if len(user) == 1:
            found_userid = user[0].userid
        else:
            context.plone_utils.addPortalMessage(pmf("Invalid email address."))
    else:
        for user in context.acl_users.getUsers():
            if email == user.getProperty('email'):
                found_userid = user.getId()                
                break
        else:
            context.plone_utils.addPortalMessage(pmf("Invalid email address."))

if (found_userid and userid) and (found_userid != userid):
    state.setError('userid', "Email and userid don't match please only specify one.")
    state.setError('email', "Email and userid don't match please only specify one.")

if found_userid and not userid:
    userid = found_userid
    context.REQUEST.set('userid', userid)
    
# Determine if we're checking userids or not
pw_tool = getToolByName(context, 'portal_password_reset')
if not pw_tool.checkUser():
    return state

if not userid and not email:
    state.setError('userid', 'This field is required')
    state.setError('email', 'This field is required')
    
if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state
