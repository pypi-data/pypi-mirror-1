from AccessControl.Permissions import manage_users as ManageUsers
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin

from Products.CMFCore.DirectoryView import registerDirectory
from config import globals

from betahaus.emaillogin import config

from plugins import emaillogin
registerMultiPlugin(emaillogin.EmailLogin.meta_type)

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

