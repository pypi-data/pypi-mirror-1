## Script (Python) "mail_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Mail a user's password
##parameters=


from Products.CMFPlone import PloneMessageFactory as pmf
REQUEST=context.REQUEST
portal = context.portal_url.getPortalObject()


email = REQUEST.get('email', None)
if email:
    if 'email_catalog' in portal.objectIds():
        user = portal.email_catalog({'email': email})
        if len(user) == 1:
            REQUEST.set('userid', user[0].userid)
        else:
            context.plone_utils.addPortalMessage(pmf("Invalid email address."))
            response = context.mail_password_form()
    else:
        for user in context.acl_users.getUsers():
            if email == user.getProperty('email'):
                REQUEST.set('userid', user.getId())                
                break
        else:
            context.plone_utils.addPortalMessage(pmf("Invalid email address."))
            response = context.mail_password_form()

userid = REQUEST.get('userid', '')
if userid != '':
    try:
        response = context.portal_registration.mailPassword(REQUEST['userid'], REQUEST)
    except ValueError, e:
        context.plone_utils.addPortalMessage(pmf(str(e)))
        response = context.mail_password_form()
        
return response
