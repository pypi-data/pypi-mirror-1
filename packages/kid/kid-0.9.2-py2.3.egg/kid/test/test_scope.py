"""Unit Tests for Python scope."""

__revision__ = "$Rev: 227 $"
__author__ = "David Stanek <dstanek@dstanek.com>"
__copyright__ = "Copyright 2005, David Stanek"

import py
import kid

tmpdir = py.test.ensuretemp("test_scope")
kid.path.paths.insert(0, str(tmpdir))

def test_scope_101():
    """Test for scoping issue reported in ticket #101.
    
    Parameters passed into the Template constructor override the
    parameters of functions created with py:def.
    """
    
    tfile = tmpdir.join("scope.kid")
    tfile.write("""
        <foo xmlns:py="http://purl.org/kid/ns#">
            <bar py:def="foo(bar)" py:content="bar"/>
            <bar py:replace="foo(0)" />
        </foo>
    """)
    t = kid.Template(file="scope.kid", bar=1)
    assert "<bar>0</bar>" in t.serialize()
