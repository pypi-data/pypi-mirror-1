betahaus.emaillogin
====================


What is betahaus.emaillogin?
----------------------------
The use of emailaddress are speading more and more but Plone does not 
have a convenient way to use a users registered email address to login.

``betahaus.emaillogin`` makes it possible to login using the email address
specified in the user profile. 

Plone has a very powerful and modifiable authentication system called 
Pluggable Authentication Service (PAS). As the name suggest the system 
is pluggable and thus can easily be extended by third-party products 
such as this.  


Installation
------------

buildout:
 - add ``betahaus.emaillogin`` entries to eggs and zcml in the appropriate buildout configuration file.
 - re-run buildout.
 - Install via portal_quickinstaller or Site Setup in plone
 
                
`buildout.eggnest <http://pypi.python.org/pypi/buildout.eggnest/>`_:
 - copy this `eggnest file <http://svn.plone.org/svn/collective/betahaus.emaillogin/buildout/src/betahaus.emaillogin.nestegg>`_ to your eggnest directory 
 - re-run buildout
 - Install via portal_quickinstaller or Site Setup in plone


How it works
------------

``betahaus.emaillogin`` is at installation put first in the list of 
extraction plugins. If an email address is specified and a corresponding 
user is found. The email address in the request is replaced with the
username and then simulates failed extraction to continue normal login procedure.


- Code repository: https://svn.plone.org/svn/collective/betahaus.emaillogin
- Nestegg url: http://svn.plone.org/svn/collective/betahaus.emaillogin/buildout/src/betahaus.emaillogin.nestegg
- Questions and comments to the author
