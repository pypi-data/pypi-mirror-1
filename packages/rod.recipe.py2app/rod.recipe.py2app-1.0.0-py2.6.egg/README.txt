The rod.recipe.py2app helps to create standalone Mac OS X application bundles
using py2app and PyObjC. It aims to provide handling eggs within a zc.buildout
environment.

To be honest, this is a recipe for scrambled eggs. The current py2app version
lacks of supporting python eggs, especially namespace packages. This recipe
reconstructs a directory tree from the contents of the given eggs.
