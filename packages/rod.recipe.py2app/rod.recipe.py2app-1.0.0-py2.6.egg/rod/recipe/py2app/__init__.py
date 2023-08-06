# Recipe for building PyObjC applications and plugins.
# Copyright (C) 2008 Tobias Rodaebel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import re

from zc.recipe.egg import Eggs

class Recipe(Eggs):

    def __init__(self, buildout, name, options):
        """Standard constructor for zc.buildout recipes.
        """
        super(Recipe, self).__init__(buildout, name, options)
        options['bin-directory'] = buildout['buildout']['bin-directory']
        options['parts-directory'] = buildout['buildout']['parts-directory']
        options['lib-directory'] = os.path.join(options['parts-directory'],
                                                name + '-lib')

    def link_packages(self, ws, lib):
        """Links egg contents to lib-directory.
        """
        if not os.path.exists(lib):
            os.mkdir(lib)
        packages = self.options.get('packages', '').split()
        keys = [ k.lower() for k in packages ]
        for p in keys:
            if p not in ws.by_key.keys():
                raise KeyError, '%s: package not found.' % p
        entries = {}
        for k in ws.entry_keys:
            key = ws.entry_keys[k][0]
            if key in keys:
                entries[packages[keys.index(key)]] = k
        for key in entries.keys():
            l = key.split('.')
            for i in range(0, len(l)):
                if len(l[i+1:]) == 0:
                    dir = [f for f in os.listdir(entries[key]) if f!='EGG-INFO']
                    if dir[0] not in l[0:i+1]:
                        for f in dir:
                            dst = os.path.join(lib, f)
                            src = os.path.join(entries[key], f)
                            if not  os.path.exists(dst):
                                os.symlink(src, dst)
                    else:
                        dst = apply(os.path.join, [lib]+l[0:i+1])
                        src = apply(os.path.join, [entries[key]]+l[0:i+1])
                        if not  os.path.exists(dst):
                            os.symlink(src, dst)
                else:
                    d = apply(os.path.join, [lib]+l[0:i+1])
                    if not os.path.exists(d):
                        os.makedirs(d)
                        f = open(os.path.join(d, '__init__.py'), "w")
                        f.write('# Package')
                        f.close()

    def write_script(self, ws, lib):
        """Writes the py2app script.
        """
        path = os.path.join(self.options['bin-directory'],
                            self.options.get('script', 'py2app'))
        script = open(path, 'w')
        script.write('#! %s\n' %
                     self.buildout[self.buildout['buildout']['python']
                     ]['executable'])
        script.write('import sys\nsys.path[0:0] = [\n    %s\n    ]\n\n' %
                     ',\n    '.join(["'"+e+"'" for e in [lib]+ws.entries]))
        script.write('from setup import *')
        script.close()
        os.chmod(path, 0755)

    def install(self):
        """Creates the part.
        """
        options = self.options
        reqs, ws = self.working_set()
        self.link_packages(ws, options['lib-directory'])
        self.write_script(ws, options['lib-directory'])
        return ()

    update = install
