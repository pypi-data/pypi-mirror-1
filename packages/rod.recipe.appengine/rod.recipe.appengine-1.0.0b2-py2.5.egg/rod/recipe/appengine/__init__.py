# Recipe for building, testing and deploying appengine projects.
#
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
import tempfile
import shutil

from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED, ZIP_STORED

from zc.recipe.egg import Eggs


def copytree(src, dst, symlinks=0):
    """Local implementation of shutil's copytree function.

    Checks wheather destination directory exists or not
    before creating it.
    """
    names = os.listdir(src)
    if not os.path.exists(dst):
        os.mkdir(dst)
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks)
            else:
                shutil.copy2(srcname, dstname)
        except (IOError, os.error), why:
            print "Can't copy %s to %s: %s" % (`srcname`, `dstname`, str(why))

class Zipper(object):
    """Provides a zip file creater.
    """

    deflate = ZIP_DEFLATED
    store   = ZIP_STORED

    def __init__(self, name, topdir, mode = "w"):
        """Initializes zipper.
        """
        self.name = name
        self.zip = ZipFile(name, mode, ZIP_DEFLATED)
        os.chdir(os.path.abspath(os.path.normpath(topdir)))
        self.topdir = os.getcwd()

    def close(self):
        self.zip.close()

    def add(self, fname, archname = None, compression_type = ZIP_DEFLATED):
        """Adds a file to the zip archive.
        """
        if archname is None:
            archname = fname

        normfname = os.path.abspath(os.path.normpath(archname))
        if normfname.startswith(self.topdir) and \
           normfname[len(self.topdir)] == os.sep:
            archivename = normfname[len(self.topdir) + 1:]
        else:
            raise RuntimeError, "%s: not found in %s" % (archname, self.topdir)

        self.zip.write(
            os.path.realpath(fname), archivename, compression_type)


class Recipe(Eggs):

    def __init__(self, buildout, name, opts):
        """Standard constructor for zc.buildout recipes.
        """
        self.temp_dir = tempfile.mkdtemp()
        super(Recipe, self).__init__(buildout, name, opts)
        opts['bin-directory'] = buildout['buildout']['bin-directory']
        opts['parts-direcotry'] = buildout['buildout']['parts-directory']
        opts['dest-direcotry'] = os.path.join(opts['parts-direcotry'],
                                                   self.name)
        opts['lib-directory'] = os.path.join(self.temp_dir, name)
        opts['src-directory'] = os.path.join(buildout['buildout']['directory'],
                                             opts.get('src'))

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
                                os.link(src, dst)
                    else:
                        dst = apply(os.path.join, [lib]+l[0:i+1])
                        src = apply(os.path.join, [entries[key]]+l[0:i+1])
                        if not  os.path.exists(dst):
                            os.link(src, dst)
                else:
                    d = apply(os.path.join, [lib]+l[0:i+1])
                    if not os.path.exists(d):
                        os.makedirs(d)
                        f = open(os.path.join(d, '__init__.py'), "w")
                        f.write('# Package')
                        f.close()

    def zip_packages(self, ws, lib):
        """Creates zip archive of configured packages.
        """
        zip_name = self.options.get('zip-name', 'packages.zip')
        zipper = Zipper(os.path.join(self.options['dest-direcotry'], zip_name), lib)
        os.chdir(lib)
        for root, dirs, files in os.walk('.'):
            for f in files:
                ext = os.path.splitext(f)[1]
                if ext not in ('.pyc', '.pyo', '.so', '.h', '.c') \
                and f.find('coptimizations') == -1:
                    zipper.add(os.path.join(root, f))
        zipper.close()

    def write_script(self, ws, lib):
        """Writes the appengine script.
        """
        path = os.path.join(self.options['bin-directory'],
                            self.options.get('script', self.name))
        script = open(path, 'w')
        script.write('#! %s\n' %
                     self.buildout[self.buildout['buildout']['python']
                     ]['executable'])

        script.write('''
import os
import sys

if not hasattr(sys, 'version_info'):
  sys.stderr.write('Very old versions of Python are not supported. Please '
                   'use version 2.5 or greater.\\n')
  sys.exit(1)
version_tuple = tuple(sys.version_info[:2])
if version_tuple < (2, 4):
  sys.stderr.write('Error: Python %%d.%%d is not supported. Please use '
                   'version 2.5 or greater.\\n' %% version_tuple)
  sys.exit(1)
if version_tuple == (2, 4):
  sys.stderr.write('Warning: Python 2.4 is not supported; this program may '
                   'break. Please use version 2.5 or greater.\\n')

DEV_APPSERVER_PATH = 'google/appengine/tools/dev_appserver_main.py'

DIR_PATH = '%s'

EXTRA_PATHS = [
  DIR_PATH,
  os.path.join(DIR_PATH, 'lib', 'django'),
  os.path.join(DIR_PATH, 'lib', 'webob'),
  os.path.join(DIR_PATH, 'lib', 'yaml', 'lib'),
]

''' % self.options.get('appengine-lib', '/usr/local/google_appengine'))

        src = self.options['src-directory']
        script.write('sys.path[0:0] = [\n    %s\n    ]\n\n' % ',\n    '.join(["'"+e+"'" for e in [self.options['dest-direcotry']]]))

        script.write('''
if __name__ == '__main__':
  sys.path = EXTRA_PATHS + sys.path
  script_path = os.path.join(DIR_PATH, DEV_APPSERVER_PATH)
  execfile(script_path, globals())
''')
        script.close()
        os.chmod(path, 0755)

    def install(self):
        """Creates the part.
        """
        options = self.options
        reqs, ws = self.working_set()
        try:
            if not os.path.exists(options['dest-direcotry']):
                os.mkdir(options['dest-direcotry'])
            self.link_packages(ws, options['lib-directory'])
            self.zip_packages(ws, options['lib-directory'])
            self.write_script(ws, options['lib-directory'])
            copytree(options['src-directory'], options['dest-direcotry'])
        finally:
            shutil.rmtree(self.temp_dir, True)
        return ()

    update = install
