"""Unit Tests for the XML comments."""

__revision__ = "$Rev: 340 $"
__author__ = "David Stanek <dstanek@dstanek.com>"
__copyright__ = "Copyright 2005, David Stanek"

import os
import kid
from kid.serialization import serialize_doctype, doctypes

def Xtest_comments_in_extend():
    """Test for the bug that was reported in ticket #66.

    I wanted to make two tests one using the KID_NOCET variable and
    one without.
    # XXX: get that to work
    """
    import py
    tmpdir = py.test.ensuretemp("test_comments")
    kid.path.paths.insert(0, str(tmpdir))
    tfile0 = tmpdir.join("layout.kid")
    tfile0.write("""
        <html xmlns:py="http://purl.org/kid/ns#">
            <body py:match="item.tag == 'body'">
                parent
                <p align="center" py:replace="item[:]">
                    ... content will be inserted here ...
                </p>
            </body>
        </html>
    """)
    tfile1 = tmpdir.join("page.kid")
    tfile1.write("""
        <html py:extends="'layout.kid'" xmlns:py="http://purl.org/kid/ns#">
            <body>
                <!-- a comment -->
                <p>my content</p>
            </body>
        </html>
    """)
    t = kid.Template(file="page.kid") 
    t.serialize()

def test_comment_removal():
    """Comments that start with an '!' character should not be output."""
    t = kid.Template('<html><!-- !comment --></html>')
    assert t.serialize(output='html') == \
            serialize_doctype(doctypes['html']) + '\n<HTML></HTML>'
    assert t.serialize(output='xhtml') == \
            serialize_doctype(doctypes['xhtml']) + '\n<html></html>'
    assert t.serialize(output='xml') == \
            '<?xml version="1.0" encoding="utf-8"?>\n<html />'

    t = kid.Template('<html><!--!comment--></html>')
    assert t.serialize(output='html') == \
            serialize_doctype(doctypes['html']) + '\n<HTML></HTML>'
    assert t.serialize(output='xhtml') == \
            serialize_doctype(doctypes['xhtml']) + '\n<html></html>'
    assert t.serialize(output='xml') == \
            '<?xml version="1.0" encoding="utf-8"?>\n<html />'

def test_comment_interpolation():
    """Comments starting with an '<' or '[' character should be interpolated.
    """
    for b in ('', ' '):
        for c in '!?->]<[':
            before_comment = '<!--%s%c$before -->' % (b, c)
            if c in '<[':
                after_comment = '<!--%s%cafter -->' % (b, c)
            elif c == '!':
                after_comment = ''
            else:
                after_comment = before_comment
            before= '<html>%s</html>' % before_comment
            t = kid.Template(before, before='after')
            for output in ('html', 'xhtml', 'xml'):
                if output == 'html':
                    after = '<HTML>%s</HTML>' % after_comment
                elif output == 'xhtml' or after_comment:
                    after = '<html>%s</html>' % after_comment
                else:
                    after = '<html />'
                if output == 'xml':
                    after = '<?xml version="1.0" encoding="utf-8"?>\n' + after
                else:
                    after = serialize_doctype(doctypes[output]) + '\n' + after
                assert t.serialize(output=output) == after
