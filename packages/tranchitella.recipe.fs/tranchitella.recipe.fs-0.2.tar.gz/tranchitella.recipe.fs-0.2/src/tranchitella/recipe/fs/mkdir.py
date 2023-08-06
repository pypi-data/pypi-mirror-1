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
        for target in filter(None, self.options['paths'].splitlines()):
            if not os.path.isdir(target):
                os.mkdir(target)
            self.options.created(target)
        return self.options.created()

    def update(self):
        pass
