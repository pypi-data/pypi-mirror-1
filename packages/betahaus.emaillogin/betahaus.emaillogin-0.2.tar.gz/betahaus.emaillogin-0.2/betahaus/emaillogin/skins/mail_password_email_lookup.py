## Script (Python) "mail_password_email_lookup"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Mail a user's password
##parameters=

        

from Products.CMFPlone import PloneMessageFactory as pmf
REQUEST=context.REQUEST

email = REQUEST.get('email', None)
if email:
    for user in context.acl_users.getUsers():
        if email == user.getProperty('email'):
            REQUEST.set('userid', user.getId())
            break

return context.mail_password()
