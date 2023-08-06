***************************
**repoze.who-testutil** API
***************************

.. module:: repoze.who.plugins.testutil
    :synopsis: Test utilities for repoze.who-powered applications
.. moduleauthor:: Gustavo Narea <me@gustavonarea.net>


Authentication middleware
=========================

.. autoclass:: AuthenticationForgerMiddleware
    :members: __init__

Middleware makers
-----------------

.. autofunction:: make_middleware

.. autofunction:: make_middleware_with_config


:mod:`repoze.who` plugins
=========================

.. autoclass:: AuthenticationForgerPlugin
    :members: __init__, identify, remember, forget, authenticate, challenge
