"""Kid Import Hooks.

When installed, these hooks allow importing .kid files as if they were
Python modules.

"""

__revision__ = "$Rev: 317 $"
__date__ = "$Date: 2006-04-21 08:51:24 +0000 (Fri, 21 Apr 2006) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

import os, sys, time, new
import __builtin__

import kid.compiler
KID_EXT = kid.compiler.KID_EXT

assert sys.hexversion >= 0x20000b1, "need Python 2.0b1 or later"

_installed = False

def install(suffixes=None):
    global _installed
    if not _installed:
        _install_hook(suffixes=suffixes)
        _installed = True

def uninstall():
    global _installed
    if _installed:
        _uninstall_hook()
        _installed = False

def import_template(name, filename, force=0):
    if not force and name and sys.modules.has_key(name):
        return sys.modules[name]
    template = kid.compiler.KidFile(filename)
    code = template.compile(dump_source=os.environ.get('KID_OUTPUT_PY'))
    module = _create_module(code, name, filename)
    return module

def get_template_name(name, filename):
    if name:
        return name
    else:
        return 'kid.util.template_%x' % (hash(filename) + sys.maxint + 1)

def _create_module(code, name, filename, store=1, ns={}):
    name = get_template_name(name, filename)
    mod = new.module(name)
    mod.__file__ = filename
    mod.__ctime__ = time.time()
    mod.__dict__.update(ns)
    exec code in mod.__dict__
    if store:
        sys.modules[name] = mod
    return mod

# this is put in a pyc file to signal that it is a kid file
KID_FILE = object()

try: # if possible, use new (PEP 302) import hooks
    from sys import path_hooks, path_importer_cache
except ImportError:
    path_hooks = None

if path_hooks is not None:

    class KIDLoader(object):

        def __init__(self, path=None):
            if path and os.path.isdir(path):
                self.path = path
            else:
                raise ImportError

        def find_module(self, fullname):
            path = os.path.join(self.path, fullname.split('.')[-1])
            for ext in [KID_EXT] + self.suffixes:
                if os.path.exists(path + ext):
                    self.filename = path + ext
                    return self
            return None

        def load_module(self, fullname):
            return import_template(fullname, self.filename, force=1)

    def _install_hook(suffixes=None):
        KIDLoader.suffixes = suffixes or []
        path_hooks.append(KIDLoader)
        sys.path_importer_cache.clear()

    def _uninstall_hook():
        i = 0
        while i < len(path_hooks):
            if path_hooks[i] is KIDLoader:
                del path_hooks[i]
            else:
                i += 1
        sys.path_importer_cache.clear()

else: # Python < 2.3, fall back to using the old ihooks module

    import ihooks, imp

    class KIDHooks(ihooks.Hooks):

        def __init__(self, verbose=ihooks.VERBOSE, suffixes=None):
            ihooks.Hooks.__init__(self, verbose)
            self.suffixes = suffixes or []

        def get_suffixes(self):
            return [(suffix, 'r', KID_FILE)
                for suffix in [KID_EXT] + self.suffixes] + imp.get_suffixes()

    class KIDLoader(ihooks.ModuleLoader):

        def load_module(self, name, stuff):
            file, filename, info = stuff
            (suff, mode, type) = info
            if type is KID_FILE:
                return import_template(name, filename, force=1)
            else:
                return ihooks.ModuleLoader.load_module(self, name, stuff)

    def _install_hook(suffixes=None):
        hooks = KIDHooks(suffixes=suffixes)
        loader = KIDLoader(hooks)
        importer = ihooks.ModuleImporter(loader)
        ihooks.install(importer)

    def _uninstall_hook():
        ihooks.uninstall()
