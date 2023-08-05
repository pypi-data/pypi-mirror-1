"""Unit Tests for error reporting."""

__revision__ = "$Rev: 421 $"
__author__ = "Christoph Zwerschke <cito@online.de>"
__copyright__ = "Copyright 2006, Christoph Zwerschke"

from os.path import join as joinpath
from tempfile import mkdtemp
from shutil import rmtree

from util import raises

import kid

def setup_module(module):
    global tmpdir, tfile
    tmpdir = mkdtemp(prefix='kid_test_error_')
    kid.path.insert(tmpdir)

def teardown_module(module):
    kid.path.remove(tmpdir)
    rmtree(tmpdir)

def test_xml_error():
    """Check that erroneous XML is reported."""
    from xml.parsers.expat import ExpatError
    page = """\
        <html>
            <h1>title</h1>
            <a><b>oops</b></a>
            <p>That's all, folks.</p>
        </html>"""
    kid.Template(page)
    page = page.replace('</b></a>', '</a></b>')
    e = str(raises(ExpatError, kid.Template, source=page))
    assert 'Error parsing XML' in e
    assert 'mismatched tag: line 3, column 24' in e
    assert page.splitlines()[2] in e # erroneous line
    assert "\n%25s\n" % "^" in e # offset pointer
    assert 'html' not in e
    assert 'title' not in e
    assert 'folks' not in e
    page = """\
        <html xmlns:py="http://purl.org/kid/ns#">
            <h1 py:replace="XML(xml)">title</h1>
        </html>"""
    t = kid.Template(source=page, xml="<h1>ok</h1>")
    from xml.parsers.expat import ExpatError
    content = """\
        <h1>start</h1>
        this &is wrong
        <p>end</p>"""
    t = kid.Template(source=page, xml=content)
    e = str(raises(ExpatError, t.serialize))
    assert 'Error parsing XML' in e
    assert 'not well-formed (invalid token): line 2, column 16' in e
    assert content.splitlines()[1] in e
    assert "\n%17s\n" % "^" in e
    assert 'html' not in e
    assert 'start' not in e
    assert 'end' not in e

def test_xml_long_line():
    """Check intelligent truncating of long XML error lines."""
    from xml.parsers.expat import ExpatError
    page = '<a>x</b>' + 9999*'x'
    e = str(raises(ExpatError, kid.Template, page))
    assert 'Error parsing XML' in e
    assert 'mismatched tag: line 1, column 6' in e
    assert ('\n<a>x</b>' + 68*'x') in e
    assert "\n%7s\n" % "^" in e
    page = '<a>' + 9999*'x' + '</b>'
    e = str(raises(ExpatError, kid.Template, page))
    assert 'Error parsing XML' in e
    assert 'mismatched tag: line 1, column 10004' in e
    assert ('\n' + 72*'x' + '</b>') in e
    assert "\n%75s\n" % "^" in e
    page = '<a>' + 9999*'x' + '</b>' + 9999*'x'
    e = str(raises(ExpatError, kid.Template, page))
    assert 'Error parsing XML' in e
    assert 'mismatched tag: line 1, column 10004' in e
    assert ('\n' + 36*'x' + '</b>' + 36*'x') in e
    assert "\n%39s\n" % "^" in e

def test_xml_filename_error():
    """Check that erroneous XML filename is reported."""
    page = "<xml>This is XML</xml>"
    open(joinpath(tmpdir, 'test_error0.kid'), 'w').write(page)
    t = kid.Template(file='test_error0.kid')
    page = "This is not XML"
    open(joinpath(tmpdir, 'test_error1.kid'), 'w').write(page)
    from xml.parsers.expat import ExpatError
    e = str(raises(ExpatError, kid.Template, file='test_error1.kid'))
    assert 'Error parsing XML' in e
    assert "test_error1.kid" in e
    assert page in e
    assert 'syntax error: line 1, column 0' in e
    assert '\n^\n' in e

def test_layout_error():
    """Check that erroneous py:layout expressions are reported."""
    page = '<html xmlns:py="http://purl.org/kid/ns#" py:layout="no_layout" />'
    # because py:layout is dynamic, the template can be created
    # but the error should show up when we try to serialize the template
    t = kid.Template(source=page)
    from kid.template_util import TemplateLayoutError
    e = str(raises(TemplateLayoutError, t.serialize))
    assert 'not defined' in e
    assert 'while processing layout=' in e
    assert 'no_layout' in e

def test_extends_error():
    """Check that erroneous py:extends expressions are reported."""
    page = '<html xmlns:py="http://purl.org/kid/ns#" py:extends="no_extends" />'
    # because py:extends is not dynamic, the template cannot be created
    from kid.template_util import TemplateExtendsError
    e = str(raises(TemplateExtendsError, kid.Template, source=page))
    assert 'not defined' in e
    assert 'while processing extends=' in e
    assert 'no_extends' in e

def test_attr_error():
    """Check that erroneous py:attrs expressions are reported."""
    page = """\
        <html xmlns:py="http://purl.org/kid/ns#">
            <p py:attrs="%s" />
        </html>"""
    t = kid.Template(source=page % "abc=123, def=789")
    s = t.serialize()
    assert 'abc="123"' in s and 'def="789"' in s
    from kid.template_util import TemplateAttrsError
    t = kid.Template(source=page % "abc=123, 456=789")
    e = str(raises(TemplateAttrsError, t.serialize))
    assert 'invalid' in e
    assert 'while processing attrs=' in e
    assert 'abc=123, 456=789' in e
    t = kid.Template(source=page % "{'mickey':'mouse'}")
    s = t.serialize()
    assert 'mickey="mouse"' in s
    t = kid.Template(source=page % "mickey mouse")
    e = str(raises(TemplateAttrsError, t.serialize))
    assert 'while processing attrs=' in e
    assert 'mickey mouse' in e
    t = kid.Template(source=page % "{mickey:mouse}")
    e = str(raises(TemplateAttrsError, t.serialize))
    assert 'not defined' in e
    assert 'mickey' in e and 'mouse' in e
