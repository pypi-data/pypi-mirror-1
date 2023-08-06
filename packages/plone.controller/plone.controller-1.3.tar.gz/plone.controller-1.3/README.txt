Introduction
============

plone.controller is a wxpython visual controller for Zope2 / Plone. Add it to a buildout
with a part specification like::

    [controller]
    recipe = zc.recipe.egg
    eggs = 
      plone.controller

This will generate a script, bin/plone-controller to start the controller, reading the
buildout.cfg in the current directory for configuration information. You may also specify
the config file on the command line.

The Python used for the buildout must include wx. This is not currently set as
a "requires" for the package because wx has a very large number of dependencies.

The controller provides a GUI for starting/stopping and checking the status of
a Zope 2 intance.
