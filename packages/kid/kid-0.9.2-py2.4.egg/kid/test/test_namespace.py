"""kid.namespace tests."""

__revision__ = "$Rev: 59 $"
__date__ = "$Date: 2005-02-16 15:43:38 -0500 (Wed, 16 Feb 2005) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

def test_namespace_module():
    from kid.namespace import Namespace
    ns = Namespace(uri='urn:test', prefix='test')
    assert ns.name == '{urn:test}name'
    assert ns['name'] == '{urn:test}name'
    assert ns.qname('name') == 'test:name'
    ns = Namespace(uri=None)
    assert ns.name == 'name'
    assert ns['name'] == 'name'
    assert ns.qname('name') == 'name'
