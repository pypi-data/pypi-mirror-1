"""Kid test package."""

__revision__ = "$Rev: 59 $"
__date__ = "$Date: 2005-02-16 15:43:38 -0500 (Wed, 16 Feb 2005) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"


import os
from os.path import dirname, basename, join, abspath

template_dir = abspath(join(dirname(__file__), '../../test'))
output_dir = template_dir
template_package = 'test.'

test_modules = ['test_namespace', 'test_pull', 'test_compiler', 'test_parser',
                'test_kid', 'test_serialization', 'test_comment']

additional_tests = 0
basic_tests = 0

def run_tests():
    from kid.test.util import run_tests
    tests = ['kid.test.%s' % m for m in test_modules]
    run_tests(tests)

from kid.test.util import dot

__all__ = ['dot', 'run_tests', 'template_package', 'output_dir',
           'template_dir']

if __name__ == '__main__':
    run_tests()
