tranchitella.recipe.wsgi
========================

This recipe creates a `paste.deploy`_ entry point for mod_wsgi_.

Usage
-----

This is a minimal ''buildout.cfg'' file which creates a WSGI script mod_wsgi
can use::

    [buildout]
    parts = wsgi

    [wsgi]
    recipe = tranchitella.recipe.wsgi
    eggs = myapplication
    config-file = ${buildout:directory}/etc/deploy.ini
    environ =
        CHAMELEON_CACHE=true
        CHAMELEON_STRICT=true

This will create a small python script in the bin directory called ''wsgi''
which mod_wsgi can load. You can also use the optional ''extra-paths'' option
to specify extra paths that are added to the python system path.

The apache configuration for this buildout looks like this:::

    WSGIScriptAlias /mysite /path/to/buildout/bin/wsgi

    <Directory /home/me/buildout>
        Order deny,allow
        Allow from all
    </Directory>

This recipe does not fully install packages, which means that console scripts
will not be created. If you need console scripts you can add a second buildout
part which uses `zc.recipe.egg`_ to do a full install.

.. _zc.buildout: http://pypi.python.org/pypi/zc.buildout
.. _paste.deploy: http://pythonpaste.org/deploy/
.. _mod_wsgi: http://code.google.com/p/modwsgi/
.. _zc.recipe.egg: http://pypi.python.org/pypi/zc.recipe.egg
