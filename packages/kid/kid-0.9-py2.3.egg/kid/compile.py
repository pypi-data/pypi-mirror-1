#!/usr/bin/python

# This module provides the "kidc" command

"""Usage: kidc [OPTIONS] [file...]
Compile kid templates into Python byte-code (.pyc) files.

OPTIONS:

  -f, --force
          Force compilation even if .pyc file already exists.
  -s, --source
          Generate .py source files along with .pyc files.
          This is sometimes useful for debugging.
  -d, --strip-dest-dir <destdir>
          Strips the supplied path from the beginning of source
          filenames stored for error messages in the generated
          .pyc files

The file list may have files and/or directories. If a directory is specified,
all .kid files found in the directory and any sub-directories are compiled.
"""

__revision__ = "$Rev: 139 $"
__date__ = "$Date: 2005-03-14 19:28:22 -0500 (Mon, 14 Mar 2005) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

import sys
from os.path import isdir
from getopt import getopt, GetoptError as gerror

import kid.compiler

def main():
    # get options
    try:
        opts, args = getopt(sys.argv[1:], 'fshd=', ['force', 'source', 'help', 'strip-dest-dir='])
    except gerror, msg:
        sys.stderr.write(str(e) + '\n')
        sys.stdout.write(__doc__)
        sys.exit(2)
    force = 0
    source = 0
    strip_dest_dir = None
    for o, a in opts:
        if o in ('-f', '--force'):
            force = True
        elif o in ('-s', '--source'):
            source = True
        elif o in ('-h', '--help'):
            sys.stdout.write(__doc__)
            sys.exit(0)
        elif o in ('-d', '--strip-dest-dir'):
            strip_dest_dir = a
    files = args

    if not files:
        sys.stderr.write('kidc: No kid template specified.\n')
        sys.stderr.write("      Try 'kidc --help' for usage information.\n")
        sys.exit(2)

    # a quick function for printing results
    def print_result(rslt):
        (rslt, file) = rslt
        if rslt == True:
            msg = 'compile: %s\n' % file
        elif rslt == False:
            msg = 'fresh: %s\n' % file
        else:
            msg = 'error: %s (%s)\n' % (file, rslt)
        sys.stderr.write(msg)

    # run through files and compile
    for f in files:
        if isdir(f):
            for rslt in kid.compiler.compile_dir(f, force=force, source=source, strip_dest_dir=strip_dest_dir):
                print_result(rslt)
        else:
            kid.compiler.compile_file(f, force=force, source=source, strip_dest_dir=strip_dest_dir)
            print_result((True, f))

if __name__ == '__main__':
    main()
