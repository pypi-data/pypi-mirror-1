"""kid package tests."""

__revision__ = "$Rev: 59 $"
__date__ = "$Date: 2005-02-16 15:43:38 -0500 (Wed, 16 Feb 2005) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

import os
import sys
from os.path import dirname, abspath, join as joinpath
from glob import glob
from StringIO import StringIO

import kid, kid.test
from kid.test import *
import kid.et as ElementTree

def cleanup():
    dont_clean = ['__init__.py', 'blocks.py']
    for f in glob(joinpath(output_dir, '*.out')):
        os.unlink(f)
    for f in glob(joinpath(template_dir, '*.pyc')):
        os.unlink(f)
#    for f in glob(joinpath(output_dir, '*.py')):
#        if f not in [joinpath(output_dir, p) for p in dont_clean]:
#            os.unlink(f)

def setup_module(module):
    cleanup()
    
def teardown_module(module):
    if not os.environ.get('KID_NOCLEANUP'):
        cleanup()

def assert_template_interface(t):
    assert hasattr(t, 'pull')
    assert hasattr(t, 'generate')
    assert hasattr(t, 'write')
    assert hasattr(t, 'serialize')

def test_import_and_expand():
    kid.enable_import()
    import test.context as c
    C = c.Template
    out = joinpath(output_dir, 'context.out')
    t = C(foo=10, bar='bla bla')
    it = t.pull()
    for e in it:
        pass
    t.write(out)
    check_test_file(out)
    
def test_import_template_func():
    assert not sys.modules.has_key(template_package + 'test_def')
    t = kid.import_template(template_package + 'test_def')
    assert_template_interface(t)
    assert sys.modules.has_key(template_package + 'test_def')
    
def test_load_template_func():
    t = kid.load_template(joinpath(template_dir, 'test_if.kid'), name='', cache=0)
    assert_template_interface(t)
    t2 = kid.load_template(joinpath(template_dir, 'test_if.kid'),
                           name=template_package + 'test_if',
                           cache=1)
    assert not t is t2
    t3 = kid.load_template(joinpath(template_dir, 'test_if.kid'),
                           name=template_package + 'test_if',
                           cache=1)
    assert t3 is t2

def test_template_func():
    t = kid.Template(name=template_package + 'test_if')
    assert_template_interface(t)
    assert isinstance(t, kid.BaseTemplate)
    
def test_generate_func():
    def run_test(o):
        for s in o.generate(encoding='ascii'):
            assert s is not None and len(s) > 0
    run_test(kid.Template(name=template_package + 'test_if'))
    run_test(kid.load_template(joinpath(template_dir, 'test_if.kid')))
    
def test_write_func():
    class FO:
        def write(self, text):
            pass
    kid.Template(name=template_package+'test_if').write(file=FO())
    m = kid.load_template(joinpath(template_dir, 'test_if.kid'))
    m.write(file=FO())

def test_serialize_func():
    def run_test(o):
        out = o.serialize(encoding='utf-8')
        assert out is not None and len(out) > 0
        out = o.serialize(encoding='ascii')
        assert out is not None and len(out) > 0
    run_test(kid.Template(name=template_package + 'test_if'))
    run_test(kid.load_template(joinpath(template_dir, 'test_if.kid')))

def test_short_form():
    # check that the serializer is outputting short-form elements when
    # no character data is present
    text = """<?xml version="1.0" encoding="utf-8"?>
<test><short /></test>"""
    template = kid.Template(file=text) #mod.Template()
    actual = template.serialize().strip()
    assert actual == text, '%r != %r' % (actual, text)

def test_XML_func_fragment():
    text = u"""some plain "text" with &amp; entities."""
    t = kid.Template(source="<p>${XML(text)}</p>", text=text)
    rslt = t.serialize(fragment=1)
    assert rslt == '''<p>some plain "text" with &amp; entities.</p>'''
    # another one
    text = """something <p>something else</p>"""
    t = kid.Template(source="<p>${XML(text)}</p>", text=text)
    actual = t.serialize(fragment=1)
    expected = '''<p>something <p>something else</p></p>'''
    assert actual == expected, '%r != %r' % (actual, expected)

def test_XML_func_unicode():
    s = u"""asdf \u2015 qwer"""
    t = kid.Template(source="""<p>${XML(s)}</p>""", s=s)
    print repr(t.serialize())

def test_dont_modify_trees():
    import elementtree.ElementTree
    t = kid.Template(source="<a>$xml</a>")
    t.xml = elementtree.ElementTree.fromstring("<b>some<c>nested</c>elements</b>")
    expected = "<a><b>some<c>nested</c>elements</b></a>"
    assert t.serialize(fragment=1) == expected
    print ElementTree.dump(t.xml)
    assert t.serialize(fragment=1) == expected

def test_comments():
    t = kid.Template(source="<doc><!-- bla --></doc>")
    rslt = t.serialize(fragment=1)
    print rslt
    assert rslt == "<doc><!-- bla --></doc>"

def test_kid_files():
    test_files = glob(joinpath(template_dir, 'test_*.kid'))
    for f in test_files:
        try:
            out = f[0:-4] + '.out'
            template = kid.Template(file=f, cache=1)
            template.assume_encoding = "utf-8"
            template.write(out)
            check_test_file(out)
        except:
            print '\nTemplate: %s' % f
            raise

def check_test_file(file):
    dot = kid.test.dot
    doc = ElementTree.parse(file).getroot()
    assert doc.tag == 'testdoc'
    for t in doc.findall('test'):
        attempt = t.find('attempt')
        expect = t.find('expect')
        if expect.get('type') == 'text':
            doc = ElementTree.XML(expect.text)
            expect.append(doc)
            expect.text = ''
        try:
            diff_elm(attempt, expect, diff_this=0)
        except AssertionError:
            raise
        else:
            dot()
        kid.test.additional_tests+= 1
        
def diff_elm(elm1, elm2, diff_this=1):
    for e in [elm1, elm2]:
        e.tail = e.tail and e.tail.strip() or None
        e.text = e.text and e.text.strip() or None
    if diff_this:
        assert elm1.tag == elm2.tag
        assert elm1.attrib == elm2.attrib
        assert elm1.tail == elm2.tail
    expected = elm2.text
    actual = elm1.text
    assert actual == expected, '%r != %r' % (actual, expected)
    ch1 = elm1.getchildren()
    ch2 = elm2.getchildren()
    assert len(ch1) == len(ch2)
    for elm1, elm2 in zip(ch1, ch2):
        diff_elm(elm1, elm2)

def test_string_templates():
    """Test for bug reported it ticket #70 where collisions occured in
    templates created with a string.
    """
    t1 = kid.Template(source="<xx/>")
    t2 = kid.Template(source="<yy/>")
    assert str(t1) ==  '<?xml version="1.0" encoding="utf-8"?>\n<xx />'
    assert str(t2) ==  '<?xml version="1.0" encoding="utf-8"?>\n<yy />'

__tests__ = [test_import_and_expand,
             test_import_template_func,
             test_load_template_func,
             test_template_func,
             test_generate_func,
             test_write_func,
             test_serialize_func,
             test_short_form,
             test_XML_func_fragment,
             test_XML_func_unicode,
             test_dont_modify_trees,
             test_comments,
             test_kid_files]
