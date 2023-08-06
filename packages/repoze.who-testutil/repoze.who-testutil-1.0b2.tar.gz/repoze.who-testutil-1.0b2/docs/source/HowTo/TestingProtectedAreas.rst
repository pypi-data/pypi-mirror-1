*******************************************
Test protected areas without authentication
*******************************************

Once your authentication middleware is prepared to skip authentication 
when explicitly requested, as described in the previous section, we'll be ready
to test the protected areas independently of the :mod:`repoze.who` 
identifiers, authenticators and challengers used.


The test configuration
======================

If you don't already have a test config file (often called ``test.ini``),
then you should create one. It's not strictly necessary, but we're going to
use it in this HOWTO.

In your ``test.ini`` file (or whatever you call it), let's define a new
application called ``main_without_authn``, which will be the same ``main``
application but without authentication:

.. code-block:: ini

    [DEFAULT]
    # (...)
    
    # Your main application:
    [app:main]
    use = config:main_configuration.ini
    
    # Your main application without authentication:
    [app:main_without_authn]
    use = main
    skip_authentication = True


The base test case
==================

Next, it's time to create a base class for your test cases, which will set
your application up without authentication (using the test configuration file
we created above).

If you've ever created one, you'll notice this one is a little special (hint:
see line #12):

.. code-block:: python
    :linenos:

    from unittest import TestCase
    
    from paste.deploy import loadapp
    from webtest import TestApp
    
    # Set the path to your configuration directory here:
    conf_dir = '/path/to/configuration/dir'
    
    class TestProtectedAreas(TestCase):
    
        def setUp(self):
            wsgiapp = loadapp('config:test.ini#main_without_authn',
                              relative_to=conf_dir)
            self.app = TestApp(wsgiapp)

Say it's defined in ``yourapplication.tests.base``.


A sample test case
==================

Finally we're ready to create our first test case for a protected area!

And all you have to do is extend ``TestProtectedAreas`` and test your
application as you'd expect:

.. code-block:: python
    :linenos:
    
    from yourapplication.tests.base import TestProtectedAreas
    
    class TestControlPanel(TestProtectedAreas):
        """Test case for the control panel at ``/panel``"""
        
        def test_index_as_admin(self):
            """Administrators can access the panel"""
            environ = {'REMOTE_USER': 'admin'}
            resp = self.app.get('/panel/', extra_environ=environ, status=200)
            assert "some text" in resp.body
        
        def test_index_as_normal_user(self):
            """Regular users shouldn't access the panel"""
            environ = {'REMOTE_USER': 'foobar'}
            self.app.get('/panel/', extra_environ=environ, status=403)
        
        def test_index_as_anonymous(self):
            """Anonymous users must not access the panel"""
            self.app.get('/panel/', status=401)

Now some comments about the test case above:

#. Every time you need to forge authentication, you should do it the standard
   way: Setting the user name in ``environ['REMOTE_USER']`` (or whatever you
   use) and then pass the fake environment to ``webtest.TestApp`` instance when
   you make a request. See lines 8-9 and 14-15.
#. If you want to act as an anonymous user, don't set 
   ``environ['REMOTE_USER']``. See line 19.
#. It's highly recommended to set the HTTP status code you expect to get when
   you make a request. See lines 9, 15 and 19. Keep in mind the meaning of the
   200, 401 and 403 HTTP status codes:
   
   * 200: Authorization was granted and the request was processed with no
     problems at all.
   * 401: Authorization was denied, but authenticating *could* help to gain
     access. This is used when the user is anonymous.
   * 403: Authorization was denied and authentication *won't* help to gain
     access. This is mostly used when the user is *not* anonymous.
   * When authorization to a given resource is denied to *everybody*
     (anonymous or authenticated), the 403 HTTP status code must be used.
