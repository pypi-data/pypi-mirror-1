## Controller Python Script "validate_personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=users=[]
##title=validates user preferences

from Products.CMFPlone import PloneMessageFactory as _

portal = context.portal_url.getPortalObject()
member=context.portal_membership.getAuthenticatedMember()
member_email = member.getProperty('email')

def isMemberEmailAllowed(email, member_id):
    if len(email) < 1:
        return False
    
    if 'email_catalog' in portal.objectIds():
        user = portal.email_catalog({'email': email})
        if len(user) == 1:
            # the email was found check if
            if user[0].userid != member_id:
                return False
        if len(user) > 1:
            return False
        return True
    else:
        acl = portal.acl_users
        for user in acl.getUsers():
            user_email = user.getProperty('email')
            if member_id == user.id:
                continue
            if email == user_email:
                return False
        return True

for user in users:
    if hasattr(user, 'email') and not isMemberEmailAllowed(user.email, user.id):
        context.plone_utils.addPortalMessage(
                                           _(u'The email you selected is already in use, duplicate emails will break emaillogin for those users. You might want to consider using another email for user') + ' ' + user.id,
                                           'warning')


return state
