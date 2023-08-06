tranchitella.recipe.fs
======================

This recipe creates files and directories in a buildout.

Usage
-----

This recipe offers the following entry points:

 * mkdir
 * mkfile

mkdir
~~~~~

This is a minimal ``buildout.cfg`` which makes use of the ``mkdir`` recipe::

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

mkfile
~~~~~~

This is a minimal ``buildout.cfg`` which makes use of the ``mkfile`` recipe::

    [buildout]
    parts = conffiles

    [conffiles]
    recipe = tranchitella.recipe.fs:mkfile
    template = ${buildout:directory}/templates/config
    path = ${buildout:directory}/etc/config
    mode = 0644
    database = postgres

This will create the file specified by the ``path`` attribute using the given
template; the file will be customized using string interpolations of the
options specified in the buildout part (eg. ``%(database)s`` will be replaced
with the string ``postgres``).
