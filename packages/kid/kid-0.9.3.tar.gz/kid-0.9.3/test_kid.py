#!/usr/bin/python
"""Runs the suite of kid tests..

For best results, run with py.test as follows:

    py.test -xl test_kid.py

py.test provides nicer tracebacks and inspects variables when assertions fail.

You can also run this test suite directly by:

   python test_kid.py

"""

import sys
from os.path import dirname, abspath, join as joinpath

if __name__ == '__main__':
    __file__ = sys.argv[0]
base_dir = abspath(dirname(__file__))
if not base_dir in sys.path:
    sys.path.insert(1, base_dir)
test_dir = joinpath(base_dir, 'test')


import kid.test
kid.test.template_package = 'test.'
kid.test.template_dir = test_dir
kid.test.output_dir = test_dir

def run_tests():
    kid.test.run_tests()
if __name__ == '__main__':
    run_tests()
