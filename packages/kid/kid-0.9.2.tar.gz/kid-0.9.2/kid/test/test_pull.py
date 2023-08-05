"""kid.pull tests"""

__revision__ = "$Rev: 59 $"
__date__ = "$Date: 2005-02-16 15:43:38 -0500 (Wed, 16 Feb 2005) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

from kid.et import *
from kid.pull import *

def test_expand():
    doc = XML("<doc><hello>world</hello></doc>", fragment=0)
    doc = doc.expand()
    assert doc.tag == 'doc'
    assert doc[0].tag == 'hello'
    assert doc[0].text == 'world'
