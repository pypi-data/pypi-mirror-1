# tranchitella.recipe.fs
# Copyright (C) 2008-2010 Tranchitella Kft. <http://tranchtella.eu>

import os

from zc.buildout.easy_install import scripts


class Recipe(object):
    """Buildout recipe: tranchitella.recipe.fs:mkdir"""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

    def install(self):
        path = self.options['path']
        basedir, name = os.path.split(path)
        if not os.path.isdir(basedir):
            os.makedirs(basedir)
            self.options.created(basedir)
        data = open(self.options['template'], 'rb').read()
        options = self.options.copy()
        for k in options.keys():
            options[k] = ' '.join(options[k].split())
        open(path, 'wb').write(data % options)
        self.options.created(path)
        mode = int(self.options.get('mode', '06544'), 8)
        os.chmod(path, mode)
        return self.options.created()

    def update(self):
        self.install()
