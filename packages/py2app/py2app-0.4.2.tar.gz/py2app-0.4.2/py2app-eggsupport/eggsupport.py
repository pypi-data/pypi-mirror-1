"""
Implement minimal support for egg files, beyond
what is supplied by pkg_resources.

Missing:
* remove .pyc and .pyo files
* compile .py files
* add dry-run support
* this breaks -A, fix that by adding .pth file
  that adds the right egg files to to sys.path.
* The callback for copy_eggs should be a delegate
  object, we need to have two callbacks
  - copy_extension(pkgname, sourcepath) -> pywrapper_source
    Called when a .so would have been copied into
    the zipfile (e.g. the current callback)
  - copied_native(destination_path)
    Called when a binary file is copied into 
    the site-packages directory (both .dylib and
    .so files), used for non-zip-safe eggs.
"""
import os, sys, zipfile
import pkg_resources
from simpleio import fsinter

from modulegraph.modulegraph import SourceModule, Package, Script

class ResourceSet (object):
    def __init__(self, eggs):
        self._egglinks = self._active_egglinks()
        self.eggs = set(egg for egg in eggs if self._usable_egg(egg))
        self.objects = set()
        self._usable = set(self.eggs)
        for egg in pkg_resources.working_set:
            if egg.project_name in ('setuptools', 'py2app'):
                continue
            elif self._usable_egg(egg):
                self._usable.add(egg)

    def finalize(self, mf):
        """
        Finalize the ResourceSet, using the module
        finder to record/calculate dependencies for
        all source files in the included eggs.
        """
        # We use a loop because we might run into
        # new egg dependencies based on the 
        # modulegraph analysis of modules we add.
        while True:
            self._insert_egg_dependencies()
            for egg in self.eggs:
                self._update_mf_for_egg(mf, egg)

            l = len(self.eggs)
            self._rescan_mf(mf)
            if len(l) == len(self.eggs):
                break


    def add(self, item):
        """
        Add 'item' to the list of included items. 

        If the item is part of a usable egg that 
        entire egg gets included, otherwise only
        the item itself gets included.
        """
        egg = self._locate_egg(item.filename)
        if egg is None:
            self.objects.add(item)
            return None
        else:
            self.eggs.add(egg)
            return egg

    def _locate_egg(self, path):
        """
        Look for a usable egg that contains ``path``,
        return ``None`` if that cannot be found.
        """
        for egg in self._usable:
            if path.startswith(egg.location + '/'):
                return egg
        return None

    def _active_egglinks(self):
        """
        Returns a set of site-packages entries that are
        actually .egg-link instances, that is: that correspond
        to eggs installed using "python setup.py develop"
        """
        active_egglinks = set()
        for subdir in sys.path:
            if not os.path.exists(os.path.join(subdir, 'easy-install.pth')):
                continue

            easy_install = open(os.path.join(subdir, 'easy-install.pth'), 'r').read().splitlines()

            egglinks = [ fn for fn in os.listdir(subdir) if fn.endswith('.egg-link') ]
            for fn in egglinks:
                tgt = open(os.path.join(subdir, fn), 'r').readline().strip()
                if tgt in easy_install:
                    active_egglinks.add(tgt)
        return active_egglinks

    def _usable_egg(self, egg):
        """
        Return True if the egg is usable, that is: a regular egg,
        or a 'develop' egg. This excludes ``--single-version-externally-managed``
        eggs.
        """
        if egg.location.endswith('.egg'):
           return True

        elif egg.location in self._egglinks:
            return True

        else:
            return False

    def copy_objects(self, target_dir, compress):

        if compress:
            compression = zipfile.ZIP_DEFLATED
        else:
            compression = zipfile.ZIP_STORED

        fn = os.path.join(target_dir, 'site-packages.zip')
        if os.path.exists(fn):
            zf = zipfile.ZipFile(fn, 'a', compression)
        else:
            zf = zipfile.ZipFile(fn, 'w', compression)

        for item in self.objects:
            if isinstance(item, Package):
                tgtName = item.identifier.replace('.', '/') + "/__init__"

            elif isinstance(item, Script):
                continue

            else:
                if '/' in item.identifier:
                    raise ValueError(item)
                tgtName = item.identifier.replace('.', '/')

            tgtName += os.path.splitext(item.filename)[-1]
            data = fsinter.read(item.filename)
            zf.writestr(tgtName, data)

    def copy_eggs(self, target_dir, rewrite_extension, compress):
        """
        Copy eggs into ``target_dir``. This creates a subdirectory
        ``site-packages`` for eggs that are not zip-safe and copies
        all zip-safe eggs into ``site-packages.zip``.

        When ``compress`` is true the zipfile for zip-safe eggs will
        be compressed. 

        The callback ``rewrite_extension(pkgname, filename)`` is called
        for extension files (``.so`` suffix) and should copy the extension
        in the bundle and return the source code for a python module that
        will load the extension from the right bit of the bundle.
        """
        zf = None

        if compress:
            compression = zipfile.ZIP_DEFLATED
        else:
            compression = zipfile.ZIP_STORED

        for egg in self.eggs:
            if self._is_zipsafe(egg):
                if zf is None:
                    fn = os.path.join(target_dir, 'site-packages.zip')
                    if os.path.exists(fn):
                        zf = zipfile.ZipFile(fn, 'a', compression)
                    else:
                        zf = zipfile.ZipFile(fn, 'w', compression)

                self._copy_zip(zf, egg, rewrite_extension)
            else:
                fn = os.path.join(target_dir, 'site-packages')
                if not os.path.exists(fn):
                    os.mkdir(fn)
                self._copy_dir(fn, egg)

        zf.close()

    def _egg_info(self, egg):
        """
        Return the location of the EGG-INFO directory for
        an egg. 
        """
        if egg.location.endswith('.egg'):
            return os.path.join(egg.location, 'EGG-INFO')
        else:
            return os.path.join(egg.location, 
                    egg.egg_name().split('-')[0] + '.egg-info')

            
    def _is_zipsafe(self, egg):
        """
        Returns True iff the egg is zip-safe.
        """
        rv =  fsinter.is_file(os.path.join(self._egg_info(egg), 'zip-safe'))
        print "zipsafe?", rv, egg
        return rv


    def _copy_zip(self, zf, egg, rewrite_extension=None):
        """
        Copy files to a zipfile object. If rewrite_extension
        is not None it will be called to get a replacement
        content for the named file. Return ``None`` to copy
        the file as is, return the contents for a ``.py`` file
        otherwise.
        """

        # First step: copy egg metadata
        zipdir = egg.egg_name() + ".egg"
        egg_info = self._egg_info(egg)
        for fn in fsinter.listdir(egg_info):
            data = fsinter.read(os.path.join(egg_info, fn))
            zf.writestr(os.path.join(zipdir, 'EGG-INFO', fn), data)

        # Then copy the actual contents
        copy_dirs = [(egg.location, zipdir)]
        while copy_dirs:
            cur_dir, cur_zip = copy_dirs.pop()

            for fn in fsinter.listdir(cur_dir):
                if fn.endswith('.pyc') or fn.endswith('.pyo'): continue

                nm = os.path.join(cur_dir, fn)
                if fsinter.is_dir(nm):
                    # XXX: to be removed
                    if egg.project_name == 'pyobjc-core' and fn == 'test': continue
                    copy_dirs.append((nm, os.path.join(cur_zip, fn)))
                else:
                    if nm.endswith('.so') and rewrite_extension is not None:
                        pkg = os.path.join(cur_zip, fn)[:-3][len(zipdir)+1:].replace('/', '.')
                        data = rewrite_extension(pkg, nm)
                        if data is not None:
                            zf.writestr(os.path.join(cur_zip, fn[:-3] + '.py'), data)
                            continue
                        
                    data = fsinter.read(nm)
                    zf.writestr(os.path.join(cur_zip, fn), data)

    def _copy_dir(self, dirpath, egg):
        """
        Copy files to a directory. This directory is assumed to be
        a clean site-packages directory.
        """

        # First step: copy egg metadata
        # We store the data in an .egg-info subdir to avoid haveing
        # to deal with .pth files.
        info_dir = os.path.join(dirpath, egg.egg_name() + ".egg-info")
        egg_info = self._egg_info(egg)
        if not os.path.exists(info_dir):
            os.mkdir(info_dir)

        for fn in fsinter.listdir(egg_info):
            data = fsinter.read(os.path.join(egg_info, fn))
            fp = open(os.path.join(info_dir, fn), 'w')
            fp.write(data)
            fp.close()

        # Then copy the actual contents, makeing sure not
        # to copy the egg-info again.
        copy_dirs = [(egg.location, dirpath)]
        at_root = True
        while copy_dirs:
            cur_dir, cur_zip = copy_dirs.pop()
            for fn in fsinter.listdir(cur_dir):
                if at_root and (fn == 'EGG-INFO' or fn.endswith('.egg-info')):
                    continue

                if fn.endswith('.pyc') or fn.endswith('.pyo'): continue

                nm = os.path.join(cur_dir, fn)
                if fsinter.is_dir(nm):
                    # XXX: to be removed
                    if egg.project_name == 'pyobjc-core' and fn == 'test': continue
                    copy_dirs.append((nm, os.path.join(cur_zip, fn)))
                else:
                    target = os.path.join(cur_zip, fn)
                    data = fsinter.read(nm)
                
                    dname = os.path.dirname(target)
                    if not os.path.exists(dname):
                        os.mkdir(dname)
                    fp = open(target, 'wb')
                    fp.write(data)
                    fp.close()

            at_root = False

    def _insert_egg_dependencies(self):
        """
        Add eggs that are dependencies of eggs
        we know about to the set of eggs we know
        about.
        """
        while True:
            l = len(self.eggs)
            for egg in self.eggs:
                extras = pkg_resources.require(egg.requires())
                for e in extras: 
                    if self._usable_egg(e):
                        self.eggs.add(e)

            if len(self.eggs) == l:
                break

    def _update_mf_for_egg(self, mf, egg):
        """
        Insert the dependencies of scanned eggs to the
        dependency list.
        """
        pass

    def _rescan_mf(self):
        """
        Scan the module finder graph and insert all
        dependencies we didn't yet know about into
        our list. 
        """
        return False

