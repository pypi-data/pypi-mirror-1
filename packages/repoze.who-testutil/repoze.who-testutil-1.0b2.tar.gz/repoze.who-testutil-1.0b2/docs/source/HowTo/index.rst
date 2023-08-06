****************************************
How to test protected areas in Web sites
****************************************

.. topic:: Overview

    This guide will show you how to test protected areas and authentication,
    separately, using `PasteDeploy <http://pythonpaste.org/deploy/>`_,
    `WebTest <http://pythonpaste.org/webtest/>`_ and
    :mod:`repoze.who.plugins.testutil`.
    
    **I assume that you already have repoze.who working the way you want**, 
    configured via an Ini file or Python code. If not, please set it up first 
    using the :mod:`repoze.who` manual and then come back to this guide.
    
    Likewise, I also assume that you already have a `PasteDeploy configuration
    file <http://pythonpaste.org/deploy/#the-config-file>`_ for your
    application. It's not strictly necessary, but we're going to use it in
    this HOWTO.


Three steps are required to test protected areas and authentication
separately:

.. toctree::
    :maxdepth: 2
    
    Reconfiguring
    TestingProtectedAreas
    TestingAuthentication
