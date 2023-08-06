tranchitella.recipe.fs
======================

This recipe creates files and directories in a buildout.

Usage
-----

This is a minimal ``buildout.cfg`` file which makes use of the recipe::

    [buildout]
    parts = dirs

    [dirs]
    recipe = tranchitella.recipe.fs:mkdir
    paths =
        ${buildout:directory}/var
        ${buildout:directory}/var/lib
        ${buildout:directory}/var/tmp
        ${buildout:directory}/var/log

This will create the directories specified by the ``paths`` attribute.
