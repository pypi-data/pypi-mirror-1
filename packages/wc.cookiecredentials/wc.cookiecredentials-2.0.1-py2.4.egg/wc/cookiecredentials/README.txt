Cookie Credentials
==================

This package features a credentials plug-in for Zope's Pluggable
Authentication Utility (PAU) that

* challenges the user to enter username and password through a login
  form and

* saves those credentials to a cookie from which it can read them back
  at any later time.

In the latter point it is similar to the ``CookieAuthHelper`` from
Zope 2's PluggableAuthService (PAS).


Challenging the user
--------------------

Imagine you go to a page that anonymous users don't have access to:

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser("http://localhost/@@contents.html")

As you can see, the plug-in redirects you to the login page:

  >>> print browser.url
  http://localhost/@@loginForm.html?camefrom=http%3A%2F%2Flocalhost%2F%40%40contents.html


Logging in
----------

Now fill in the credentials and log in:

  >>> browser.getControl('User Name').value = 'admin'
  >>> browser.getControl('Password').value = 'secret'
  >>> browser.getControl('Log in').click()

We're now being redirected where we originally wanted to go:

  >>> print browser.url
  http://localhost/@@contents.html


Cookie
------

The cookie credentials plug-in has stored our credentials in a cookie.
Therefore, if we create a second browser object that doesn't have the
cookie, we will not be authenticated:

  >>> browser = Browser("http://localhost/@@contents.html")
  >>> print browser.url
  http://localhost/@@loginForm.html?camefrom=http%3A%2F%2Flocalhost%2F%40%40contents.html

If, however, we set the appropriate cookie, we can authenticate
ourselves:

  >>> import base64
  >>> cred = base64.encodestring('admin:secret')
  >>> browser.addHeader('Cookie', 'wc.cookiecredentials=%s' % cred)
  >>> browser.open("http://localhost/@@contents.html")
  >>> print browser.url  
  http://localhost/@@contents.html


Logging out
-----------

We can also manually destroy the cookie by invoking the logout page:

  >>> browser.open("http://localhost/@@logout.html")
  >>> print browser.headers['Set-Cookie']
  wc.cookiecredentials=deleted; ...
