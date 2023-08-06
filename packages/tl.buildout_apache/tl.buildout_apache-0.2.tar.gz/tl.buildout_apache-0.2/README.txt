==================
tl.buildout_apache
==================


This is a collection of `zc.buildout`_ recipes for setting up an `Apache web
server`_ environment. It provides the following entry points:

:httpd:
    Builds the Apache HTTP server software from source.

:modpython:
    Builds the Apache/Python integration module from source.

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

    :cgi-bin:
        Absolute file system path to the document cgi-bin distributed with
        the Apache server, containing test and demo scripts.

.. NOTE::
    Building httpd has been tested without any compiler or linker flags set
    (``CFLAGS`` and ``LDFLAGS`` environment variables). It has also been
    observed that httpd may not build with certain linker flags. If the httpd
    recipe fails with a warning from the ``make`` run, try again with the
    above variables unset.

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


The mod_python recipe: ``tl.buildout_apache:modpython``
=======================================================

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

    ..

    :httpd:
        The name of a buildout section for an httpd installation, defaults to
        "httpd". It must export the "apxs-path" option.

    :python:
        The name of a buildout section for a Python installation, defaults to
        the Python section used by the "buildout" part. It must export the
        "executable" option.

    :virtualenv:
        Whether to create a virtual Python environment from the Python
        installation given. Defaults to "true". The recipe needs to write to
        its Python's site packages, so don't turn this off unless the
        ``python`` option describes a writable (probably virtual) Python
        installation that this part should share.

Exported options:

    :modpython:
        Absolute file system path to the ``mod_python.so`` shared module.

    :executable:
        The Python executable that should be used for installing eggs.


The server root recipe: ``tl.buildout_apache:root``
===================================================

An Apache server process configured with this recipe will run the "prefork"
multi-processing module.

None of the options described below are required: they either have sensible
defaults or are computed by the recipe. You may override any of them.

The configuration of an Apache root may be split across a number of buildout
sections in order to allow for semantic grouping, re-use etc. These sections
are called config parts and are usually just configuration sections without
the need of a buildout recipe. Config parts work recursively.

Configuration options that apply only to the root part:

    :httpd:
        The name of a buildout section for an httpd installation, defaults to
        "httpd". It must export the following options:

        - httpd-path
        - envvars-path
        - module-dir

        Other options, if present, are used to provide default values for the
        root part's own options:

        - htdocs
        - cgi-bin

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

    ..

    :python:
        The name of a buildout section defining a mod_python installation.
        If not given, mod_python is not used. If present, the named section
        must export the following options:

        - modpython
        - executable

    ..

    :virtual-hosts:
        name=address pairs for configuring name-based virtual hosts. The name
        selects a config-part describing the host, the address is an IP
        address with an optional port, e.g. 127.0.0.1:80.

Configuration options that apply to both the root part and virtual hosts:

    :servername:
        Server name to announce, e.g. localhost:80. Mandatory for virtual
        hosts.

    :serveradmin:
        E-mail address of the server administrator.

    :htdocs:
        Absolute file system path to the document root, defaults to the value
        of the httpd part's ``htdocs`` option.

    :cgi-bin:
        Absolute file system path to the CGI library directory, defaults to
        the value of the https part's ``cgi-bin`` option.

    :log-dir:
        File system path to the log directory to be created, either absolute
        or relative to the server root.

    ..

    :index:
        See the zc.recipe.egg documentation.

Configuration options that apply to config-parts, including the root and
virtual host parts:

    :modules:
        Names of shared modules to load, e.g. "dir" or "rewrite". Includes
        authz_host by default. To specify the shared object path of a module,
        add an entry of the form "foo=path/to/foo.so". Paths are either
        absolute or considered relative to the httpd installation.

    :extra-env:
        Additional variables to be exported to httpd's environment.
        Each line is of the form "``<name>=<value>``", e.g.
        "``PATH=/opt/foo:$PATH``".

    :extra-config:
        Arbitrary multi-line server configuration.

    ..

    :eggs:
        Specifications of eggs to be added to the Python module search path
        available to code run by mod_python.

    :find-links:
        See the zc.recipe.egg documentation.

    :extra-paths:
        Non-egg paths to be included in the Python module search path.

    ..

    :config-parts:
        Names of buildout sections with further configuration. The following
        options exported from config parts are recognized:

        - config-parts (included recursively)
        - modules
        - extra-env
        - extra-config
        - eggs
        - find-links
        - extra-paths


Change log
==========

For a continuously updated change log, see
<https://svn.thomas-lotze.de/repos/public/tl.buildout_apache/trunk/CHANGES.txt>.


Contact
=======

This package is written by Thomas Lotze. Please contact the author at
<thomas@thomas-lotze.de> to provide feedback, suggestions, or contributions.

See also <http://www.thomas-lotze.de/en/software/buildout-recipes/>.


.. _`zc.buildout`: http://www.zope.org/DevHome/Buildout/

.. _`Apache web server`: http://httpd.apache.org/

.. _`mod_python`: http://www.modpython.org/


.. Local Variables:
.. mode: rst
.. End:
