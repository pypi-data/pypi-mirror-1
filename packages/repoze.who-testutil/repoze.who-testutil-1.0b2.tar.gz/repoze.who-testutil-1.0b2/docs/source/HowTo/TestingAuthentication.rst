*********************************
Test authentication independently
*********************************

You may want to test authentication in order to make sure :mod:`repoze.who` is
working properly within your application, which is also known as "integration
tests".

This section will help you test authentication *only*, based on the 
``test.ini`` file defined in the previous section.


The test case
=============

In most situations, a single test case will be enough to test authentication
exhaustively.

While testing authentication, you have to check the behavior of your
application in the following situations:

* When authorization is denied with the 401 HTTP status code: :mod:`repoze.who`
  must catch it and run the challenger(s) you specified. This is, when the user
  is forced to log in.
* When the user logs in voluntarily.
* When the user logs out.

So, your test case for authentication should be made up of at least three
tests.

.setUp()
--------

The ``.setUp()`` method of this test case should perform the traditional
procedure to test applications with WebTest:

.. code-block:: python
    :linenos:

    from unittest import TestCase
    
    from paste.deploy import loadapp
    from webtest import TestApp
    
    # Set the path to your configuration directory here:
    conf_dir = '/path/to/configuration/dir'
    
    class TestAuthentication(TestCase):
        """Test case for the authentication sub-system in the application"""
    
        def setUp(self):
            appconfig = loadapp('config:test.ini', relative_to=conf_dir)
            self.app = TestApp(appconfig)
        
        # (...)

Note that we're using the ``main`` application, which doesn't skip 
authentication. This way, authentication will behave the same way as in a
production environment.


Sample test case
================

Say we have the following :mod:`repoze.who` configuration file:

.. literalinclude:: ../_static/sample-who.ini
    :language: ini

The following test case illustrates how you could test authentication for that
setup::

    from unittest import TestCase
    
    from paste.deploy import loadapp
    from webtest import TestApp
    
    # Set the path to your configuration directory here:
    conf_dir = '/path/to/configuration/dir'
    
    class TestAuthentication(TestCase):
        """Test case for the authentication sub-system in the application"""
    
        def setUp(self):
            wsgiapp = loadapp('config:test.ini', relative_to=conf_dir)
            self.app = TestApp(wsgiapp)
        
        def test_forced_login(self):
            """
            Anonymous users should be redirected to the login form when they
            request a protected area.
            
            """
            # Requesting a protected area as anonymous:
            resp = self.app.get('/panel/', status=302)
            assert resp.location.startswith('http://localhost/login?')
            # Being redirected to the login page:
            login_page = resp.follow(status=200)
            login_form = login_page.form
            login_form['login'] = 'gustavo'
            login_form['password'] = 'hola'
            # Submitting the login form:
            login_handler = login_form.submit(status=302)
            # We should be redirected to the initially requested page:
            assert login_handler.location == 'http://localhost/panel/'
            # Checking that the user was correctly authenticated:
            initial_page = login_handler.follow(status=200)
            assert 'auth_tkt' in initial_page.request.cookies, \
                   "Session cookie wasn't defined: %s" % initial_page.request.cookies
        
        def test_voluntary_login(self):
            """Voluntary logins should work perfectly"""
            # Requesting the login form:
            login_page = self.app.get('/login', status=200)
            login_form = login_page.form
            login_form['login'] = 'gustavo'
            login_form['password'] = 'hola'
            # Submitting the login form:
            login_handler = login_form.submit(status=302)
            assert login_handler.location == 'http://localhost/'
            # Checking that the user was correctly authenticated:
            initial_page = login_handler.follow(status=200)
            assert 'auth_tkt' in initial_page.request.cookies, \
                   "Session cookie wasn't defined: %s" % initial_page.request.cookies
        
        def test_logout(self):
            """Users should be logged out correctly"""
            # Logging in:
            self.app.get('/login_handler?login=gustavo&password=hola', status=302)
            # Checking that the user was correctly authenticated:
            home_page = self.app.get('/', status=200)
            assert 'auth_tkt' in home_page.request.cookies, \
                   "Session cookie wasn't defined: %s" % home_page.request.cookies
            # Now let's log out:
            self.app.get('/logout_handler', status=302)
            # Finally, let's check that the session cookie was destroyed after logout:
            home_page = self.app.get('/', status=200)
            assert home_page.request.cookies.get('auth_tkt') == '', \
                   "Session cookie wasn't deleted: %s" % home_page.request.cookies

Depending on your :mod:`repoze.who` plugins and the way you use them, you may
need more tests. In our example, it also makes sense to test what happens when
the user tries to log in with the wrong credentials.
