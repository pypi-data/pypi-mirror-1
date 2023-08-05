"""Kid test package."""

__revision__ = "$Rev: 421 $"
__date__ = "$Date: 2006-10-22 07:02:46 -0400 (Sun, 22 Oct 2006) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

import sys
import os
import glob
from os.path import abspath, basename, dirname, join as joinpath

_mydir = abspath(joinpath(dirname(__file__))) + '/../../'
template_dir = _mydir + 'test'
output_dir = template_dir
template_package = 'test.'

test_modules = [basename(f)[:-3] for f in
    glob.glob(_mydir + 'kid/test/test*.py')]

additional_tests = 0
basic_tests = 0

def run_suite(args):
    stop_first = '-x' in args
    from kid.test.util import run_suite
    tests = ['kid.test.%s' % m for m in test_modules]
    run_suite(tests, stop_first)

from kid.test.util import dot

__all__ = ['dot', 'run_suite',
    'template_package', 'output_dir', 'template_dir']

if __name__ == '__main__':
    run_suite(sys.argv[1:])
