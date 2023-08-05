"""ElementTree extensions."""

__revision__ = "$Rev$"
__date__ = "$Date: 2005-02-16 15:43:38 -0500 (Wed, 16 Feb 2005) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

import os

import elementtree.ElementTree as ET
if not os.environ.get('KID_NOCET'):
    try:
        from cElementTree import *
    except ImportError:
        from elementtree.ElementTree import *
else:
    from elementtree.ElementTree import *

def Comment(text=None):
    elem = Element(Comment)
    elem.text = text
    return elem

def ProcessingInstruction(target, text=None):
    element = Element(ProcessingInstruction)
    element.text = target
    if text:
        element.text = element.text + " " + text
    return element

def Fragment(text=''):
    """Create an XML fragment.

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
           'parse', 'tostring', 'namespaces']
