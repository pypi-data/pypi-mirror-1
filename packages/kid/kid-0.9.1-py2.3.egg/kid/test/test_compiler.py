"""kid package tests."""

__revision__ = "$Rev: 59 $"
__date__ = "$Date: 2005-02-16 15:43:38 -0500 (Wed, 16 Feb 2005) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

import os
import sys
from os.path import join, dirname, exists
import kid
import kid.compiler

import kid.test.test_kid
check_test_file = kid.test.test_kid.check_test_file

def setup_module(module):
    kid.test.test_kid.setup_module(module)

def teardown_module(module):
    kid.test.test_kid.teardown_module(module)

def assert_template_interface(t):
    assert hasattr(t, 'pull')
    assert hasattr(t, 'generate')
    assert hasattr(t, 'write')
    assert hasattr(t, 'serialize')

def test_import_hook():
    kid.enable_import()
    import test.test_if
    assert_template_interface(test.test_if)
    assert sys.modules.has_key('test.test_if')

def test_pyc_generation():
    # if this exists, the test is worthless. make sure this test runs before
    # anything else import test_content
    from kid.test import template_dir
    kid.enable_import()
    assert not exists(join(template_dir, 'test_content.pyc'))
    import test.test_content
    assert exists(join(template_dir, 'test_content.pyc'))
    assert sys.modules.has_key('test.test_content')
    
def test_import_and_expand():
    from kid.test import template_dir, output_dir
    kid.enable_import()
    import test.context as c
    C = c.Template
    out = join(output_dir, 'context.out')
    t = C(foo=10, bar='bla bla')
    it = t.pull()
    for e in it:
        pass
    t.write(out)
    check_test_file(out)

__tests__ = [test_import_hook,
             test_pyc_generation,
             test_import_and_expand]
