from zope.interface import implements

from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements

from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from betahaus.emaillogin.interfaces import IEmailLoginPlugin
from betahaus.emaillogin.config import CATALOG_ID

manage_addEmailLoginPlugin = PageTemplateFile("../www/emailloginAdd", globals(), 
                __name__="manage_addEmailLoginPlugin")

def addEmailLoginPlugin(self, id, title='', REQUEST=None):
    """Add a EmailLogin plugin to a Pluggable Authentication Service.
    """
    p=EmailLogin(id, title)
    self._setObject(p.getId(), p)

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect("%s/manage_workspace"
                "?manage_tabs_message=EmailLogin+plugin+added." %
                self.absolute_url())


class EmailLogin(BasePlugin):
    
    meta_type = "EmailLogin plugin"
    security  = ClassSecurityInfo()
    implements(IEmailLoginPlugin)
    
    def __init__(self, id, title=None):

        self._id = self.id = id
        self.title = title


    def _get_username_from_email(self, request, login_email):
        """Returns the username for a given email. If no user found it returns None"""
        email_catalog = getToolByName(self, CATALOG_ID, None)
        if email_catalog != None:
            user = email_catalog(email=login_email)
            if len(user) == 1:
                return user[0].userid
        else:
            pas = self._getPAS()
            for user in pas.getUsers():
                if login_email == user.getProperty('email'):
                    return user.getId()


    # IExtractionPlugin implementation
    def extractCredentials(self, request):
        login_email = request.get("__ac_name", None).strip()
    
        if login_email is None or '@' not in login_email:
            return {}
        
        login_name = self._get_username_from_email(request, login_email)
        if login_name is not None:
            request.set("__ac_name", login_name)
            password=request.get("__ac_password", None)
            return { "login" : login_name, "password" : password }
        return {}
    
    
classImplements(EmailLogin, IExtractionPlugin)
