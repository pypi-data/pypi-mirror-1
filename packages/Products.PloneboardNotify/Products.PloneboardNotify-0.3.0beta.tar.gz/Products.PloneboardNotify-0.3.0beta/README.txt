What is this?
=============

An event based Plone product.
Add some configuration to your Plone site for sending email on new messages or replies
added on forums.

You also need `Ploneboard`__ product to be installed.

__ http://pypi.python.org/pypi/Products.Ploneboard

Plone 2.5
---------

Yes, this is done to be compatible with Plone 2.5 and older versions of Ploneboard.
To install this for Plone 2.5 just copy the *PloneboardNotify* directory in the *Products* directory
provided by older Zope releases.

TODO
----

* Current version support global configuration and forum specific ones; the long-term
  plan wanna reach also forum area configurations.
* Also manipulate the FROM part of the mail, configurable globally, for single forum, etc.
* Forum outside the Forum Area are not supported by the configuration UI.
* Add user info to notification?
* A complete, clean uninstall procedure that remove all unwanted stuff.

