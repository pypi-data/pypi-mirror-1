"""Utility functions used by generated kid modules.
"""

__revision__ = "$Rev: 263 $"
__date__ = "$Date: 2006-01-30 10:51:40 +0000 (Mon, 30 Jan 2006) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

from __future__ import generators

import inspect
import sys
from types import TypeType, ModuleType
from os.path import join, normpath, abspath, dirname

# these are for use by template code
import kid
from kid.pull import XML, document, ElementStream, \
                     Element, SubElement, Comment, ProcessingInstruction, \
                     START, END, TEXT, START_NS, COMMENT, PI, DOCTYPE, \
                     XML_DECL, to_unicode

class TemplateNotFound(Exception): pass

_local_excludes = ['generate', 'module', 'pull', 'serialize', 'transform', 'write']
def get_locals(inst, _locals=None):
    if _locals is None:
        _locals = {}
    ls = []
    local_excludes = _local_excludes # local copy
    for var, value in inspect.getmembers(inst):
        if not var.startswith('_') and not var in local_excludes \
                and var not in _locals:
            ls.append('%s=self.%s' % (var, var))
    return ';'.join(ls)

def get_base_class(thing, from_file):
    if thing is None or thing is kid.BaseTemplate:
        cls = kid.BaseTemplate
    elif isinstance(thing, basestring):
        path = kid.path.find(thing, from_file)
        cls = kid.load_template(path).Template
    elif isinstance(thing, TypeType):
        cls = thing
    elif isinstance(thing, ModuleType):
        cls = thing.Template
    else:
        raise TemplateNotFound("Could not find template: %r" % thing)
    return cls

def make_attrib(attrib, encoding=None):
    if attrib is None:
        return {}
    if encoding is None:
        encoding = sys.getdefaultencoding()

    for (k, v) in attrib.items():
        if isinstance(v, list):
            ls = [to_unicode(i, encoding) for i in v if i is not None]
            if not ls:
                del attrib[k]
            else:
                attrib[k] = ''.join(ls)
        else:
            attrib[k] = to_unicode(v, encoding)
    return attrib

def generate_content(content, parent=None):
    if content is None:
        return []
    if isinstance(content, basestring):
        return [(TEXT, content)]
    elif hasattr(content, 'tag') and hasattr(content, 'attrib'):
        # if we get an Element back, make it an ElementStream
        return ElementStream(content)
    elif hasattr(content, '__iter__'):
        # if we get an iterable back, there are two cases:
        if hasattr(content, '__getitem__'):
            # if we get a sequence back, we simply flatten it
            def flatten(seq):
                for i in seq:
                    for ev, item in generate_content(i):
                        yield ev, item
            return flatten(content)
        else:
            # if we get a generator back, pray it's an ElementStream
            return content
    else:
        return [(TEXT, unicode(content))]

def filter_names(names, omit_list):
    for ns in names.keys():
        if ns in omit_list:
            del names[ns]
    return names

def update_dict(a, s, globals, locals):
    """Update dictionary a from keyword argument string s."""
    try:
        strings = None
        try:
            b = eval('dict(%s)' % s, globals, locals)
        except (TypeError, SyntaxError):
            # TypeErrror happens with Python <2.3, because building
            # dictionaries from keyword arguments was not supported.
            # SyntaxError can happen if one of the keyword arguments
            # is the same as a Python keyword (e.g. "class") or if it is a
            # qualified name containing a namespace prefixed with a colon.
            # So in these cases we parse the keyword arguments manually:
            try:
                from cStringIO import StringIO
            except ImportError:
                from StringIO import StringIO
            from tokenize import generate_tokens
            from token import NAME, OP
            depth, types, strings = 0, [], []
            for token in generate_tokens(StringIO(s).readline):
                type_, string = token[:2]
                if type_ == OP:
                    if string == '=':
                        if depth == 0:
                            if len(types) > 0 \
                                and types[-1] == NAME and strings[-1]:
                                if len(types) > 2 \
                                    and types[-2] == OP and strings[-2] == ':' \
                                    and types[-3] == NAME and strings[-3]:
                                    strings[-3:] = ["'%s'" % ''.join(strings[-3:])]
                                else:
                                    strings[-1] = "'%s'" % strings[-1]
                                string = ':'
                    elif string in '([{':
                        depth += 1
                    elif depth > 0 and string in ')]}':
                        depth -= 1
                types.append(type_)
                strings.append(string)
            b = eval('{%s}' % ''.join(strings), globals, locals)
    except Exception:
        exc_type, exc_obj, tb = sys.exc_info()
        if strings is None:
            code = s
        else:
            code = "%s -> %s" % (s, ''.join(strings))
        raise exc_type("%s in %s" % (exc_obj, code))
    for k in b.keys():
        if b[k] is None:
            del b[k]
            if k in a:
                del a[k]
    a.update(b)
    return a

__all__ = ['XML', 'document', 'ElementStream',
           'Element', 'SubElement', 'Comment', 'ProcessingInstruction',
           'START', 'END', 'TEXT', 'START_NS', 'COMMENT',
           'PI', 'DOCTYPE', 'XML_DECL']
