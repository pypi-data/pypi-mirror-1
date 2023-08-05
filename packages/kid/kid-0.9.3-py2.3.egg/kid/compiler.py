"""Kid Compiler

Compile XML to Python byte-code.
"""

from __future__ import generators

__revision__ = "$Rev: 262 $"
__date__ = "$Date: 2006-01-28 16:38:09 +0000 (Sat, 28 Jan 2006) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

import sys
import re
import os
import os.path
import imp
import stat
import struct
import marshal
import new

import kid.parser

__all__ = ['KID_EXT', 'compile', 'compile_file', 'compile_dir']

# kid filename extension
KID_EXT = ".kid"

py_compile = compile

def actualize(code, dict=None):
    if dict is None:
        dict = {}
    exec code in dict
    return dict

def compile(source, filename='<string>', encoding=None):
    """Compiles kid xml source to a Python code object.

    source   -- A file like object - must support read.
    filename -- An optional filename that is used

    """
    # XXX all kinds of work to do here catching syntax errors and
    #     adjusting line numbers..
    py = kid.parser.parse(source, encoding, filename=filename)
    return py_compile(py, filename, 'exec')

_timestamp = lambda filename : os.stat(filename)[stat.ST_MTIME]

class KidFile(object):
    magic = imp.get_magic()

    def __init__(self, kid_file, force=0, encoding=None, strip_dest_dir=None):
        self.kid_file = kid_file
        self.py_file = os.path.splitext(kid_file)[0] + '.py'
        self.strip_dest_dir = strip_dest_dir
        self.pyc_file = self.py_file + 'c'
        self.encoding = encoding or 'utf-8'
        fp = None
        if force:
            stale = 1
        else:
            stale = 0
            try:
                fp = open(self.pyc_file, "rb")
            except IOError:
                stale = 1
            else:
                if fp.read(4) != self.magic:
                    stale = 1
                else:
                    mtime = struct.unpack('<I', fp.read(4))[0]
                    kid_mtime = _timestamp(kid_file)
                    if kid_mtime is None or mtime < kid_mtime:
                        stale = 1
        self.stale = stale
        self._pyc_fp = fp
        self._python = None
        self._code = None

    def compile(self, dump_code=1, dump_source=0):
        if dump_source:
            self.dump_source()
        code = self.code
        if dump_code and self.stale:
            self.dump_code()
        return code

    def code(self):
        if self._code is None:
            if not self.stale:
                self._code = marshal.load(self._pyc_fp)
            else:
                pyfile = self.py_file
                if self.strip_dest_dir and \
                   self.py_file.startswith(self.strip_dest_dir):
                    pyfile = os.path.normpath(self.py_file[len(self.strip_dest_dir):])
                self._code = py_compile(self.python, pyfile, 'exec')
        return self._code
    code = property(code)

    def python(self):
        """Get the Python source for the template."""
        if self._python is None:
            py = kid.parser.parse_file(self.kid_file, self.encoding)
            self._python = py
        return self._python
    python = property(python)

    def dump_source(self, file=None):
        py = self.python
        file = file or self.py_file
        try:
            fp = _maybe_open(file, 'wb')
            fp.write('# -*- coding: utf-8 -*-\n') # PEP 0263
            fp.write(self.python.encode('utf-8'))
        except IOError:
            try:
                os.unlink(file)
            except OSError:
                pass
            return 0
        else:
            return 1

    def dump_code(self, file=None):
        code = self.code
        file = file or self.pyc_file
        try:
            fp = _maybe_open(file, 'wb')
            if self.kid_file:
                mtime = os.stat(self.kid_file)[stat.ST_MTIME]
            else:
                mtime = 0
            fp.write('\0\0\0\0')
            fp.write(struct.pack('<I', mtime))
            marshal.dump(code, fp)
            fp.flush()
            fp.seek(0)
            fp.write(self.magic)
        except IOError:
            try:
                os.unlink(file)
            except OSError:
                pass
            return 0
        else:
            return 1

def _maybe_open(f, mode):
    if isinstance(f, basestring):
        return open(f, mode)
    else:
        return f

#
# functions for compiling files directly and the kidc utility
#

def compile_file(file, force=0, source=0, encoding=None, strip_dest_dir=None):
    """Compile the file specified.

    Return True if the file was compiled, False if the compiled file already
    exists and is up-to-date.

    """
    template = KidFile(file, force, encoding, strip_dest_dir)
    if template.stale:
        template.compile(dump_source=source)
        return 1
    else:
        return 0


def compile_dir(dir, maxlevels=10, force=0, source=0, encoding=None, strip_dest_dir=None):
    """Byte-compile all kid modules in the given directory tree.

    Keyword Arguments: (only dir is required)
    dir       -- the directory to byte-compile
    maxlevels -- maximum recursion level (default 10)
    force     -- if true, force compilation, even if timestamps are up-to-date.
    source    -- if true, dump python source (.py) files along with .pyc files.

    """
    names = os.listdir(dir)
    names.sort()
    success = 1
    ext_len = len(KID_EXT)
    for name in names:
        fullname = os.path.join(dir, name)
        if os.path.isfile(fullname):
            head, tail = name[:-ext_len], name[-ext_len:]
            if tail == KID_EXT:
                try:
                    rslt = compile_file(fullname, force, source, encoding, strip_dest_dir)
                except Exception, e:
                    # TODO: grab the traceback and yield it with the other stuff
                    rslt = e
                yield (rslt, fullname)
        elif (maxlevels > 0 and name != os.curdir and name != os.pardir and
                    os.path.isdir(fullname) and not os.path.islink(fullname)):
            for rslt in compile_dir(fullname, maxlevels - 1, force, source, strip_dest_dir):
                yield rslt
    return

