"""kid.parser tests."""

__revision__ = "$Rev: 59 $"
__date__ = "$Date: 2005-02-16 15:43:38 -0500 (Wed, 16 Feb 2005) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

import kid

def test_interpolate_expr():
    from kid.parser import interpolate
    tests = [ ('foo ${bar} baz', ["'foo '", "bar", "' baz'"]),
              ('foo $bar baz', ["'foo '", "bar", "' baz'"]),
              ('foo $${bar} baz', 'foo ${bar} baz'),
              ('foo $$bar baz', 'foo $bar baz'),
              ('${foo} bar baz', ["foo", "' bar baz'"]),
              ('$foo bar baz', ["foo", "' bar baz'"]),
              ('foo bar ${baz}', ["'foo bar '", "baz"]),
              ('foo bar $baz', ["'foo bar '", "baz"]),
              ('foo $${bar}${baz}', ["'foo ${bar}'", "baz"]),
              ('foo $$bar$baz', ["'foo $bar'", "baz"]),
              ('${foo} bar ${baz}', ["foo", "' bar '", "baz"]),
              ('$foo bar $baz', ["foo", "' bar '", "baz"]),
              ('${foo}$${bar}${baz}', ["foo", "'${bar}'", "baz"]),
              ('$foo$$bar$baz', ["foo", "'$bar'", "baz"]),
              ('foo $object.attr bar', ["'foo '", "object.attr", "' bar'"]),
              ('$ foo ${bar baz}', ["'$ foo '", 'bar baz']),
              ('foo$ ${bar.baz}', ["'foo$ '", 'bar.baz']),
              ('$foo $100 $bar', ["foo", "' $100 '", "bar"]),
              ('$foo $$100 $bar', ["foo", "' $100 '", "bar"]),
              ('$$foo', '$foo'),
              ('', '')]
    for test, expect in tests:
        actual = interpolate(test)
        assert actual == expect

def test_interpolate_object():
    from kid.parser import interpolate
    expr = interpolate("foo ${bar} baz")
    assert repr(expr) == "['foo ', bar, ' baz']"

    # test for ticket #79
    assert repr(interpolate('$foo')) == '[foo]'

def test_adjust_block():
    from test.blocks import blocks
    from kid.parser import _adjust_python_block
    for test, expect in blocks:
        rslt = list(_adjust_python_block(test.splitlines()))
        rslt = '\n'.join(rslt)
        if expect != rslt:
            print 'Expected: %r' % expect
            print 'Got: %r' % rslt
            raise "test_adjust_block failed."

def test_exec_hack():
    """Guido may break this some day.."""
    exec('x = 10')
    assert x == 10
