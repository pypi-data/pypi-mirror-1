"""Unit Tests for the XML comments."""

__revision__ = "$Rev: 256 $"
__author__ = "David Stanek <dstanek@dstanek.com>"
__copyright__ = "Copyright 2005, David Stanek"

import os
import kid
from kid.serialization import serialize_doctype, doctypes

def test_comments_in_extend():
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
    """Comments that start with an '<' or '[' character should be interpolated."""
    for b in ('', ' '):
        for c in '!?->]<[':
            before = '<!--%s%c$before -->' % (b, c)
            if c in '<[':
                after = '<!--%s%cafter -->' % (b, c)
            elif c == '!':
                after = ''
            else:
                after = before
            before = '<html>%s</html>' % before
            t = kid.Template(before, before='after')
            for output in ('html', 'xhtml', 'xml'):
                if output == 'html':
                    after = '<HTML>%s</HTML>' % after
                elif output == 'xhtml' or after:
                    after = '<html>%s</html>' % after
                else:
                    after = '<html />'
                if output == 'xml':
                    after = '<?xml version="1.0" encoding="utf-8"?>' + after
                else:
                    after = serialize_doctype(doctypes[output]) + after
                assert t.serialize(output=output), after


__tests__ = [test_comment_removal,
             test_comment_interpolation]
