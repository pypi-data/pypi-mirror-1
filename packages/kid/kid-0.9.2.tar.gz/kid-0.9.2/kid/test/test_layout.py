"""Unit Tests for layout templates."""

__revision__ = "$Rev: 257 $"
__author__ = "Daniel Miller <millerdev@nwsdb.com>"
__copyright__ = "Copyright 2006, David Stanek"

import os
import kid

def test_dynamic_layout():
    layout = kid.Template(source="""
        <html xmlns:py="http://purl.org/kid/ns#">
          ${body_content()}
        </html>
        """)
    child = kid.Template(source="""
        <html py:layout="dynamic_layout" xmlns:py="http://purl.org/kid/ns#">
          <body py:def="body_content()">body content</body>
        </html>
        """, dynamic_layout=type(layout))
    output = child.serialize()
    assert output.find("body content") > -1, "body_content function was not executed"

def test_match_locals():
    layout = kid.Template(source="""
        <?python
          test_var = "WRONG VALUE"
        ?>
        <html xmlns:py="http://purl.org/kid/ns#">
          <body>
            <?python
              assert "test_var" in locals(), "test_var is not defined in layout locals"
              assert test_var == "test value", "test_var has wrong value: %r" % test_var
            ?>
            <div />
          </body>
        </html>
        """)
    child = kid.Template(source="""
        <?python
          layout_params["test_var"] = "WRONG VALUE"
        ?>
        <html py:layout="layout" xmlns:py="http://purl.org/kid/ns#">
          <content py:match="item.tag == 'div'" py:strip="True">
            <?python
              assert "test_var" in locals(), "test_var is not defined in py:match locals"
              assert test_var == "test value", "test_var has wrong value in py:match: %r" % test_var
            ?>
            test_var=${test_var}
          </content>
        </html>
        """, layout=type(layout), test_var="test value")
    output = child.serialize()
    assert output.find("test_var=test value") > -1, "match template was not executed"

def test_def_locals():
    layout = kid.Template(source="""
        <?python
          test_var = "WRONG VALUE"
        ?>
        <html xmlns:py="http://purl.org/kid/ns#">
          <body>
            <?python
              assert "test_var" in locals(), "test_var is not defined in layout locals"
              assert test_var == "test value", "test_var has wrong value: %r" % test_var
            ?>
            ${child_content()}
          </body>
        </html>
        """)
    child = kid.Template(source="""
        <?python
          layout_params["test_var"] = "WRONG VALUE"
        ?>
        <html py:layout="layout" xmlns:py="http://purl.org/kid/ns#">
          <content py:def="child_content()" py:strip="True">
            <?python
              assert "test_var" in locals(), "test_var is not defined in py:def locals"
              assert test_var == "test value", "test_var has wrong value in py:def: %r" % test_var
            ?>
            test_var=${test_var}
          </content>
        </html>
        """, layout=type(layout), test_var="test value")
    output = child.serialize()
    assert output.find("test_var=test value") > -1, "child_content function was not executed"
