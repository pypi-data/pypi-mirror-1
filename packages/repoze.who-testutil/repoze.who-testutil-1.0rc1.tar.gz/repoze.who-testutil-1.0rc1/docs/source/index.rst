*********************************************************
Test utilities for :mod:`repoze.who`-powered applications
*********************************************************

:Author: Gustavo Narea.
:Latest release: |release|

.. topic:: Overview

    **repoze.who-testutil** is a :mod:`repoze.who` plugin which modifies
    :mod:`repoze.who`'s original middleware to make it easier to forge
    authentication, without bypassing identification (this is, running the
    metadata providers).
    
    It's been created in order to ease testing of :mod:`repoze.who`-powered
    applications, in a way independent of the identifiers, authenticators
    and challengers used originally by your application, so that you won't
    have to update your test suite as your application grows and the
    authentication method changes.


The problems
============

While testing protected areas, you have to authenticate first
-------------------------------------------------------------

And that's absolutely specific to the identifiers/challengers you're using.

For example, if you're using `WebTest <http://pythonpaste.org/webtest/>`_ and 
the :class:`repoze.who.plugins.form.RedirectingFormPlugin` plugin, you have to
get the login handler at the beginning of each test that covers situations 
where the user is authenticated::
    
    class TestControlPanel(TestCase):
        
        def setUp(self):
            from paste.deploy import loadapp
            from webtest import TestApp
            wsgiapp = loadapp('config:test.ini')
            self.app = TestApp(wsgiapp)
        
        def test_index_as_admin(self):
            # First of all, let's log in the RedirectingFormPlugin way:
            self.app.get('/login_handler?login=admin&password=somepass')
            # Now that we're authenticated, let's request the control panel:
            resp = self.app.get('/panel/', status=200)
            assert "some text" in resp.body
        
        def test_index_as_normal_user(self):
            # First of all, let's log in the RedirectingFormPlugin way:
            self.app.get('/login_handler?login=foo&password=bar')
            # Now that we're authenticated, let's request the control panel:
            self.app.get('/panel/', status=302)
            # We got a 302 redirection. This is the RedirectingFormPlugin way 
            # to let us know that authorization was denied.
        
        def test_index_as_anonymous(self):
            # Let's request the control panel as an anonymous user:
            self.app.get('/panel/', status=302)
            # We got a 302 redirection. This is the RedirectingFormPlugin way 
            # to let us know that authorization was denied.

This is, we end up testing protected areas in a way that is totally tied to
the :mod:`repoze.who` identifiers and challengers you intend to use initially.
If the are replaced later, you will have to update many of your tests (*most*
of them, possibly).


Or, while testing protected areas, you have to forge authentication
-------------------------------------------------------------------

But that will bypass identification: The metadata providers won't get run, so
this is not an option if your application relies on them::
    
    class TestControlPanel(TestCase):
        
        def setUp(self):
            from paste.deploy import loadapp
            from webtest import TestApp
            wsgiapp = loadapp('config:test.ini')
            self.app = TestApp(wsgiapp)
        
        def test_index_as_admin(self):
            # Let's forge authentication:
            environ = {'REMOTE_USER': 'admin'}
            resp = self.app.get('/panel/', extra_environ=environ, status=200)
            assert "some text" in resp.body

This seems like the best way to test a protected area, and you may expect it
to work, but unfortunately it won't:

If the controller action for ``'/panel/'`` assumes that if the user is
authenticated, her full name will be available in 
``identity['full_name']``, then your test will be broken because such an item
won't be defined in the ``identity`` dict -- even worse: the ``identity`` dict
won't even be defined because :mod:`repoze.who` will assume that, because
``environ['REMOTE_USER']`` is set, it won't be necessary to run its middleware.


The solution
============

It's absolutely unnecessary to test authentication every time you test a
protected area in your Web site; authentication should be tested *once* and
*separately*. This is, to test a protected area in a Web site, only
*identification* and *authorization* are required, not authentication.

With **repoze.who-testutil**, you'll be able to write tests for protected areas
the way you'd expect::
    
    class TestControlPanel(TestCase):
        
        def setUp(self):
            from paste.deploy import loadapp
            from webtest import TestApp
            wsgiapp = loadapp('config:test.ini')
            self.app = TestApp(wsgiapp)
        
        def test_index_as_admin(self):
            environ = {'REMOTE_USER': 'admin'}
            resp = self.app.get('/panel/', extra_environ=environ, status=200)
            assert "some text" in resp.body
        
        def test_index_as_normal_user(self):
            environ = {'REMOTE_USER': 'foobar'}
            # The 403 HTTP status code means that authorization has been
            # denied, while we are aware of who the user is:
            self.app.get('/panel/', status=403)
        
        def test_index_as_anonymous(self):
            # Let's request the control panel as an anonymous user.
            # The 401 HTTP status code means that authorization has been
            # denied, although it may be granted if the user logs in:
            self.app.get('/panel/', status=401)

As you may have noticed, these tests are absolutely independent of the
:mod:`repoze.who` plugins used. And the best of all: The :mod:`repoze.who`
middleware won't be skipped, so the ``identity`` dict will be defined as usual!

Then if you want to test authentication, you can do it once and separately --
and if the authentication method changes over time, you'd just have to update
a few tests, instead of all the tests that cover protected areas.


How to install
==============

It requires :mod:`repoze.who` only, and you can install them with
``easy_install``::
    
    easy_install repoze.who-testutil


Documentation
=============

.. toctree::
    :maxdepth: 2
    
    HowTo/index
    API


Support and development
=======================

The prefered place to ask questions is the `Repoze mailing list 
<http://lists.repoze.org/listinfo/repoze-dev>`_ or the `#repoze 
<irc://irc.freenode.net/#repoze>`_ IRC channel. Bugs reports and feature 
requests should be sent to `the issue tracker of the Repoze project 
<http://bugs.repoze.org/>`_.

The development mainline is available at the following Subversion repository::

    http://svn.repoze.org/whoplugins/whotestutil/trunk/


Releases
--------

.. toctree::
    :maxdepth: 2
    
    News
