from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin


class IEmailLoginPlugin(IExtractionPlugin):
    
    def extractCredentials(request):
        """Looks for an email address in __ac_name, 
           finds the first user with that email and ex-changes the email with the username in the request.
           
           Always returns {} to simulate failed extraction this will trigger continued PAS extraction of credentials.  
        """
