"""ElementTree extensions."""

__revision__ = "$Rev: 424 $"
__date__ = "$Date: 2006-10-22 12:42:24 -0400 (Sun, 22 Oct 2006) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

import os
import re

# If allowed and possible, import all objects from CElementTree:

try:
    if os.environ.get('KID_NOCET'):
        raise ImportError
    else:
        try:
            if os.environ.get('KID_NOET'):
                raise ImportError
            else:
                import cElementTree as CET
                from cElementTree import *
        except ImportError:
            # you must have Python 2.5 or newer
            import xml.etree.cElementTree as CET
            from xml.etree.cElementTree import *
except:
    CET = None

# Otherwise, import all objects from ElementTree:

try:
    if os.environ.get('KID_NOET'):
        raise ImportError
    else:
        import elementtree.ElementTree as ET
        if not CET:
            from elementtree.ElementTree import *
except ImportError:
    # you must have Python 2.5 or newer
    import xml.etree.ElementTree as ET
    if not CET:
        from xml.etree.ElementTree import *

# The following is duplicated from ET,
# because it is not official or broken in some versions.
# This also allows us to sneak in some enhancements.

def raise_serialization_error(text):
    raise TypeError(
        "cannot serialize %r (type %s)" % (text, type(text).__name__)
        )

escape_map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
}

re_escape = re.compile(eval(r'u"[&<>\"\u0080-\uffff]+"'))

def encode_entity(text, pattern=re_escape, map=None):
    if map is None:
        map = escape_map
    # map reserved and non-ascii characters to XML entities
    def escape_entities(m, map=map):
        out = []
        for char in m.group():
            text = map.get(char)
            if text is None:
                text = "&#%d;" % ord(char)
            out.append(text)
        return ''.join(out)
    try:
        return pattern.sub(escape_entities, text).encode('ascii')
    except TypeError:
        raise_serialization_error(text)

def Comment(text=None):
    """Comment element factory."""
    elem = Element(Comment)
    elem.text = text
    return elem

def ProcessingInstruction(target, text=None):
    """PI element factory."""
    elem = Element(ProcessingInstruction)
    elem.text = target
    if text:
        elem.text += " " + text
    return elem

def Fragment(text=''):
    """XML fragment factory.

    Fragments hold TEXT and children but do not have a tag or attributes.

    """
    elem = Element(Fragment)
    elem.text = text
    return elem

def namespaces(elem, remove=False):
    """Get the namespace declarations for an Element.

    This function looks for attributes on the Element provided that have the
    following characteristics:

       * Begin with 'xmlns:' and have no namespace URI.
       * Are named 'xmlns' and have no namespace URI.

    The result is a dictionary containing namespace prefix -> URI mappings.
    Default namespace attributes result in a key of ''.

    If remove is truthful, namespace declaration attributes are removed
    from the passed in Element.

    """
    names = {}
    for k in elem.keys():
        if k.startswith('xmlns:'):
            names[k[6:]] = elem.get(k)
            if remove:
                del elem.attrib[k]
        elif k == 'xmlns':
            names[''] = elem.get(k)
            if remove:
                del elem.attrib[k]
    return names

__all__ = ['Element', 'SubElement', 'Comment', 'ProcessingInstruction',
           'Fragment', 'ElementTree', 'QName', 'dump',
           'parse', 'tostring', 'namespaces', 'escape_map',
           'encode_entity', 'raise_serialization_error']
