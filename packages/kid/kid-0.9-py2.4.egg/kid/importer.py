"""Kid Import Hooks.

When installed, these hooks allow importing .kid files as if they were
Python modules.

Notes:

There's some unpleasant incompatibility between ZODB's import trickery and the
import hooks here. Bottom line: if you're using ZODB, import it *before*
installing the import hooks.

This module is based heavily on code from the Quixote ptl_import module by MEMS
Exchange -- thanks guys.
"""

__revision__ = "$Rev: 252 $"
__date__ = "$Date: 2006-01-15 14:55:12 -0500 (Sun, 15 Jan 2006) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
import sys
import time
import imp, ihooks, new
import __builtin__

import kid.compiler
KID_EXT = kid.compiler.KID_EXT

assert sys.hexversion >= 0x20000b1, "need Python 2.0b1 or later"

_installed = False
def install(suffixes=None):
    global _installed
    if not _installed:
        hooks = KIDHooks(suffixes=suffixes)
        loader = KIDLoader(hooks)
        if cimport is not None:
            importer = cModuleImporter(loader)
        else:
            importer = ihooks.ModuleImporter(loader)
        ihooks.install(importer)
        _installed = True

def uninstall():
    global _installed
    _installed = False
    ihooks.uninstall()

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
        return 'kid.util.template_' + hex(hash(filename) + 0x80000000)
    
def _create_module(code, name, filename, store=1):
    name = get_template_name(name, filename)
    mod = new.module(name)
    mod.__file__ = filename
    mod.__ctime__ = time.time()
    exec code in mod.__dict__
    if store:
        sys.modules[name] = mod
    return mod

# this is put in a pyc file to signal that it is a kid file
KID_FILE = object()

class KIDHooks(ihooks.Hooks):

    def __init__(self, verbose=ihooks.VERBOSE, suffixes=None):
        ihooks.Hooks.__init__(self, verbose)
        self.suffixes = suffixes or []

    def get_suffixes(self):
        return [(KID_EXT, 'r', KID_FILE)] \
                + [(suffix, 'r', KID_FILE) for suffix in self.suffixes] \
                + imp.get_suffixes()

class KIDLoader(ihooks.ModuleLoader):

    def load_module(self, name, stuff):
        file, filename, info = stuff
        (suff, mode, type) = info
        if type is KID_FILE:
            return import_template(name, filename, force=1)
        else:
            return ihooks.ModuleLoader.load_module(self, name, stuff)

try:
    import cimport
except ImportError:
    cimport = None

class cModuleImporter(ihooks.ModuleImporter):
    def __init__(self, loader=None):
        self.loader = loader or ihooks.ModuleLoader()
        cimport.set_loader(self.find_import_module)

    def find_import_module(self, fullname, subname, path):
        stuff = self.loader.find_module(subname, path)
        if not stuff:
            return None
        return self.loader.load_module(fullname, stuff)

    def install(self):
        self.save_import_module = __builtin__.__import__
        self.save_reload = __builtin__.reload
        if not hasattr(__builtin__, 'unload'):
            __builtin__.unload = None
        self.save_unload = __builtin__.unload
        __builtin__.__import__ = cimport.import_module
        __builtin__.reload = cimport.reload_module
        __builtin__.unload = self.unload
