"""Recipe for setting up a google appengine development environment."""

import logging
import os
import shutil
import sys
import tempfile
import urllib
import zc.recipe.egg
import zipfile

logger = logging.getLogger(__name__)


def copytree(src, dst, symlinks=0):
    """Local implementation of shutil's copytree function.

    Checks wheather destination directory exists or not
    before creating it.
    """
    names = os.listdir(src)
    if not os.path.exists(dst):
        os.mkdir(dst)
    for name in names:
        base, ext = os.path.splitext(name)
        if ext == ".egg-info":
            continue
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
            logging.error("Can't copy %s to %s: %s" % 
                          (srcname, dstname, str(why)))


class Zipper(object):
    """Provides a zip file creater."""

    def __init__(self, name, topdir, mode = "w"):
        """Initializes zipper."""
        self.name = name
        self.zip = zipfile.ZipFile(name, mode, zipfile.ZIP_DEFLATED)
        os.chdir(os.path.abspath(os.path.normpath(topdir)))
        self.topdir = os.getcwd()

    def close(self):
        self.zip.close()

    def add(self, fname, archname=None, compression_type=zipfile.ZIP_DEFLATED):
        """Adds a file to the zip archive."""
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


class Recipe(zc.recipe.egg.Eggs):
    """Buildout recipe for google appengine."""

    def __init__(self, buildout, name, opts):
        """Standard constructor for zc.buildout recipes."""

        super(Recipe, self).__init__(buildout, name, opts)
        opts['app-directory'] = os.path.join(buildout['buildout']
                                              ['parts-directory'],
                                              self.name)
        opts['bin-directory'] = buildout['buildout']['bin-directory']

    def write_server_script(self, name, bin, sys_path):
        """Generates bin script with given name."""

        # Open the destination script file
        path = os.path.join(self.options['bin-directory'], name)
        script = open(path, 'w')

        # Write script
        script.write("#!%s\n\n" % 
                        self.buildout[self.buildout['buildout']['python']]
                        ['executable'])
        script.write("import sys\nimport os\n\n")
        script.write("sys.path[0:0] = [\n")
        script.write(",\n".join(["  '%s'" % p for p in sys_path]))
        script.write("\n  ]\n\n")
        script.write("PROJECT_HOME = '%s'\n\n" %
                     self.buildout['buildout']['directory'])
        script.write("def mkvar():\n")
        script.write("  var = os.path.join(PROJECT_HOME, 'var')\n")
        script.write("  if not os.path.exists(var):\n")
        script.write("    os.mkdir(var)\n")
        script.write("  return var\n\n")
        script.write("from dev_appserver import *\n\n")
        script.write("if __name__ == '__main__':\n")
        script.write("  os.environ['TMPDIR'] = mkvar()\n")
        script.write("  run_file('%s', locals())" % bin)

        # Close script file and modify permissions
        script.close()
        os.chmod(path, 0755)

    def install_appengine(self):
        """Downloads and installs google appengine."""
        arch_filename = self.options['url'].split('/')[-1]
        dst = os.path.join(self.buildout['buildout']['parts-directory'])
        downloads_dir = os.path.join(os.getcwd(), 'downloads')
        if os.path.isdir(downloads_dir):
            shutil.rmtree(downloads_dir)
        os.mkdir(downloads_dir)
        src = os.path.join(downloads_dir, arch_filename)
        urllib.urlretrieve(self.options['url'], src)
        if os.path.isdir(os.path.join(dst, 'google_appengine')):
            shutil.rmtree(os.path.join(dst, 'google_appengine'))
        arch = zipfile.ZipFile(open(src, "rb"))
        for name in arch.namelist():
            if name.endswith('/'):
                os.mkdir(os.path.join(dst, name))
            else:
                outfile = open(os.path.join(dst, name), 'wb')
                outfile.write(arch.read(name))
                outfile.close()

    def setup_bin(self, ws):
        """Setup bin scripts."""
        gae = self.options.get('appengine-lib')
        if gae is None:
            gae = os.path.join(self.buildout['buildout']['parts-directory'], 
                               'google_appengine')

        sys_path = [gae]
        gae = os.path.join(gae, 'dev_appserver.py')

        # Write server script
        self.write_server_script(self.name, gae, sys_path)

    def copy_packages(self, ws, lib):
        """Copy egg contents to lib-directory."""
        if not os.path.exists(lib):
            os.mkdir(lib)
        packages = self.options.get('packages', '').split()
        keys = [k.lower() for k in packages]
        for p in keys:
            if p not in ws.by_key.keys():
                raise KeyError, '%s: package not found.' % p
        entries = {}
        for k in ws.entry_keys:
            key = ws.entry_keys[k][0]
            if key in keys:
                entries[packages[keys.index(key)]] = k
        for key in entries.keys():
            src = os.path.join(entries[key], key.split('.')[0])
            dir = os.path.join(lib, os.path.basename(src))
            if not os.path.exists(dir):
                os.mkdir(dir)
            copytree(src, dir)

    def zip_packages(self, ws, lib):
        """Creates zip archive of configured packages."""

        zip_name = self.options.get('zip-name', 'packages.zip')
        zipper = Zipper(os.path.join(self.options['app-directory'],
                                     zip_name), lib)
        os.chdir(lib)
        for root, dirs, files in os.walk('.'):
            for f in files:
                ext = os.path.splitext(f)[1]
                if ext not in ('.pyc', '.pyo', '.so', '.h', '.c') \
                and f.find('coptimizations') == -1:
                    zipper.add(os.path.join(root, f))
        pkg_resources_dummy = open(os.path.join(lib, 'pkg_resources.py'), "w")
        pkg_resources_dummy.write("def _dummy_func(*args):\n")
        pkg_resources_dummy.write("    pass\n\n")
        pkg_resources_dummy.write("declare_namespace = _dummy_func\n")
        pkg_resources_dummy.write("resource_filename = _dummy_func\n")
        pkg_resources_dummy.write("import imp\n\n")
        pkg_resources_dummy.write("imp.load_dynamic = _dummy_func\n\n")
        pkg_resources_dummy.close()
        zipper.add('pkg_resources.py')
        zipper.close()

    def copy_sources(self):
        """Copies the application sources."""
        options = self.options
        src = None
        if options.get('src'):
            src = os.path.join(self.buildout['buildout']['directory'],
                               options['src'])
        if src:
            sources = [src]
        else:
            reqs, ws = self.working_set()
            sources = [d.location for d in ws if d.key in reqs]
        for s in sources:
            copytree(s, options['app-directory'])

    def install(self):
        """Creates the part."""
        options = self.options
        reqs, ws = self.working_set()
        if not self.options.get('appengine-lib', False):
            self.install_appengine()
        self.setup_bin(ws)
        temp_dir = os.path.join(tempfile.mkdtemp(), self.name)
        self.copy_packages(ws, temp_dir) 
        app_dir = options['app-directory']
        if os.path.isdir(app_dir):
            shutil.rmtree(app_dir, True)
        if not os.path.exists(app_dir):
            os.mkdir(app_dir)
        self.zip_packages(ws, temp_dir)
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir, True)
        self.copy_sources()
        return ()

    def update(self):
        """Updates the part."""
        options = self.options
        reqs, ws = self.working_set()
        self.setup_bin(ws)
        self.copy_sources()
        return ()
