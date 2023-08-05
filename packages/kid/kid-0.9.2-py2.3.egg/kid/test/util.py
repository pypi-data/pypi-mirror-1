"""Utility stuff for tests.."""

__revision__ = "$Rev: 59 $"
__date__ = "$Date: 2005-02-16 15:43:38 -0500 (Wed, 16 Feb 2005) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

import sys
import os
import traceback

import kid.test
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class stdold:
    """Original sys.stderr and sys.stdout."""
    out = sys.stdout
    err = sys.stderr

def dot():
    stdold.err.write('.')

def skip():
    stdold.err.write('s')

def come_on_guido_this_is_just_wrong(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def test_funcs(mod):
    """Return a list of test functions for the given module object."""
    funcs = []
    for name in dir(mod):
        if name[:4] == 'test':
            attr = getattr(mod, name)
            if callable(attr):
                funcs.append(attr)
    return funcs

def run_tests(tests, stop_first=1):
    """Run tests given a list of modules that export __test__ variables."""
    try:
        os.mkdir(kid.test.output_dir)
    except OSError:
        e = sys.exc_info()[1]
        if int(e.errno) != 17:
            raise
    bad = []
    kid.test.basic_tests = 1
    test_cnt = 0
    from time import time
    start = time()
    # run over modules..
    for module_name in tests:
        try:
            mod = come_on_guido_this_is_just_wrong(module_name)
        except ImportError, e:
            if 'No module named py' not in str(e):
                raise
            skip()
            continue # you don't have pylib - so i won't run these tests
        #if not hasattr(mod, '__tests__'):
        #    raise '%r does not export a __tests__ variable.' % module_name
        if hasattr(mod, 'setup_module'): mod.setup_module(mod)
        # run each test...
        for test in test_funcs(mod):
            test_cnt += 1
            sys.stdout, sys.stderr = StringIO(), StringIO()
            try:
                test()
            except:
                asserr = isinstance(sys.exc_info()[0], AssertionError)
                ftype = asserr and 'F' or 'E'
                buf = StringIO()
                traceback.print_exc(file=buf)
                stdold.err.write(ftype)
                bad.append( (test, ftype, sys.exc_info(), \
                             (sys.stdout.getvalue(), sys.stderr.getvalue())))
                if stop_first:
                    sys.stdout, sys.stderr = (stdold.out, stdold.err)
                    sys.stderr.write(' *(bailing after %d tests)*\n' \
                                     % test_cnt)
                    o, e = bad[-1][3][0], bad[-1][3][1]
                    if o: sys.stderr.write('-- sys.stdout:\n%s\n' % o)
                    if e: sys.stderr.write('-- sys.stderr:\n%s\n' % e)
                    raise
            else:
                dot()
        sys.stdout, sys.stderr = stdold.out, stdold.err
        if hasattr(mod, 'teardown_module'): mod.teardown_module(mod)
    done = time()
    for test, ftype, exc_info, (o, e) in bad:
        sys.stderr.write('%s: %s\n' % ({'F':'Failure','E':'Error'}[ftype],
                                       test.__doc__))
        traceback.print_exception(exc_info[0], exc_info[1], exc_info[2],
                                  15, sys.stderr)
        if o: sys.stderr.write('-- sys.stdout:\n %s\n' % o)
        if e: sys.stderr.write('-- sys.stderr:\n %s\n' % e)
        sys.stderr.write('=========================\n')
    sys.stderr.write('\n%d Tests (+%d extended) OK (%f seconds)\n'
                     % (test_cnt, kid.test.additional_tests, done - start))
