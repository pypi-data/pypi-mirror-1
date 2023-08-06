betahaus.emaillogin
====================

Contents
========

* `What is betahaus.emaillogin?`_
* `Installation`_
* `How it works`_
* `Performance`_
* `A quick word about buildout.eggnest`_
* `Change history`_
* `Contributors`_

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


Performance
-----------

The current default implementation does a lookup of the email by iterating over all of the PAS users until the 
corresponding email is found. This approach is fine for a large number of sites with a liberal number of users. 
It is however computationally expensive and slow when the number of users rise. If you experience performance issues
there is a GenericSetup profile called ``extended`` that can be applied. This extension adds a custom email->userid
catalog that enables faster userid look-up from email address.

The extended profile is applied via ``portal_setup`` -> ``Import`` -> select and apply profile ``Extended performance 
for EmailLogin Support``.

If you want to uninstall this extended profile just remove the ``email_catalog`` from the site root and emaillogin will 
fall back to default lookup implementation. 


A quick word about buildout.eggnest
-----------------------------------

`buildout.eggnest <http://pypi.python.org/pypi/buildout.eggnest/>`_ is an extension to buildout that enables you to auto load eggs. 
You only drop a .nestegg specification file into a predefined directory and it will get downloaded 
by buildout as if it was entered in the buildout configuration file. 
This way you don't have to edit the buildout config all the time.
The .nestegg specification file is normally made by the author of the egg.
More information at `http://pypi.python.org/pypi/buildout.eggnest/ <http://pypi.python.org/pypi/buildout.eggnest/>`_

