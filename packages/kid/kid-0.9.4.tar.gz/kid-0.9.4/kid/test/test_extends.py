"""Unit Tests for Template Reuse."""

__revision__ = "$Rev: 421 $"
__author__ = "Christoph Zwerschke <cito@online.de>"
__copyright__ = "Copyright 2006, Christoph Zwerschke"

import sys
from os.path import join as joinpath
from tempfile import mkdtemp
from shutil import rmtree

import kid

def setup_module(module):
    global tmpdir
    tmpdir = mkdtemp(prefix='kid_test_extends_')
    kid.path.insert(tmpdir)
    open(joinpath(tmpdir, 'layout.kid'), 'w').write("""\
        <html xmlns:py="http://purl.org/kid/ns#">
            <body py:match="item.tag == 'body'">
                <p>my header</p>
                <div py:replace="item[:]" />
                <p>my footer</p>
            </body>
        </html>""")

def teardown_module(module):
    kid.path.remove(tmpdir)
    rmtree(tmpdir)

def test_extends():
    """Test the basic template reuse functionality."""
    page = """\
        <html py:extends="%s" xmlns:py="http://purl.org/kid/ns#">
            <body>
                <p>my content</p>
            </body>
        </html>"""
    for extends in ("'layout.kid'", "layout.kid",
        "'layout'", "layout"):
        source = page % extends
        rslt = kid.Template(source=source).serialize()
        assert 'my header' in rslt
        assert 'my content' in rslt
        assert 'my footer' in rslt
    source = page % "layout_module"
    from kid.template_util import TemplateExtendsError
    try:
        rslt = kid.Template(source=source).serialize()
    except TemplateExtendsError, e:
        e = str(e)
    except Exception:
        e = 'wrong error'
    else:
        e = 'silent'
    assert "'layout_module'" in e
    assert 'not defined' in e
    assert 'while processing extends=' in e
    source = """<?python
        layout_module = kid.load_template(
        kid.path.find('layout.kid')) ?>
        """ + source
    for extends in ("layout_module", "layout_module.Template"):
        rslt = kid.Template(source=source).serialize()
        assert 'my header' in rslt
        assert 'my content' in rslt
        assert 'my footer' in rslt

def test_comments_in_extends():
    """Test for the bug that was reported in ticket #66."""
    open(joinpath(tmpdir, 'layout2.kid'), 'w').write("""\
        <!-- layout -->
        <html xmlns:py="http://purl.org/kid/ns#">
            <head><title>layout</title></head>
            <body py:match="item.tag == 'body'">
                <div>header</div>
                <!-- comment 1 -->
                <p align="center" py:replace="item[:]">
                    ... content will be inserted here ...
                </p>
                <!-- comment 2 -->
                <div>footer</div>
            </body>
        </html>""")
    open(joinpath(tmpdir, 'page2.kid'), 'w').write("""\
        <!-- page -->
        <html xmlns:py="http://purl.org/kid/ns#"
                py:extends="'layout2.kid'">
            <head><title>page</title></head>
            <body>
                <!-- comment 3 -->
                <p>my content</p>
                <!-- comment 4 -->
            </body>
        </html>""")
    t = kid.Template(file="page2.kid")
    rslt = t.serialize(output='xhtml')
    expected = """\
        <!-- page -->
        <html>
            <head>
            <title>page</title></head>
            <body>
                <div>header</div>
                <!-- comment 1 -->
                <!-- comment 3 -->
                <p>my content</p>
                <!-- comment 4 -->
                <!-- comment 2 -->
                <div>footer</div>
            </body>
        </html>"""
    i = 0
    for line in expected.splitlines():
        line = line.strip()
        i = rslt.find(line, i)
        assert i >= 0, 'Missing or misplaced: ' + line
