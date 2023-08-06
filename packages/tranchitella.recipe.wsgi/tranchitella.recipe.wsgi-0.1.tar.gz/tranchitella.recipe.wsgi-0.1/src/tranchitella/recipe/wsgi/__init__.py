# tranchitella.recipe.wsgi
# Copyright (C) 2008-2010 Tranchitella Kft. <http://tranchtella.eu>

import logging
import os
import string

from zc.buildout.easy_install import scripts
from zc.recipe.egg.egg import Eggs


WRAPPER_TEMPLATE = """\
import sys
sys.path[0:0] = [
    %(syspath)s,
]
%(environ)s
from paste.deploy import loadapp
application = loadapp("config:%(config)s")
"""


class Recipe(object):
    """Buildout recipe: tranchitella.recipe.wsgi:default"""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.options['eggs'] += '\nPasteDeploy'

    def install(self):
        egg = Eggs(self.buildout, self.options["recipe"], self.options)
        requirements, ws = egg.working_set()
        path = [pkg.location for pkg in ws]
        extra_paths = self.options.get('extra-paths', '')
        extra_paths = extra_paths.split()
        path.extend(extra_paths)
        environ = self.options.get('environ')
        if environ:
            environ = filter(None, environ.splitlines())
            environ = '\nimport os\n' + ''.join([
                "os.environ['%s'] = '%s'\n" % \
                    tuple(map(string.strip, i.split('=', 1))) \
                for i in environ if '='  in i])
        output = WRAPPER_TEMPLATE % dict(
            config=self.options["config-file"], environ=environ,
            syspath=",\n    ".join((repr(p) for p in path)))
        location = self.buildout["buildout"]["bin-directory"]
        target = os.path.join(location, "wsgi")
        open(target, "wt").write(output)
        os.chmod(target, 0755)
        self.options.created(target)
        return self.options.created()

    def update(self):
        pass
