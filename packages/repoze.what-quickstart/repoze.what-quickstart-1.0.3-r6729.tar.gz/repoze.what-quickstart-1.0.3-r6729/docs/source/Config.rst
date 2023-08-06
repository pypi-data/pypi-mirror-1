.. _config:

*****************************************************
:mod:`repoze.what` Quickstart via configuration files
*****************************************************

.. versionadded:: 1.0.1

If you prefer to configure the quickstart plugin via Ini files instead of
Python code, that's possible as of version 1.0.1.

All the settings can be adjusted via configuration files, except passing
additional arguments to :mod:`repoze.who` (which will be possible in later
versions).

To use a configuration file instead of Python code, use
:func:`repoze.what.plugins.quickstart.add_auth_from_config` instead of
:func:`repoze.what.plugins.quickstart.setup_sql_auth`, like this::

    from repoze.what.plugins.quickstart import add_auth_from_config
    # (...)
    # "config_file" is the path to the configuration file that contains your
    # auth settings:
    application = add_auth_from_config(application, global_config, config_file)


Supported options
=================

In these configuration files you can set the arguments you would pass to
:func:`repoze.what.plugins.quickstart.setup_sql_auth`. For example, the sample
file below illustrates how you'd pass the arguments required by this function:

.. code-block:: ini
    
    [general]
    dbsession = your_project.model:DBSession
    
    [authentication]
    user_class = your_project.model:User
    
    [authorization]
    group_class = your_project.model:Group
    permission_class = your_project.model:Permission

While the file below illustrates how to pass the optional arguments as well,
including the so-called "translations":

.. code-block:: ini

    [general]
    dbsession = tests.fixture.model:DBSession
    
    [authentication]
    user_class = tests.fixture.model:User
    form_plugin = tests.fixture.misc_config:form_plugin
    form_identifies = True
    cookie_name = authntkt
    cookie_secret = you cannot see this
    login_url = /log-me-in
    login_handler = /handle-login
    post_login_url = /do-something-after-login
    logout_handler = /log-me-out
    post_logout_url = /do-something-after-logout
    login_counter_name = login_attempts
    
    [authorization]
    group_class = tests.fixture.model:Group
    permission_class = tests.fixture.model:Permission
    
    [translations]
    validate_password = check_it
    users = members
    user_name = member_name
    groups = teams
    group_name = team_name
    permissions = perms
    permission_name = perm_name


API
===

.. autofunction:: repoze.what.plugins.quickstart.add_auth_from_config

.. autoexception:: repoze.what.plugins.quickstart.BadConfigurationException

.. autoexception:: repoze.what.plugins.quickstart.MissingOptionError

.. autoexception:: repoze.what.plugins.quickstart.BadOptionError
