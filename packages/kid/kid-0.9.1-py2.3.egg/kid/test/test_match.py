"""Unit Tests for the template matching."""

__revision__ = "$Rev: 305 $"
__author__ = "David Stanek <dstanek@dstanek.com>"
__copyright__ = "Copyright 2005, David Stanek"

import py
import kid
from kid.serialization import serialize_doctype, doctypes

tmpdir = py.test.ensuretemp("test_matching")
kid.path.paths.insert(0, str(tmpdir))

def test_match0():
    tfile0 = tmpdir.join("match0_base.kid")
    tfile0.write("""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml"
        xmlns:py="http://purl.org/kid/ns#">
    
        <head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'">
            <meta content="text/html; charset=UTF-8"
                http-equiv="content-type" py:replace="''" />
            <title py:replace="''">Your title goes here</title>
            <meta py:replace="item[:]" />
        </head>
    
        <body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'">
            <p align="center">
                <img src="http://www.turbogears.org/tgheader.png" />
            </p>
            <div py:replace="item[:]" />
        </body>
    </html>
    """)
    tfile1 = tmpdir.join("match0_page.kid")
    tfile1.write("""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml"
        xmlns:py="http://purl.org/kid/ns#" py:extends="'match0_base.kid'">
        
        <head>
            <meta content="text/html; charset=UTF-8"
                http-equiv="content-type" py:replace="''" />
            <title>Welcome to TurboGears</title>
        </head>
        
        <body>
            <strong py:match="item.tag == '{http://www.w3.org/1999/xhtml}b'"
                py:content="item.text.upper()" />
                
            <p>My Main page with <b>bold</b> text</p>
        </body>
    </html>
    """)

    t = kid.Template(file="match0_page.kid")
    html = t.serialize()
    assert '<title>Welcome to TurboGears</title>' in html
    assert '<strong>BOLD</strong>' in html

def test_match1():
    tfile0 = tmpdir.join("match1_base.kid")
    tfile0.write("""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns:py="http://purl.org/kid/ns#"
         xmlns="http://www.w3.org/1999/xhtml" lang="en">

        <head py:match="item.tag == '{http://www.w3.org/1999/xhtml}head'">
            <title>Some title here</title>
        </head>
        
        <span py:match="item.tag == '{http://www.w3.org/1999/xhtml}a' and item.get('href').startswith('http://') and 'noicon' not in str(item.get('class')).split(' ')" class="link-external" py:content="item"></span>
        <span py:match="item.tag == '{http://www.w3.org/1999/xhtml}a' and item.get('href').startswith('mailto:') and 'noicon' not in str(item.get('class')).split(' ')" class="link-mailto" py:content="item"></span>
        <span py:match="item.tag == '{http://www.w3.org/1999/xhtml}a' and item.get('href').startswith('/members/') and item.get('href').count('/') == 2 and 'noicon' not in str(item.get('class')).split(' ')" class="link-person" py:content="item"></span>

        <body py:match="item.tag == '{http://www.w3.org/1999/xhtml}body'">
            <div id="header">...</div>
            <div py:replace="item[:]">Real content would go here.</div>
            <div id="footer">...</div>
        </body>
    </html>
    """)
    tfile1 = tmpdir.join("match1_page.kid")
    tfile1.write("""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml"
        xmlns:py="http://purl.org/kid/ns#" py:extends="'match1_base.kid'">
        <head />
        <body>
            <p>This is a <a href="http://www.google.ca/">test link</a>,
            or an <a href="mailto:foo@bar.baz">e-mail address</a>.</p>
        </body>
    </html>
    """)

    t = kid.Template(file="match1_page.kid")
    html = t.serialize()
    assert '<div id="header">...</div>' in html
    assert '<span class="link-external"><a href="http://www.google.ca/">test link</a></span>' in html
    assert '<span class="link-mailto"><a href="mailto:foo@bar.baz">e-mail address</a></span>' in html
    assert '<div id="footer">...</div>' in html
    assert '<div>Real content would go here.</div>' not in html

def test_match_142():
    """Test for a know bad case in the apply_matches function. This
    was rewritten in #142.
    """
    tfile = tmpdir.join("match142_master.kid")
    tfile.write("""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd ">
    <html xmlns="http://www.w3.org/1999/xhtml"
        xmlns:py="http://purl.org/kid/ns#">
    <body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'">
    <div py:replace="item[:]"/>
    <!-- MASTER MATCH -->
    </body>
    </html>
    """)

    tfile = tmpdir.join("match142_userform.kid")
    tfile.write("""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        " http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml"
        xmlns:py="http://purl.org/kid/ns#">
    <body>
    <!-- THE INFAMOUS PY:MATCH   -->
    <div py:match="item.tag=='{http://testing.seasources.net/ns#}userform'"
        py:strip="True">
    <form py:attrs="action=action,method='post'" id="usereditform" />
    </div>
    </body>
    </html>
    """)

    tfile = tmpdir.join("match142_edit.kid")
    tfile.write("""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml"
        xmlns:py="http://purl.org/kid/ns#"
        xmlns:seasources="http://testing.seasources.net/ns#"
        py:extends="'match142_userform.kid','match142_master.kid'">
    <body>
    <!-- THIS IS THE TAG I WANT TO PY:MATCH ON -->
    <seasources:userform></seasources:userform>
    </body>
    </html>
    """)

    t = kid.Template(file='match142_edit.kid')
    t.action = 'match142_edit.kid'
    html = t.serialize()
    assert 'THIS IS THE' in html # text from  main template
    assert 'MASTER MATCH' in html # text from master template
    assert 'seasources:userform' not in html # text from userform template
