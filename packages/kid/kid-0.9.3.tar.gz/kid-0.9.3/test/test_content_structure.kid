<?xml version='1.0' encoding='utf-8'?>
<?python #
from os.path import dirname, join as joinpath

some_xml = "<hello>world</hello>"

from kid.et import Element, SubElement
test_elm = Element("et")
test_elm.set("x", "foo")
SubElement(test_elm, "inner").text = "test"

?>
<testdoc xmlns:py="http://purl.org/kid/ns#">
  <test>
    <attempt py:content="document(joinpath(dirname(__file__), 'include-me.xml'))">
      test including a file
    </attempt>
    <expect><div>
  <p>included from external file.</p>
  <p>cool</p>
</div></expect>
  </test>
  <test>
    <attempt py:content="XML(some_xml)">
      test with XML string
    </attempt>
    <expect><hello>world</hello></expect>
  </test>

  <test>
    <attempt py:content="test_elm">Test ET structure</attempt>
    <expect><et x="foo"><inner>test</inner></et></expect>
  </test>

</testdoc>
