"""Kid properties tests."""

__revision__ = "$Rev: $"
__date__ = "$Date: $"
__author__ = "David Stanek <dstanek@dstanek.com>"
__copyright__ = "Copyright 2006, David Stanek"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

import kid
prop = kid.properties

def test_api_nonexisting_property():
    property = 'does_not_exist:property'
    assert prop.get(property) == None
    assert prop.get(property, -1) == -1
    o = object()
    assert prop.get(property, o) is o
    assert not prop.isset(property)

def test_api_existing_property():
    property = 'unittest:property'
    expected = 'it worked'
    assert prop.set(property, expected) == expected
    assert prop.get(property, "it didn't worked") == expected
    assert prop.isset(property)

def test_api_remove_property():
    property = 'unittest:property'
    prop.set(property, 'test')
    assert prop.get(property) == 'test'
    prop.remove(property)
    assert not prop.isset(property)
    assert not prop.isset(property) # should not exist here
