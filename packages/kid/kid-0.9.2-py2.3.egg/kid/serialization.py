"""Infoset serialization formats (XML, XHTML, HTML, etc)"""

from __future__ import generators

__revision__ = "$Rev$"
__date__ = "$Date: 2005-02-16 15:43:38 -0500 (Wed, 16 Feb 2005) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

import re

from kid.et import *
from kid.pull import *
from kid.pull import _coalesce

# bring in well known namespaces
import kid.namespace as namespace

__all__ = ['doctypes', 'Serializer', 'XMLSerializer', 'HTMLSerializer']

# some doctypes. you can pass strings from here or doctype tuples to
# Serializers
doctypes = {
    'html-strict'  : ('HTML', '-//W3C//DTD HTML 4.01//EN',
                      'http://www.w3.org/TR/html4/strict.dtd'),
    'html'         : ('HTML', '-//W3C//DTD HTML 4.01 Transitional//EN',
                      'http://www.w3.org/TR/html4/loose.dtd'),
    'xhtml-strict' : ('html', '-//W3C//DTD XHTML 1.0 Strict//EN',
                      'http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd'),
    'xhtml'        : ('html', '-//W3C//DTD XHTML 1.0 Transitional//EN',
                      'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd') }


class Serializer(object):

    namespaces = namespace.namespaces
    encoding = 'utf-8'
    balanced_blocks = 1
    strip_whitespace = 0

    def __init__(self, encoding=None, src_encoding="utf-8"):
        if encoding is not None:
            self.encoding = encoding
        self.src_encoding = src_encoding

    def has_only_pcdata(self, tagname):
        return False

    def serialize(self, stream, encoding=None, fragment=0):
        text = list(self.generate(stream, encoding, fragment))
        return ''.join(text)

    def write(self, stream, file, encoding=None, fragment=0):
        needs_closed = False
        if not hasattr(file, 'write'):
            needs_closed = True
            file = open(file, 'wb')
        try:
            write = file.write
            for text in self.generate(stream, encoding, fragment):
                write(text)
        finally:
            # only close a file if it was opened locally
            if needs_closed:
                file.close()

    def generate(self, stream, encoding=None, fragment=0):
        pass

    def apply_filters(self, stream):
        stream = _coalesce(stream, self.src_encoding)
        if self.strip_whitespace:
            stream = self.whitespace_filter(stream)
        else:
            if self.balanced_blocks:
                stream = self.balancing_filter(stream)
        return stream

    def balancing_filter(self, stream):
        line_collapse = re.compile('\n{2,}')
        text = ''
        hops = 0
        for ev, item in stream:
            if ev == TEXT:
                text = item
                hops = 0
            elif ev in (START, END) and item.tag != Fragment:
                if hops > 0:
                    if text and text.strip() == '':
                        yield (TEXT, line_collapse.sub('\n', text))
                elif text:
                    if text.strip() == '':
                        yield (TEXT, line_collapse.sub('\n', text))
                    else:
                        yield (TEXT, text)
                yield (ev, item)
                hops+=1
                # pre-tag indentation was used.
                # Make sure it's not used again for #PCDATA-sensitive elements
                if ev == START and (self.has_only_pcdata(item.tag)
                        or item.tag == Comment):
                    text = ''
            else:
                yield (ev, item)

    def whitespace_filter(self, stream):
        for ev, item in stream:
            if ev == TEXT:
                yield (TEXT, item.strip())
            else:
                yield (ev, item)

class XMLSerializer(Serializer):

    decl = 1
    doctype = None
    cdata_elements = []

    def __init__(self, encoding=None, decl=None, doctype=None,
                 namespaces=None):
        Serializer.__init__(self, encoding)
        if decl is not None:
            self.decl = decl
        if doctype is not None:
            self.doctype = doctype
        if isinstance(self.doctype, basestring):
            # allow doctype strings
            self.doctype = doctypes[self.doctype]
        if namespaces:
            self.namespaces = namespaces

    def can_be_empty_element(self, ns_stack, item_name):
        return True

    def generate(self, stream, encoding=None, fragment=0):
        """Serializes an event stream to bytes of the specified encoding.

        This function yields an encoded string over and over until the
        stream is exhausted.

        """

        encoding = encoding or self.encoding or 'utf-8'
        escape_cdata = XMLSerializer.escape_cdata
        escape_attrib = XMLSerializer.escape_attrib

        lastev = None
        stream = iter(stream)
        names = NamespaceStack(self.namespaces)
        if not fragment:
            if self.decl:
                yield '<?xml version="1.0" encoding="%s"?>\n' % encoding
            if self.doctype is not None:
                yield serialize_doctype(self.doctype) + '\n'
        text = None
        for ev, item in self.apply_filters(stream):
            if ev in (START, END) and item.tag == Fragment:
                continue
            elif ev == TEXT:
                if text is not None:
                    text = u''.join([text, item])
                else:
                    text = item
                continue
            if lastev == START:
                if ev == END and (not text or not text.strip()) and self.can_be_empty_element(names, item.tag):
                    yield ' />'
                    lastev = END
                    text = None
                    names.pop()
                    continue
                yield ">"
            if text:
                yield escape_cdata(text, encoding)
                text = None
            if ev == START:
                if item.tag == Comment:
                    yield "<!--%s-->" % item.text.encode(encoding)
                    lastev = COMMENT
                    continue
                elif item.tag == ProcessingInstruction:
                    yield "<?%s?>" % item.text.encode(encoding)
                    lastev = PI
                    continue
                else:
                    tag = item.tag
                    names.push(namespaces(item, remove=1))
                    qname = names.qname(tag, default=1)
                    yield "<" + qname.encode(encoding)
                    attrs = item.attrib.items()
                    if attrs:
                        for k, v in attrs:
                            qname = names.qname(k, default=0)
                            yield ' %s="%s"' % (qname.encode(encoding),
                                                escape_attrib(v, encoding))
                    for prefix, uri in names.current.items():
                        if prefix == '':
                            yield ' xmlns="%s"' % escape_attrib(uri, encoding)
                        else:
                            yield ' xmlns:%s="%s"' % (prefix.encode(encoding),
                                                      escape_attrib(uri, encoding))
            elif ev == END and item.tag not in (Comment, ProcessingInstruction):
                qname = names.qname(item.tag, default=1)
                yield "</%s>" % qname.encode(encoding)
                names.pop()
            lastev = ev
        return

    def escape_cdata(text, encoding=None):
        """Escape character data."""
        try:
            if encoding:
                try:
                    text = text.encode(encoding)
                except UnicodeError:
                    return encode_entity(text)
            text = text.replace("&", "&amp;")
            text = text.replace("<", "&lt;")
            return text
        except (TypeError, AttributeError):
            raise_serialization_error(text)
    escape_cdata = staticmethod(escape_cdata)

    def escape_attrib(text, encoding=None):
        """Escape attribute value."""
        try:
            if encoding:
                try:
                    text = text.encode(encoding)
                except UnicodeError:
                    return encode_entity(text)
            text = text.replace("&", "&amp;")
            text = text.replace("<", "&lt;")
            text = text.replace("\"", "&quot;")
            return text
        except (TypeError, AttributeError):
            raise_serialization_error(text)
    escape_attrib = staticmethod(escape_attrib)


# sets
try:
    set
except NameError:
    try:
        from sets import Set as set
    except ImportError:
        def set(seq):
            return seq

import kid.namespace as namespace
xhtml = namespace.xhtml.uri
import string

class HTMLSerializer(Serializer):

    doctype = doctypes['html']
    transpose = string.upper
    transpose = staticmethod(transpose)
    inject_type = 1
    empty_elements = set(['area', 'base', 'basefont', 'br', 'col', 'frame',
                          'hr', 'img', 'input', 'isindex', 'link', 'meta',
                          'param'])
    # These element tags should not be indented
    elements_with_pcdata = set(['option', 'textarea', 'fieldset', 'title'])
    noescape_elements = set(['script', 'style'])
    boolean_attributes = set(['selected', 'checked', 'compact', 'declare',
                          'defer', 'disabled', 'ismap', 'multiple', 'nohref',
                          'noresize', 'noshade', 'nowrap'])

    def __init__(self, encoding='utf-8', doctype=None, transpose=None):
        Serializer.__init__(self, encoding)
        if doctype:
            self.doctype = doctype
        if isinstance(self.doctype, basestring):
            # allow doctype strings
            self.doctype = doctypes[self.doctype]
        if transpose:
            self.transpose = transpose

    def has_only_pcdata(self, tagname):
        if isinstance(tagname, basestring) and tagname[0] == '{':
            tagname = tagname.split('}')[1]
        return tagname in self.elements_with_pcdata

    def generate(self, stream, encoding=None, fragment=0):
        """Serializes an event stream to bytes of the specified encoding.

        This function yields an encoded string over and over until the
        stream is exhausted.

        """

        encoding = encoding or self.encoding or 'utf-8'

        escape_cdata = HTMLSerializer.escape_cdata
        escape_attrib = HTMLSerializer.escape_attrib
        noescape_elements = self.noescape_elements
        boolean_attributes = self.boolean_attributes
        empty_elements = self.empty_elements

        names = NamespaceStack(self.namespaces)

        def grok_name(tag):
            if tag[0] == '{':
                uri, localname = tag[1:].split('}', 1)
            else:
                uri, localname = None, tag
            if uri and uri != xhtml:
                qname = names.qname(tag, default=0)
            else:
                qname = localname
                if self.transpose is not None:
                    qname = self.transpose(qname)
            return (uri, localname, qname)

        attr_http_equiv = 'http-equiv'
        attr_content = 'content'
        if self.transpose:
            attr_http_equiv = self.transpose('http-equiv')
            attr_content = self.transpose('content')

        current = None
        stack = [current]
        stream = iter(stream)
        if not fragment and self.doctype is not None:
            yield serialize_doctype(self.doctype) + '\n'
        for ev, item in self.apply_filters(stream):
            if ev == TEXT and item:
                escape = current not in noescape_elements
                yield escape_cdata(item, encoding, escape)
            elif ev == START:
                if item.tag == Comment:
                    yield "<!--%s-->" % item.text.encode(encoding)
                    lastev = COMMENT
                    continue
                elif item.tag == ProcessingInstruction:
                    yield "<?%s>" % item.text.encode(encoding)
                    lastev = PI
                    continue
                elif item.tag == Fragment:
                    continue
                else:
                    names.push(namespaces(item, remove=1))
                    tag = item.tag
                    (uri, localname, qname) = grok_name(tag)

                    # push this name on the stack so we know where we are
                    current = qname.lower()
                    stack.append(current)

                    yield "<" + qname.encode(encoding)
                    attrs = item.attrib.items()
                    if attrs:
                        for k, v in attrs:
                            (u, l, q) = grok_name(k)
                            lq = q.lower()
                            if lq == 'xml:lang': continue
                            if lq in boolean_attributes:
                                # XXX: what if v is 0, false, or no.
                                #      should we omit the attribute?
                                yield ' %s' % q.encode(encoding)
                            else:
                                yield ' %s="%s"' % (q.encode(encoding),
                                                    escape_attrib(v, encoding))
                    yield ">"
                    if self.inject_type:
                        if current == 'head':
                            (uri, localname, qname) = grok_name("meta")
                            yield '<%s %s="text/html; charset=%s"' \
                                  ' %s="Content-Type">' \
                                  % (qname.encode(encoding),
                                     attr_content,
                                     encoding,
                                     attr_http_equiv)

            elif ev == END and item.tag not in (Comment,
                                                ProcessingInstruction,
                                                Fragment):
                current = stack.pop()
                if current not in empty_elements:
                    tag = item.tag
                    (uri, localname, qname) = grok_name(tag)
                    yield "</%s>" % qname.encode(encoding)
                current = stack[-1]
                names.pop()
        return

    def escape_cdata(text, encoding=None, escape=1):
        """Escape character data."""
        try:
            if encoding:
                try:
                    text = text.encode(encoding)
                except UnicodeError:
                    return encode_entity(text)
            if escape:
                text = text.replace("&", "&amp;")
                text = text.replace("<", "&lt;")
            return text
        except (TypeError, AttributeError):
            raise_serialization_error(text)
    escape_cdata = staticmethod(escape_cdata)

    def escape_attrib(text, encoding=None):
        """Escape attribute value."""
        try:
            if encoding:
                try:
                    text = text.encode(encoding)
                except UnicodeError:
                    return encode_entity(text)
            text = text.replace("&", "&amp;")
            text = text.replace("\"", "&quot;")
            return text
        except (TypeError, AttributeError):
            raise_serialization_error(text)
    escape_attrib = staticmethod(escape_attrib)

class XHTMLSerializer(XMLSerializer):
    empty_elements = [namespace.xhtml.clarkname(name) for name in HTMLSerializer.empty_elements]
    elements_with_pcdata = [namespace.xhtml.clarkname(name) for name in HTMLSerializer.elements_with_pcdata]

    def can_be_empty_element(self, ns_stack, tagname):
        return tagname in self.empty_elements

    def has_only_pcdata(self, tagname):
        return tagname in self.elements_with_pcdata

class PlainSerializer(Serializer):

    def generate(self, stream, encoding=None, fragment=0):
        # XXX: Should this be ASCII?
        encoding = encoding or self.encoding or 'utf-8'
        for ev, item in self.apply_filters(stream):
            if ev == TEXT:
                yield item


class NamespaceStack:

    """Maintains a stack of namespace prefix to URI mappings."""

    def __init__(self, default_map=namespace.namespaces):
        self.stack = []
        self.default_map = default_map
        self.push()
        self.ns_count = 0

    def push(self, names=None):
        if names is None:
            names = {}
        self.current = names
        self.stack.insert(0, self.current)

    def pop(self):
        del self.stack[0]
        if len(self.stack):
            self.current = self.stack[0]

    def resolve_prefix(self, uri, default=1):
        """Figure out prefix given a URI."""

        if uri == 'http://www.w3.org/XML/1998/namespace':
            return 'xml'
        # first check if the default is correct
        is_default = -1
        prefix = None
        for names in self.stack:
            for k, v in names.items(): # (k,v) = (prefix, uri)
                if default and is_default == -1 and k == '':
                    # this is the current default namespace
                    is_default = (v == uri)
                    if (default and is_default) or prefix:
                        break
                if v == uri and k != '':
                    prefix = k
                    if is_default > -1:
                        break
        if default and is_default == 1:
            return ''
        elif prefix:
            return prefix
        else:
            return None

    def resolve_uri(self, prefix):
        """Figure out URI given a prefix."""

        if prefix == 'xml':
            return 'http://www.w3.org/XML/1998/namespace'
        for names in self.stack:
            uri = names.get(prefix)
            if uri:
                return uri
        return None

    def qname(self, cname, default=0):
        if isinstance(cname, QName):
            cname = cname.text
        if cname[0] != '{':
            # XXX: need to make sure default namespace is "no-namespace"
            return cname
        uri, localname = cname[1:].split('}', 1)
        prefix = self.resolve_prefix(uri, default)
        if prefix is None:
            # see if we have it in our default map
            prefix = self.default_map.get(uri)
            if prefix is not None:
                self.current[prefix] = uri
            else:
                if default and not self.current.has_key(''):
                    prefix = ''
                    self.current[prefix] = uri
                else:
                    self.ns_count += 1
                    # XXX : need to check for collisions here.
                    prefix = 'ns%d' % self.ns_count
                    self.current[prefix] = uri
        if prefix != '':
            return '%s:%s' % (prefix, localname)
        else:
            return localname

    def set(self, prefix, uri):
        if prefix is None:
            prefix = ''
        self.current[prefix] = uri

def serialize_doctype(doctype):
    return '<!DOCTYPE %s PUBLIC "%s" "%s">' % doctype
