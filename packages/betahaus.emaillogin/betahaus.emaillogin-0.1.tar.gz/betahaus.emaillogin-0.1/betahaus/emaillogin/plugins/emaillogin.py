from zope.interface import implements

from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements

from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from betahaus.emaillogin.interfaces import IEmailLoginPlugin



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

    # IExtractionPlugin implementation
    def extractCredentials(self, request):
        login=request.get("__ac_name", None)
    
        if login is None or '@' not in login:
            return {}
        
        pas = self._getPAS()
        for user in pas.getUsers():
            if login == user.getProperty('email'):
                login = user.getId()
                request.set("__ac_name", login)
        
                password=request.get("__ac_password", None)
                return { "login" : login, "password" : password }
        
        return {}
    
    
classImplements(EmailLogin, IExtractionPlugin)
