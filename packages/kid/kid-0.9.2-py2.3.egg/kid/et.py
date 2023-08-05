"""ElementTree extensions."""

__revision__ = "$Rev$"
__date__ = "$Date: 2005-02-16 15:43:38 -0500 (Wed, 16 Feb 2005) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

import os

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

# These functions exist only in ET, not in CET:

encode_entity = ET._encode_entity
raise_serialization_error = ET._raise_serialization_error

# We take the Comment factory from ET, not from CET,
# because this guarantees that Comment().tag = Comment
# (another possibile solution would have been to set
# CommentTag = Comment().tag and then later compare tags
# against CommentTag). Same for ProcessingInstructions.

Comment = ET.Comment
ProcessingInstruction = ET.ProcessingInstruction

# The fragment factory does not exist in ElementTree:

def Fragment(text=''):
    """XML fragment factory.

    Fragments hold TEXT and children but do not have a tag or attributes.

    """
    elem = Element(Fragment)
    elem.text = text
    return elem

def namespaces(elem, remove=0):
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
            if remove: del elem.attrib[k]
        elif k == 'xmlns':
            names[''] = elem.get(k)
            if remove: del elem.attrib[k]
    return names

__all__ = ['Element', 'SubElement', 'Comment', 'ProcessingInstruction',
           'Fragment', 'ElementTree', 'QName', 'dump',
           'parse', 'tostring', 'namespaces',
           'encode_entity', 'raise_serialization_error']
