"""Pull-style interface for ElementTree."""

__revision__ = "$Rev$"
__date__ = "$Date: 2005-02-16 15:43:38 -0500 (Wed, 16 Feb 2005) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

from __future__ import generators

from kid.et import *  # ElementTree
from kid.util import open_resource, QuickTextReader

from xml.parsers import expat

# This is the default entity map.
import htmlentitydefs
default_entity_map = {}
default_external_dtd = []
for k, v in htmlentitydefs.name2codepoint.items():
    default_entity_map[k] = unichr(v)
    default_external_dtd.append('<!ENTITY %s "&#%d;">' % (k, v))
default_external_dtd = '\n'.join(default_external_dtd)

# Bring common ElementTree objects into scope
class InvalidStreamState(Exception):
    def __init__(self, msg="Invalid stream state."):
        Exception.__init__(self, msg)

def XML(text, fragment=1, encoding=None):
    """Element generator that reads from a string"""
    if text.startswith('<?xml ') or text.startswith('<!DOCTYPE '):
        fragment = 0
    if fragment:
        text = '<xml>%s</xml>' % text # allow XML fragments
        if isinstance(text, unicode):
            encoding = 'utf-16'
            text = text.encode(encoding)
        p = Parser(QuickTextReader(text), encoding)
        p._sourcetext = text
        return ElementStream(_coalesce(p, encoding=encoding)).strip()
    else:
        if isinstance(text, unicode):
            encoding = 'utf-16'
            text = text.encode(encoding)
        p = Parser(QuickTextReader(text), encoding)
        p._sourcetext = text
        return ElementStream(_coalesce(p, encoding=encoding))
    
def document(file, encoding=None, filename=None):
    if not hasattr(file, 'read'):
        if filename is None:
            filename = file
        file = open_resource(file, 'rb')
    else:
        if filename is None:
            filename = '<string>'
    p = Parser(file, encoding)
    p._filename = filename
    return ElementStream(_coalesce(p, encoding=encoding))

class ElementStream(object):
    
    """Provides a pull/streaming interface to ElementTree.
    
    Instances of this class are iterable. Most methods of the class act on
    the Element that is currently being visited.
    
    """
    
    def __init__(self, stream, current=None):
        """Create an ElementStream.
        
        stream - an iterator that returns ElementStream events.
        current - If an Element is provided in this parameter than
                  it is yielded as the first element in the stream.

        """
        if hasattr(stream, 'tag') and hasattr(stream, 'attrib'):
            stream = self._pull(stream, tail=1)
        self.current = None
        self._iter = self._track(iter(stream), current)
        
    def __iter__(self):
        return self._iter
    
    def expand(self):
        """Expand the current item in the stream as an Element."""
        
        current = self.current
        if current is None:
            current = []
        stack = [current]
        last = None
        for ev, item in self._iter:
            if ev == START:
                current = item
                if len(stack) > 0:
                    stack[-1].append(current)
                last = None
                stack.append(current)
            elif ev == END:
                last = stack.pop()
                assert last is item
                if len(stack) == 0:
                    break
            elif ev == TEXT:
                if last is not None:
                    last.tail = item
                else:
                    current.text = item
        if isinstance(last, list):
            return last[0]
        else:
            return last
        
    def strip(self, levels=1):
        depth = self.current is not None and 1 or 0
        for (ev, item) in self._iter:
            if ev == START:
                depth += 1
            if depth > levels or (depth == levels and ev not in (START, END)):
                yield (ev, item)
            if ev == END:
                depth -= 1
                if depth == 0:
                    break
                elif depth < 0:
                    raise InvalidStreamState()
            
    def eat(self):
        """Eat the current element and all decendant items."""
        depth = self.current is not None and 1 or 0
        for (ev, item) in self._iter:
            if ev == START:
                depth += 1
            elif ev == END:
                depth -= 1
                if depth == 0:
                    break
        return self        
    
    def _pull(self, elem, tail=0):
        orig = elem
        elem = Element(orig.tag, dict(orig.attrib))
        ## XXX: find a better way
        if elem.tag in (Comment, ProcessingInstruction):
            elem.text = orig.text
            orig.text = None
        yield (START, elem)
        if orig.text:
            yield (TEXT, orig.text)
        for child in orig.getchildren():
            for event in self._pull(child, tail=1):
                yield event
        yield (END, elem)
        if tail and orig.tail:
            yield (TEXT, orig.tail)
        
    def _track(self, stream, current=None):
        if current is not None:
            self.current = current
            yield (START, current)
        for p in stream:
            ev, item = p
            if ev == START:
                self.current = item
            elif ev == END:
                self.current = None
            yield (ev, item)
    
    def ensure(cls, stream, current=None):
        if isinstance(stream, cls):
            return stream
        else:
            return cls(stream, current)
    ensure = classmethod(ensure)


def to_unicode(value, encoding):
    if isinstance(value, unicode):
        return value

    if hasattr(value, '__unicode__'):
        return unicode(value)

    if not isinstance(value, str):
        value = str(value)
    
    return unicode(value, encoding)
    

def _coalesce(stream, encoding, extended=1):
    """Coalesces TEXT events and namespace events.
    
    Fold multiple sequential TEXT events into a single event.
    
    The 'encoding' attribute is for the source strings.
    """
    textbuf = []
    namespaces = []
    last_ev = None
    last = None
    current = None
    stack = [None]
    for ev, item in stream:
        if ev == TEXT:
            textbuf.append(item)
            last_ev = TEXT
            continue
        if last_ev == TEXT:
            text = u""
            for value in textbuf:
                text += to_unicode(value, encoding)

            textbuf = []
            if text:
                yield (TEXT, text)
        if ev == START:
            attrib = item.attrib
            for prefix, uri in namespaces:
                if prefix:
                    attrib['xmlns:%s' % prefix] = uri
                else:
                    attrib['xmlns'] =  uri
            namespaces = []
            current = item
            stack.append(item)
        elif ev == END:
            current = stack.pop()
        elif ev == START_NS:
            prefix, uri = item
            namespaces.append( (prefix, uri) )
            continue
        elif ev == END_NS:
            continue
        yield ev, item
    if last_ev == TEXT:
        text = u""
        for value in textbuf:
            text += to_unicode(value, encoding)

        if text:
            yield (TEXT, text)
    
# Common Events
START = 1
END = 2
TEXT = 3
DOCTYPE = 4
XML_DECL = 5

# These events aren't used after initial parsing
START_NS = 10
END_NS = 11
PI = 12
COMMENT = 13

def Parser(source, encoding=None):
    return ExpatParser(source)


# Most of the following copied from ElementTree.XMLTreeBuilder
# Differences from ET implementation:
#
#   * Specialized for generator based processing. Elements are built
#     using a iterator approach instead of the TreeBuilder approach.
#
#   * Support for DOCTYPE, Comment, and Processing Instruction nodes.
   
class ExpatParser(object):
    
    def __init__(self, source, encoding=None):
        if not hasattr(source, 'read'):
            filename = source
            source = open(source, 'rb')
        else:
            filename = '<string>'
        self._filename = filename
        self._source = source
        self._parser = parser = expat.ParserCreate(encoding, "}")
        self._queue = []
        
        # callbacks
        parser.DefaultHandler = self._default
        parser.StartElementHandler = self._start
        parser.EndElementHandler = self._end
        parser.CharacterDataHandler = self._data
        parser.ProcessingInstructionHandler = self._pi
        parser.CommentHandler = self._comment
        parser.StartNamespaceDeclHandler = self._start_ns
        parser.EndNamespaceDeclHandler = self._end_ns
        parser.XmlDeclHandler = self._xmldecl_handler
        parser.StartDoctypeDeclHandler = self._doctype_handler
        
        # let expat do the buffering, if supported
        try:
            self._parser.buffer_text = 1
        except AttributeError:
            pass
        # use new-style attribute handling, if supported
        try:
            self._parser.ordered_attributes = 1
            self._parser.specified_attributes = 1
            parser.StartElementHandler = self._start_list
        except AttributeError:
            pass
        self._doctype = None
        # these should be come customizable at some point
        self.entity = default_entity_map
        self.external_dtd = default_external_dtd
        # setup entity handling
        self._parser.SetParamEntityParsing(
            expat.XML_PARAM_ENTITY_PARSING_ALWAYS)
        self._parser.ExternalEntityRefHandler = self._buildForeign
        self._parser.UseForeignDTD()
    
    def _buildForeign(self, context, base, systemId, publicId):
        import StringIO
        parseableFile = StringIO.StringIO(default_external_dtd)
        original_parser = self._parser
        self._parser = self._parser.ExternalEntityParserCreate(context)
        self._parser.ParseFile(parseableFile)
        self._parser = original_parser
        return 1
    
    def push(self, ev, stuff):
        self._queue.append( (ev, stuff) )
    
    def _expat_stream(self):
        bufsize = 4 * 1024 # 4K
        feed = self.feed
        read = self._source.read
        done = 0
        while 1:
            while not done and len(self._queue) == 0:
                data = read(bufsize)
                if data == '':
                    self.close()
                    done = 1
                else:
                    feed(data)
            for i in self._queue:
                yield i
            self._queue = []
            if done:
                break
    
    def __iter__(self):
        names = {}

        # XXX: hack to enable old namespace. This should be removed for 0.7
        old_ns = 'http://naeblis.cx/ns/kid#'
        new_ns = 'http://purl.org/kid/ns#'
        def fixname(key):
            if key.startswith(old_ns):
                key = ''.join([new_ns, key[len(old_ns):]])
            try:
                name = names[key]
            except KeyError:
                name = key
                if "}" in name:
                    name = "{" + name
                names[key] = name
            return name
        
        stack = []
        parent = None
        current = None
        for (ev, stuff) in self._expat_stream():
            if ev == TEXT:
                yield (TEXT, stuff)
            elif ev == START:
                tag, attrib_in = stuff
                tag = fixname(tag)
                attrib = {}
                if attrib_in:
                    for key, value in attrib_in.items():
                        attrib[fixname(key)] = value
                parent = current
                current = Element(tag, attrib)
                stack.append(current)
                yield (START, current)
            elif ev == END:
                current = stack.pop()
                assert fixname(stuff) == current.tag
                parent = len(stack) and stack[-1] or None
                yield (END, current)
            elif ev == COMMENT:
                current = Comment(stuff)
                yield (START, current)
                yield (END, current)
            elif ev == PI:
                current = ProcessingInstruction(stuff[0], stuff[1])
                yield (START, current)
                yield (END, current)
            else:
                yield (ev, stuff)
            
    def feed(self, data):
        try:
            self._parser.Parse(data, 0)
        except expat.ExpatError, e:
            e.filename = self._filename
            if hasattr(self, '_sourcetext'):
                line = e.lineno
                e.source = self._sourcetext.split('\n', line)[-1]
            else:
                e.source = '???'
            raise e
    
    def close(self):
        if hasattr(self, '_parser'):
            self._parser.Parse('', 1) # end of data
            del self._parser # get rid of circular references
        
    def _start(self, tag, attrib_in):
        self._queue.append((START, (tag, attrib_in)))
        
    def _start_list(self, tag, attrib_in):
        attrib = None
        if attrib_in:
            attrib = {}
            for i in range(0, len(attrib_in), 2):
                attrib[attrib_in[i]] = attrib_in[i+1]
        self._queue.append((START, (tag, attrib)))
    
    def _data(self, text):
        self._queue.append((TEXT, text))
    
    def _end(self, tag):
        self._queue.append((END, tag))
    
    def _default(self, text):
        prefix = text[:1]
        if prefix == "&":
            # deal with undefined entities
            try:
                self._queue.append((TEXT, self.entity[text[1:-1]]))
            except KeyError:
                from xml.parsers import expat
                raise expat.error(
                    "undefined entity %s: line %d, column %d" %
                    (text, self._parser.ErrorLineNumber,
                    self._parser.ErrorColumnNumber)
                    )
        else:
            # XXX not sure what should happen here.
            # This gets: \n at the end of documents?, <![CDATA[, etc..
            pass
            
    def _pi(self, target, data):
        self._queue.append((PI, (target, data)))
        
    def _comment(self, text):
        self._queue.append((COMMENT, text))
    
    def _start_ns(self, prefix, uri):
        # XXX: hack to enable backward compatibility for kid templates.
        #      remove in version 0.7
        if uri == 'http://naeblis.cx/ns/kid#':
            newuri = 'http://purl.org/kid/ns#'
            from warnings import warn
            warn('Document uses old kid namespace [%s] this should be changed'
                 ' to [%s].' % (uri, newuri))
            uri = newuri
        self._queue.append((START_NS, (prefix or '', uri)))
    
    def _end_ns(self, prefix):
        self._queue.append((END_NS, prefix or ''))
    
    def _xmldecl_handler(self, version, encoding, standalone):
        self._queue.append((XML_DECL, (version, encoding, standalone)))
        
    def _doctype_handler(self, name, sysid, pubid, has_internal_subset):
        self._queue.append((DOCTYPE, (name, pubid, sysid)))
    

# utilities =================================================================


__all__ = ['Element', 'SubElement', 'Comment','ProcessingInstruction',
           'ElementStream', 'XML', 'document', 'Parser', 'ExpatParser',
           'START', 'END', 'TEXT', 'COMMENT', 'PI', 'XML_DECL', 'DOCTYPE']
