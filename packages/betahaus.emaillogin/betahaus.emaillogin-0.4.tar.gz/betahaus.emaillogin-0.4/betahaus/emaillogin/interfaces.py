from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from zope.interface import Interface


class IEmailCatalog(Interface):
    """Custom catalog for faster emaillookup
    """

class IEmailLoginPlugin(IExtractionPlugin):
    
    def extractCredentials(request):
        """Looks for an email address in __ac_name, 
           finds the first user with that email and ex-changes the email with the username in the request.
           
           Always returns {} to simulate failed extraction this will trigger continued PAS extraction of credentials.  
        """
