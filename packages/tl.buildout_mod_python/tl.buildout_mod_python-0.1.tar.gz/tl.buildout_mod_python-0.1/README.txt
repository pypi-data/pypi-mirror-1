======================
tl.buildout_mod_python
======================


This is a `zc.buildout`_ recipe for setting up the `mod_python`_ module for
the `Apache web server`_. It is designed to work together with the
`tl.buildout_apache`_ recipes.

This recipe appears to be reliable, but the feature set is basically
determined by the author's immediate needs. Don't hesitate to send questions,
bug reports, suggestions, or patches to <thomas@thomas-lotze.de>.


Options
=======

A buildout part created by this recipe serves as a config part to be used in a
``tl.buildout_apache:root`` section. It adds configuration directives to load
the mod_python shared module and configure the Python interpreters' module
search path.

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
        "httpd". This can either be a part that uses the
        ``tl.buildout_apache:root`` recipe, or a section that describes a
        system-wide installation. It must export the "apxs-path" option.

    :python:
        The name of a buildout section for a Python installation, defaults to
        the Python section used by the "buildout" part. It must export the
        "executable" option.

    ..

    :eggs:
        Specifications of eggs to be available on mod_python's default Python
        path.

    :find-links:
        See the zc.recipe.egg documentation.

    :index:
        See the zc.recipe.egg documentation.

    :extra-paths:
        Non-egg paths to be included in mod_python's default Python path.

    ..

    :config-parts:
        Names of buildout sections with further configuration. See the
        ``tl.buildout_apache:root`` recipe.

Exported options:
    :so-path:
        Absolute file system path to the ``mod_python.so`` shared module.

    :lib-dir:
        Absolute file system path to the Python library directory that
        contains the ``mod_python`` package.

    :path-list:
        A Python list literal to be used in ``PythonPath`` Apache server
        configuration directives. It contains the paths to the configured eggs
        and all of the configured extra paths.

    :extra-config:
        A piece of Apache server configuration that loads the mod_python
        shared module and sets mod_python's default Python path.


.. _`zc.buildout`: http://www.zope.org/DevHome/Buildout/

.. _`mod_python`: http://www.modpython.org/

.. _`Apache web server`: http://httpd.apache.org/

.. _`tl.buildout_apache`: http://www.python.org/pypi/tl.buildout_apache
