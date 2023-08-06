from AccessControl.Permissions import manage_users as ManageUsers
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin

from Products.CMFCore.DirectoryView import registerDirectory
from config import globals

from betahaus.emaillogin import config

from plugins import emaillogin
registerMultiPlugin(emaillogin.EmailLogin.meta_type)

import logging
logger = logging.getLogger(config.PROJECTNAME)

# Register skins directory
registerDirectory('skins', globals)



def initialize(context):
    context.registerClass(emaillogin.EmailLogin,
                                permission=ManageUsers,
                                constructors=
                                        (emaillogin.manage_addEmailLoginPlugin,
                                        emaillogin.addEmailLoginPlugin),
                                visibility=None,
                                icon="www/email.png")

    def reindex_after(func):
        logger.info('Adding reindex-after wrapper for custom email catalog to %s.%s' % (func.__module__,func.__name__))
        def indexer(*args, **kwargs):
            context = args[0]
            value = func(*args, **kwargs)
            try: context.email_catalog.reindexObject(context.portal_membership.getMemberById(context.getId()))
            except: pass
            return value
        return indexer
    
    # These two monky pathces could probably be done in a better way, that does not need patching.
    # maybe some kind of subscriber when the user preferences are updated?
    # If anyone looking at this know of a way to catch when a users properties has changed, 
    # please let me know! ;) 
    from Products.PlonePAS.plugins.ufactory import PloneUser
    PloneUser.setProperties = reindex_after(PloneUser.setProperties)

    from Products.CMFCore.MemberDataTool import MemberData    
    MemberData.notifyModified = reindex_after(MemberData.notifyModified)
        
        