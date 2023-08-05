==================
tl.buildout_apache
==================


This is a collection of `zc.buildout`_ recipes for setting up an `Apache web
server`_ environment. It provides the following entry points:

:httpd:
    Builds the Apache HTTP server software from source.

:root:
    Configures an Apache server root (an instance in Zope speak).

These recipes appear to be reliable, but the feature set is basically
determined by the author's immediate needs. Don't hesitate to send questions,
bug reports, suggestions, or patches to <thomas@thomas-lotze.de>.


The build recipe: ``tl.buildout_apache:httpd``
==============================================

None of the options described below are required: they either have sensible
defaults or are computed by the recipe. You may override any of them.

Configuration options:
    :url:
        Where to get the source distribution.

    :md5sum:
        MD5 checksum of the source distribution.

    :extra-options:
        Extra configure options, appended to the ``./configure`` command line.

    :extra-vars:
        Extra environment variables for ``./configure``, ``make``, and ``make
        install`` calls.

Exported options:
    :httpd-path:
        Absolute file system path to the ``httpd`` executable.

    :envvars-path:
        Absolute file system path to the ``envvars`` script.

    :apxs-path:
        Absolute file system path to the ``apxs`` executable.

    :module-dir:
        Absolute file system path to the shared modules directory.

    :htdocs:
        Absolute file system path to the document directory distributed with
        the Apache server, containing the welcome page.

.. CAUTION::
    If you plan to embed Python 2.4 into Apache, e.g. by using `mod_python`_,
    make sure you have version 1.95.8 of the expat library and its development
    files installed on your system when running the build recipe. Otherwise
    Apache will use its own, older version of expat which may later on lead to
    segmentation faults due to two incompatible expat versions being
    used in the same process.

    This is a temporary measure of caution since Python 2.5 and above avoid
    the conflict. Therefore, the recipe doesn't step out of its way to make
    sure about the expat version programmatically.


The server root recipe: ``tl.buildout_apache:root``
===================================================

An Apache server process configured with this recipe will run the "prefork"
multi-processing module.

None of the options described below are required: they either have sensible
defaults or are computed by the recipe. You may override any of them.

Configuration options:
    :httpd:
        The name of a buildout section for an httpd installation, defaults to
        "httpd". It must export the following options:

        - httpd-path
        - envvars-path
        - apxs-path
        - module-dir

    ..

    :ulimit:
        Command to increase the maximum allowed number of file descriptors per
        child process.

    :sysconf-dir:
        Absolute file system path to the system configuration directory, e.g.
        ``/etc``. It is used to find MIME configuration files.

    :lynx-path:
        Absolute file system path to the ``lynx`` executable.

    ..

    :user:
        User name to run the server as (if starting it as root).

    :group:
        Group name to run the server as (if starting it as root).

    :listen:
        Interfaces and ports to listen at, such as 127.0.0.1:80.

    :modules:
        Names of shared modules to load, e.g. "dir" or "rewrite". Includes
        authz_host by default.

    ..

    :servername:
        Server name to announce, e.g. localhost:80.

    :serveradmin:
        E-mail address of the server administrator.

    :htdocs:
        Absolute file system path to the document root.

    :cgi-bin:
        Absolute file system path to the CGI library directory.

    :log-dir:
        File system path to the log directory to be created, either absolute
        or relative to the server root.

    :extra-env:
        Additional variables to be exported to httpd's environment.
        Each line is of the form "``<name>=<value>``", e.g.
        "``PATH=/opt/foo:$PATH``".

    :extra-config:
        Arbitrary multi-line server configuration.

    ..

    :config-parts:
        Names of buildout sections with further configuration. The following
        options exported from config parts are recognized:

        - config-parts (included recursively)
        - modules
        - extra-env
        - extra-config


.. _`zc.buildout`: http://www.zope.org/DevHome/Buildout/

.. _`Apache web server`: http://httpd.apache.org/

.. _`mod_python`: http://www.modpython.org/
