*****************************
Reconfigure :mod:`repoze.who`
*****************************

Now that you have :mod:`repoze.who` working, it's time to change its setup
slightly in order for us to skip authentication while testing protected areas.

The way to change it depends on the way you configure :mod:`repoze.who`:


Via Python code
===============

If the PasteDeploy factory for your application looks like this::

    from repoze.who.middleware import PluggableAuthenticationMiddleware
    
    def make_application(global_config, **local_conf):
        # (...)
        app = PluggableAuthenticationMiddleware(
            app,
            identifiers,
            authenticators,
            challengers,
            mdproviders,
            classifier,
            challenge_decider)
        # (...)
        return app

You should replace 
:class:`repoze.who.middleware.PluggableAuthenticationMiddleware` with
:func:`repoze.who.plugins.testutil.make_middleware`::

    from repoze.who.plugins.testutil import make_middleware
    
    def make_application(global_config, **local_conf):
        # (...)
        app = make_middleware(
            local_conf.get('skip_authentication'),
            app,
            identifiers,
            authenticators,
            challengers,
            mdproviders,
            classifier,
            challenge_decider)
        # (...)
        return app


.. attention::
    Note that :func:`repoze.who.plugins.testutil.make_middleware` receives one
    more argument, before ``app``.


Via :mod:`repoze.what`
----------------------

TODO


Via .ini file
=============

If the PasteDeploy factory for your application looks like this::

    from repoze.who.config import make_middleware_with_config
    
    def make_application(global_config, **local_conf):
        # (...)
        app = make_middleware_with_config(
            app,
            global_conf,
            local_conf['who.config_file'],
            local_conf['who.log_file'],
            local_conf['who.log_level'])
        # (...)
        return app

You should replace 
:class:`repoze.who.config.make_middleware_with_config` with
:func:`repoze.who.plugins.testutil.make_middleware_with_config`::

    from repoze.who.plugins.testutil import make_middleware_with_config
    
    def make_application(global_config, **local_conf):
        # (...)
        app = make_middleware_with_config(
            app,
            global_conf,
            local_conf['who.config_file'],
            local_conf['who.log_file'],
            local_conf['who.log_level'],
            skip_authentication=local_conf.get('skip_authentication'))
        # (...)
        return app


.. attention::
    Note that :func:`repoze.who.plugins.testutil.make_middleware_with_config`
    receives one more argument: ``skip_authentication``.

--------------

.. tip::
    You may want to run your application now to check that, so far, nothing
    seems to have changed.
