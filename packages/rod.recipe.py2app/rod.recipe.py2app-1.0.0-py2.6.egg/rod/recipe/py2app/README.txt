py2app-Build Recipe
===================

The build recipe takes a number of options:

eggs
    A list of eggs to install given as one or more setuptools requirement
    strings. Each string must be given on a separate line.

packages
    A list of required python packages.

script
    The name of the build script, which will be set up in bin.
    Default is 'py2app'.


Tests
=====

Let's try to import the Recipe class:

    >>> from rod.recipe.py2app import Recipe
