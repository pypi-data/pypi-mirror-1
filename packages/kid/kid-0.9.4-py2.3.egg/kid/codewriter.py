"""KidWriter

Write Python source code from XML.

"""

__revision__ = "$Rev: 433 $"
__date__ = "$Date: 2006-11-11 12:41:35 -0500 (Sat, 11 Nov 2006) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

from kid import __version__

import re
from kid.parser import *
from kid.et import namespaces, Comment, ProcessingInstruction
from kid import Namespace

# the kid xml namespace
KID_XMLNS = "http://purl.org/kid/ns#"
KID_PREFIX = 'py'
kidns = Namespace(KID_XMLNS)
QNAME_FOR = kidns['for']
QNAME_IF = kidns['if']
QNAME_DEF = kidns['def']
QNAME_SLOT = kidns['slot']
QNAME_CONTENT = kidns['content']
QNAME_REPLACE = kidns['replace']
QNAME_MATCH = kidns['match']
QNAME_STRIP = kidns['strip']
QNAME_ATTRIBUTES = kidns['attrs']
QNAME_EXTENDS = kidns['extends']
QNAME_LAYOUT = kidns['layout']

# deprectaed
QNAME_OMIT = kidns['omit']
QNAME_REPEAT = kidns['repeat']

# the kid processing instruction name
KID_PI = 'python'
KID_ALT_PI = 'py'
KID_OLD_PI = 'kid'

def parse(source, encoding=None, filename=None, entity_map=None):
    writer = KidWriter(document(source, encoding=encoding,
        filename=filename, entity_map=entity_map), encoding)
    return writer.parse()

def parse_file(filename, encoding=None, entity_map=None):
    """Parse the file specified.

    filename -- the name of a file.
    fp       -- an optional file like object to read from. If not specified,
                filename is opened.

    """
    source = open(filename, 'rb')
    try:
        return parse(source, encoding, filename, entity_map)
    finally:
        source.close()

class KidWriter(object):
    def __init__(self, stream, encoding=None):
        self.stream = stream
        self.encoding = encoding or 'utf-8'
        self.depth = 0
        self.module_code = CodeGenerator()
        self.class_code = CodeGenerator()
        self.expand_code = CodeGenerator(level=1)
        self.end_module_code = CodeGenerator()
        self.module_defs = []
        self.inst_defs = []

    def parse(self):
        self.begin()
        self.proc_stream(self.module_code)
        self.end()
        parts = []
        parts += self.module_code.code
        for c in self.module_defs:
            parts += c.code
        parts += self.class_code.code
        parts += self.expand_code.code
        for c in self.inst_defs:
            parts += c.code
        parts += self.end_module_code.code
        return '\n'.join(parts)

    def begin(self):
        code = self.module_code
        # Start with PEP 0263 encoding declaration
        code.line('# -*- coding: %s -*-' % self.encoding,
            '# Kid %s template module' % __version__,
            # imports
            'import kid',
            'from kid.template_util import *',
            'import kid.template_util as template_util',
            '_def_names = []',
            # default variables (can be overridden by template)
            'encoding = "%s"' % self.encoding,
            'doctype = None',
            'omit_namespaces = [kid.KID_XMLNS]',
            'layout_params = {}',
            # module methods
            'def pull(**kw): return Template(**kw).pull()',
            "def generate(encoding=encoding, fragment=False,"
                " output=None, format=None, **kw):"
                " return Template(**kw).generate(encoding=encoding,"
                " fragment=fragment, output=output, format=format)",
            "def serialize(encoding=encoding, fragment=False,"
                " output=None, format=None, **kw):"
                " return Template(**kw).serialize(encoding=encoding,"
                " fragment=fragment, output=output, format=format)",
            "def write(file, encoding=encoding, fragment=False,"
                " output=None, format=None, **kw):"
                " return Template(**kw).write(file, encoding=encoding,"
                " fragment=fragment, output=output, format=format)",
            'def initialize(template): pass',
            'BaseTemplate = kid.BaseTemplate')
        # expand code
        code = self.expand_code
        code.start_block('def initialize(self):')
        code.line('rslt = initialize(self)',
            'if rslt != 0: super(Template, self).initialize()')
        code.end_block()
        code.start_block('def _pull(self):')
        # XXX hack: nasty kluge for making kwargs locals
        code.line("exec template_util.get_locals(self, locals())",
            'current, ancestors = None, []',
            'if doctype: yield DOCTYPE, doctype')
        code = self.end_module_code
        code.line('')

    def end(self):
        self.expand_code.end_block()

    def proc_stream(self, code):
        for ev, item in self.stream:
            if ev == START:
                if item.tag == Comment:
                    text = item.text.strip()
                    if text.startswith('!'):
                        continue # swallow comment
                    if code is self.module_code:
                        line = self.expand_code.line
                    else:
                        line = code.line
                    if text.startswith('[') or text.startswith('<![') \
                            or text.endswith('//'):
                        sub = interpolate(item.text)
                        if isinstance(sub, list):
                            text = "''.join([unicode(o) for o in %r])" % sub
                        else:
                            text = repr(sub)
                    else:
                        text = repr(item.text)
                    line('_e = Comment(%s)' % text,
                        'yield START, _e; yield END, _e; del _e')
                elif item.tag == ProcessingInstruction:
                    if ' ' in item.text.strip():
                        name, data = item.text.split(' ', 1)
                    else:
                        name, data = item.text, ''
                    if name in (KID_PI, KID_ALT_PI, KID_OLD_PI):
                        if data:
                            code.insert_block(data)
                    else:
                        c = self.depth and code or self.expand_code
                        c.line('_e = ProcessingInstruction(%r, %r)'
                                % (name, data),
                            'yield START, _e; yield END, _e; del _e')
                        del c
                else:
                    layout = None
                    if code is self.module_code:
                        layout = item.get(QNAME_LAYOUT)
                        if layout is not None:
                            del item.attrib[QNAME_LAYOUT]
                            layout = str(layout)
                        base_classes = []
                        extends = item.get(QNAME_EXTENDS)
                        if extends is not None:
                            del item.attrib[QNAME_EXTENDS]
                            extends = str(extends)
                            for c in extends.split(','):
                                base_classes.append('BaseTemplate%d'
                                    % (len(base_classes) + 1))
                                code.line('%s = template_util'
                                    '.base_class_extends(%r, globals(), {}, %r)'
                                    % (base_classes[-1], c.strip(), extends))
                            code.end_block()
                        base_classes.append('BaseTemplate')
                        code = self.class_code
                        code.start_block('class Template(%s):'
                            % ', '.join(base_classes))
                        code.line('_match_templates = []')
                        code = self.expand_code
                    self.def_proc(item, item.attrib, code)
                    if layout is not None:
                        old_code = code
                        code = CodeGenerator(level=1)
                        code.start_block('def _pull(self):')
                        # Note: the following hack could be avoided
                        # if template args were not stored in self.__dict__
                        code.line(
                            'exec template_util.get_locals(self, locals())',
                            'kw = dict(layout_params)',
                            'kw.update(dict([(name, getattr(self, name))'
                                ' for name in _def_names]))',
                            'kw.update(self.__dict__)',
                            # Note: these names cannot be passed
                            # to the layout template via layout_params
                            'kw.pop("assume_encoding", None)',
                            'kw.pop("_layout_classes", None)',
                            't = template_util.base_class_layout('
                                '%r, globals(), locals())(**kw)' % layout,
                            't._match_templates += self._match_templates',
                            'bases = list(t.__class__.__bases__)')
                        code.start_block('for c in self.__class__.__bases__:')
                        code.start_block('if c not in bases:')
                        code.line('bases.append(c)')
                        code.end_block()
                        code.end_block()
                        code.line('self.__class__.__bases__ = tuple(bases)',
                            'return t._pull()')
                        code.end_block()
                        self.inst_defs.append(code)
                        code = old_code
            elif ev == END and item.tag not in (
                    ProcessingInstruction, Comment):
                break
            elif ev == TEXT:
                self.text_interpolate(item, code)
            elif ev == XML_DECL and item[1] is not None:
                encoding = str(item[1])
                if encoding != self.encoding:
                    self.module_code.line('encoding = %r' % encoding)
            elif ev == DOCTYPE:
                self.module_code.line('doctype = (%r, %r, %r)' % item)

    def def_proc(self, item, attrib, code):
        attr_name = QNAME_DEF
        decl = attrib.get(attr_name)
        if decl is None:
            attr_name = QNAME_SLOT
            decl = attrib.get(attr_name)
        if decl is not None:
            del attrib[attr_name]
            old_code = code
            if '(' not in decl:
                decl = decl + '()'
            name, args = decl.split('(', 1)
            pos = args.rfind(')')
            args = args[0:pos].strip()
            self_ = args and 'self, ' or 'self'
            class_decl = '%s(%s%s)' % (name, self_, args)

            # module function code
            code = CodeGenerator()
            code.start_block('def %s(*args, **kw):' % name)
            code.line('return Template().%s(*args, **kw)' % name)
            code.end_block()
            code.line('_def_names.append("%s")' % name)
            self.module_defs.append(code)

            # instance method code
            code = CodeGenerator(level=1)
            code.start_block('def __%s:' % class_decl)
            code.line('exec template_util.get_locals(self, locals())',
                'current, ancestors = None, []')
            self.inst_defs.append(code)
            self.match_proc(item, attrib, code)
            code.end_block()
            code.start_block('def %s:' % class_decl)
            code.line('return ElementStream(self.__%s(%s))' % (name, args))
            code.end_block()
            if attr_name == QNAME_SLOT:
                old_code.line('for _e in template_util'
                    '.generate_content(self.%s()): yield _e' % name)
        else:
            self.match_proc(item, attrib, code)

    def match_proc(self, item, attrib, code):
        expr = attrib.get(QNAME_MATCH)
        if expr is not None:
            del attrib[QNAME_MATCH]
            code = CodeGenerator(level=1)
            code.start_block('def _match_func(self, item, apply):')
            code.line('exec template_util.get_locals(self, locals())',
                'current, ancestors = None, []')
            self.for_proc(item, attrib, code)
            code.end_block()
            code.line('_match_templates.append('
                '(lambda item: %s, _match_func))' % expr)
            self.inst_defs.append(code)
        else:
            self.for_proc(item, attrib, code)

    def for_proc(self, item, attrib, code):
        expr = attrib.get(QNAME_FOR)
        if expr is not None:
            code.start_block('for %s:' % expr)
            del attrib[QNAME_FOR]
            self.if_proc(item, attrib, code)
            code.end_block()
        else:
            self.if_proc(item, attrib, code)

    def if_proc(self, item, attrib, code):
        expr = attrib.get(QNAME_IF)
        if expr is not None:
            code.start_block('if %s:' % expr)
            del attrib[QNAME_IF]
            self.replace_proc(item, attrib, code)
            code.end_block()
        else:
            self.replace_proc(item, attrib, code)

    def replace_proc(self, item, attrib, code):
        expr = attrib.get(QNAME_REPLACE)
        if expr is not None:
            del attrib[QNAME_REPLACE]
            attrib[QNAME_STRIP] = ""
            attrib[QNAME_CONTENT] = expr
        self.strip_proc(item, attrib, code)

    def strip_proc(self, item, attrib, code):
        has_content = self.content_proc(attrib, code)
        expr, attr = attrib.get(QNAME_STRIP), QNAME_STRIP
        if expr is None:
            # XXX py:omit is deprecated equivalent of py:strip
            expr, attr = attrib.get(QNAME_OMIT), QNAME_OMIT
        start_block, end_block = code.start_block, code.end_block
        line = code.line
        if expr is not None:
            del attrib[attr]
            if expr != '':
                start_block("if not (%s):" % expr)
                self.attrib_proc(item, attrib, code)
                end_block()
            else:
                pass # element is always stripped
        else:
            self.attrib_proc(item, attrib, code)
        if has_content:
            code.start_block(
                'for _e in template_util.generate_content(_cont):')
            line('yield _e', 'del _e')
            code.end_block()
            self.stream.eat()
        else:
            self.depth += 1
            self.proc_stream(code)
            self.depth -= 1
        if expr:
            start_block("if not (%s):" % expr)
            line('yield END, current',
                'current = ancestors.pop(0)')
            end_block()
        elif expr != '':
            line('yield END, current',
                'current = ancestors.pop(0)')

    def attrib_proc(self, item, attrib, code):
        line = code.line
        need_interpolation = False
        names = namespaces(item, remove=True)
        for k, v in attrib.items():
            sub = interpolate(v)
            if id(sub) != id(v):
                attrib[k] = sub
                if isinstance(sub, list):
                    need_interpolation = True
        expr = attrib.get(QNAME_ATTRIBUTES)
        if expr is not None:
            del attrib[QNAME_ATTRIBUTES]
            attr_text = ('template_util.make_updated_attrib('
                '%r, "%s", globals(), locals(), self._get_assume_encoding())'
                % (attrib, expr.replace('"', '\\\"')))
        else:
            if attrib:
                if need_interpolation:
                    attr_text = ('template_util.make_attrib('
                        '%r, self._get_assume_encoding())' % attrib)
                else:
                    attr_text = repr(attrib)
            else:
                attr_text = '{}'
        line('ancestors.insert(0, current)',
            'current = Element(%r, %s)' % (item.tag, attr_text))
        if len(names):
            code.start_block('for _p, _u in %r.items():' % names)
            line('if not _u in omit_namespaces: yield START_NS, (_p,_u)')
            code.end_block()
        line('yield START, current')

    def content_proc(self, attrib, code):
        expr = attrib.get(QNAME_CONTENT)
        if expr is not None:
            del attrib[QNAME_CONTENT]
            if expr:
                code.line('_cont = %s' % expr)
            else:
                code.line('_cont = None')
            return True

    def text_interpolate(self, text, code):
        line = code.line
        sub = interpolate(text)
        if isinstance(sub, list):
            code.start_block('for _e in %r:' % sub)
            code.line('for _e2 in template_util'
                '.generate_content(_e): yield _e2')
            code.end_block()
        else:
            line('yield TEXT, %r' % sub)


class SubExpression(list):
    """Collecting and representing expressions."""
    def __repr__(self):
        return "[%s]" % ', '.join(map(_ascii_encode, self))

# regular expression for expression substitution
_sub_expr = re.compile( # $$ | $expr | ${expr}
    r"\$(\$|[a-zA-Z][a-zA-Z0-9_\.]*|\{.*?\})",
        re.DOTALL) # this is for multi-line expressions

def interpolate(text):
    """Perform expression substitution on text."""
    text = _sub_expr.split(text)
    if len(text) == 1:
        # shortcut for standard case
        return text[0]
    # build subexpression list,
    # making it as small as possible (coalesce pieces)
    parts = SubExpression()
    plain_parts = [] # collect plaintext parts here
    plain = True # first part is plaintext
    for part in text:
        if part: # skip empty text
            if plain or part == '$': # plaintext
                plain_parts.append(part)
            else: # code expression
                if part.startswith('{'):
                    # long form
                    part = part[1:-1].strip()
                if part: # skip empty expressions
                    plain_parts = ''.join(plain_parts)
                    if plain_parts:
                        parts.append(repr(plain_parts))
                    plain_parts = []
                    parts.append(part)
        # plaintext and code parts take turns
        plain = not plain
    plain_parts = ''.join(plain_parts)
    if parts:
        if plain_parts:
            parts.append(repr(plain_parts))
        return parts
    else:
        return plain_parts


class CodeGenerator(object):
    """A simple Python code generator."""

    level = 0
    tab = '\t'

    def __init__(self, code=None, level=0, tab='\t'):
        self.code = code or []
        if level != self.level:
            self.level = level
        if tab != self.tab:
            self.tab = tab
        self.pad = self.tab * self.level

    def line(self, *lines):
        for text in lines:
            self.code.append(self.pad + text)

    def start_block(self, text):
        self.line(text)
        self.level += 1
        self.pad += self.tab

    def end_block(self, nblocks=1, with_pass=False):
        for n in range(nblocks):
            if with_pass:
                self.line('pass')
            self.level -= 1
            self.pad = self.pad[:-len(self.tab)]

    def insert_block(self, block):
        output_line = self.line
        lines = block.splitlines()
        if len(lines) == 1:
            # special case single lines
            output_line(lines[0].strip())
        else:
            # adjust the block
            for line in _adjust_python_block(lines, self.tab):
                output_line(line)

    def __str__(self):
        self.code.append('')
        return '\n'.join(self.code)

# Auxiliary functions

def _ascii_encode(s):
    return s. encode('ascii', 'backslashreplace')

def _adjust_python_block(lines, tab='\t'):
    """Adjust the indentation of a Python block."""
    lines = [lines[0].strip()] + [line.rstrip() for line in lines[1:]]
    ind = None # find least index
    for line in lines[1:]:
        if line != '':
            s = line.lstrip()
            if s[0] != '#':
                i = len(line) - len(s)
                if ind is None or i < ind:
                    ind = i
                    if i == 0:
                        break
    if ind is not None or ind != 0: # remove indentation
        lines[1:] = [line[:ind].lstrip() + line[ind:]
            for line in lines[1:]]
    if lines[0] and not lines[0][0] == '#':
        # the first line contains code
        try: # try to compile it
            compile(lines[0], '<string>', 'exec')
            # if it works, line does not start new block
        except SyntaxError: # unexpected EOF while parsing?
            try: # try to compile the whole block
                block = '\n'.join(lines) + '\n'
                compile(block, '<string>', 'exec')
                # if it works, line does not start new block
            except IndentationError: # expected an indented block?
                # so try to add some indentation:
                lines2 = lines[:1] + [tab + line for line in lines[1:]]
                block = '\n'.join(lines2) + '\n'
                # try again to compile the whole block:
                compile(block, '<string>', 'exec')
                lines = lines2 # if it works, keep the indentation
            except:
                pass # leave it as it is
        except:
            pass # leave it as it is
    return lines
