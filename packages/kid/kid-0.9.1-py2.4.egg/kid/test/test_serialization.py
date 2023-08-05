"""kid.serialization tests."""

__revision__ = "$Rev: 59 $"
__date__ = "$Date: 2005-02-16 15:43:38 -0500 (Wed, 16 Feb 2005) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"


import kid
from kid.namespace import xhtml
from kid.serialization import serialize_doctype, doctypes

xhtml_namespace = str(xhtml)

def test_html_output_method():
    t = kid.Template('<html><p>test</p><br /></html>')
    rslt = t.serialize(output='html')
    expected = serialize_doctype(doctypes['html']) + \
               '\n<HTML><P>test</P><BR></HTML>'
    
    print rslt
    assert rslt == expected
    
def test_xhtml_output_method():
    t = kid.Template('<html xmlns="http://www.w3.org/1999/xhtml">'
            '<p>test</p><img src="some.gif" /><br /></html>')
    rslt = t.serialize(output='xhtml')
    expected = serialize_doctype(doctypes['xhtml']) \
               + '\n<html xmlns="http://www.w3.org/1999/xhtml"><p>test</p>' \
               + '<img src="some.gif" /><br /></html>'
    
    print rslt
    assert rslt == expected
    
def test_html_strict_output_method():
    t = kid.Template('<html><p>test</p><br /></html>')
    rslt = t.serialize(output='html-strict')
    expected = serialize_doctype(doctypes['html-strict']) + \
               '\n<HTML><P>test</P><BR></HTML>'
    
    print rslt
    assert rslt == expected

def test_xml_output_method():
    t = kid.Template('<html><p>test</p><br/></html>')
    rslt = t.serialize(output='xml')
    expected = '<?xml version="1.0" encoding="utf-8"?>\n' \
               '<html><p>test</p><br /></html>'
    print rslt
    assert rslt == expected


from kid.serialization import HTMLSerializer
serializer = HTMLSerializer()
serializer.doctype = None
serializer.inject_type = 0
    
def HTMLTemplate(text, **kw):
    t = kid.Template(source=text, **kw)
    t.serializer = serializer
    return t

def test_html_empty_elements():
    t = HTMLTemplate("<html xmlns='%s'><br/></html>" % xhtml_namespace)
    rslt = t.serialize()
    print rslt
    assert rslt == '<HTML><BR></HTML>'

def test_html_noescape_elements():
    t = HTMLTemplate("<html><head><script>" \
                     "<![CDATA[less than: < and amp: &]]>" \
                     "</script></head></html>")
    expected = '<HTML><HEAD><SCRIPT>less than: < and amp: &</SCRIPT></HEAD></HTML>'
    rslt = t.serialize()
    print rslt
    assert rslt == expected

def test_html_boolean_attributes():
    t = HTMLTemplate("<html xmlns='%s'><option selected='1'>Bla</option></html>"
                     % xhtml_namespace )
    expected = '<HTML><OPTION SELECTED>Bla</OPTION></HTML>'
    rslt = t.serialize()
    print rslt
    assert rslt == expected

def test_doctype_and_injection():
    serializer = HTMLSerializer()
    serializer.doctype = doctypes['html-strict']
    serializer.inject_type = 1
    t = kid.Template(source="<html><head /></html>")
    t.serializer = serializer
    expected = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n'\
               '<HTML><HEAD>'\
               '<META CONTENT="text/html; charset=utf-8" HTTP-EQUIV="Content-Type">'\
               '</HEAD></HTML>'
    print expected
    rslt = t.serialize()
    print rslt
    assert rslt == expected

def test_strip_lang():
    serializer = HTMLSerializer()
    serializer.doctype = doctypes['html-strict']
    t = kid.Template(source="<html xml:lang='en' lang='en' />")
    t.serializer = serializer
    expected = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n'\
               '<HTML LANG="en"></HTML>'
    print expected
    rslt = t.serialize()
    print rslt
    assert rslt == expected

import string
def test_transpose_lower():
    serializer = HTMLSerializer()
    serializer.doctype = None
    serializer.inject_type = 0
    serializer.transpose = string.lower
    t = kid.Template(source="<HTML><HEAD /></HTML>")
    t.serializer = serializer
    expected = '<html><head></head></html>'
    rslt = t.serialize()
    assert rslt == expected

def test_transpose_off():
    serializer = HTMLSerializer()
    serializer.doctype = None
    serializer.inject_type = 0
    serializer.transpose = None
    t = kid.Template(source="<HTML><HEAD /></HTML>")
    t.serializer = serializer
    expected = '<HTML><HEAD></HEAD></HTML>'
    rslt = t.serialize()
    assert rslt == expected

def test_comment_whitespace():
    """Ticket #107 reported an issue where comments add an additional
    newline.
    """
    expected = '<?xml version="1.0" encoding="utf-8"?>\n<html>\n' \
            '<!-- a comment -->\n<element />\n</html>'
    assert kid.Template(expected).serialize(output='xml') == expected

    expected = serialize_doctype(doctypes['html']) + '\n<HTML>\n' \
            '<!-- a comment -->\n<ELEMENT>\n</ELEMENT>\n</HTML>'
    assert kid.Template(expected).serialize(output='html') == expected

    expected = serialize_doctype(doctypes['xhtml']) + '\n<html>\n' \
            '<!-- a comment -->\n<element>\n</element>\n</html>'
    assert kid.Template(expected).serialize(output='xhtml') == expected

__tests__ = [test_xml_output_method,
             test_html_output_method,
             test_html_strict_output_method,
             test_html_empty_elements,
             test_html_noescape_elements,
             test_html_boolean_attributes,
             test_doctype_and_injection,
             test_strip_lang,
             test_transpose_lower,
             test_transpose_off]
