"""Kid Parser

Parses Kid embedded XML to Python source code.
"""

from __future__ import generators

__revision__ = "$Rev: 261 $"
__date__ = "$Date: 2006-01-22 00:48:22 -0500 (Sun, 22 Jan 2006) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

import re
from kid.pull import *
from kid.et import namespaces
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

def parse(source, encoding=None, filename=None):
    parser = KidParser(document(source, encoding=encoding, filename=filename), encoding)
    return parser.parse()

def parse_file(filename, encoding=None):
    """Parse the file specified.

    filename -- the name of a file.
    fp       -- an optional file like object to read from. If not specified,
                filename is opened.

    """
    source = open(filename, 'rb')
    try:
        return parse(source, encoding, filename=filename)
    finally:
        source.close()

class KidParser(object):
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
        code.line('from __future__ import generators')
        code.line('import kid')
        code.line('from kid.template_util import *')
        code.line('import kid.template_util as template_util')

        # default variables. can be overridden by template
        code.line('encoding = "%s"' % self.encoding)
        code.line('doctype = None')
        code.line('omit_namespaces = [kid.KID_XMLNS]')
        code.line('layout_params = {}')

        # module methods.
        code.line('def pull(**kw): return Template(**kw).pull()')
        code.line("def generate(encoding=encoding, fragment=0, output=None, **kw): "
                  "return Template(**kw).generate(encoding=encoding, fragment=fragment, output=output)")
        code.line("def serialize(encoding=encoding, fragment=0, output=None, **kw): "
                  "return Template(**kw).serialize(encoding=encoding, fragment=fragment, output=output)")
        code.line("def write(file, encoding=encoding, fragment=0, output=None, **kw): "
                  "return Template(**kw).write(file, encoding=encoding, fragment=fragment, output=output)")
        code.line('BaseTemplate = kid.BaseTemplate')
        code.line('def initialize(template): pass')

        # expand code
        code = self.expand_code
        code.start_block('def initialize(self):')
        code.line('rslt = initialize(self)')
        code.line('if rslt != 0: super(Template, self).initialize()')
        code.end_block()
        code.start_block('def _pull(self):')
        # XXX hack: nasty kluge for making kwargs locals
        code.line("exec template_util.get_locals(self, locals())")
        code.line('current, ancestors = None, []')
        code.line('if doctype: yield (DOCTYPE, doctype)')

        code = self.end_module_code
        code.line('')

    def end(self):
        self.expand_code.end_block()

    def proc_stream(self, code):
        for (ev, item) in self.stream:
            if ev == START:
                if item.tag == Comment:
                    text = item.text.lstrip()
                    if text.startswith('!'):
                        continue
                    line = code.line
                    if text.startswith('<') or text.startswith('['):
                        sub = interpolate(item.text)
                        if isinstance(sub, list):
                            text = "''.join(%r)" % sub
                        else:
                            text = repr(sub)
                    else:
                        text = repr(item.text)
                    line('_e = Comment(%s)' % text)
                    line('yield (START, _e); yield (END, _e); del _e')
                elif item.tag == ProcessingInstruction:
                    if ' ' in item.text.strip():
                        (name, data) = item.text.split(' ', 1)
                    else:
                        (name, data) = (item.text, '')
                    if name in (KID_PI, KID_ALT_PI, KID_OLD_PI):
                        if data:
                            code.insert_block(data)
                    else:
                        c = self.depth and code or self.expand_code
                        c.line('_e = ProcessingInstruction(%r, %r)' \
                                  % (name, data) )
                        c.line('yield (START, _e); yield (END, _e); del _e')
                        del c
                else:
                    layout = None
                    if code is self.module_code:
                        layout = item.get(QNAME_LAYOUT)
                        if layout is not None:
                            del item.attrib[QNAME_LAYOUT]
                        decl = ['class Template(']
                        extends = item.get(QNAME_EXTENDS)
                        parts = []
                        if extends is not None:
                            del item.attrib[QNAME_EXTENDS]
                            for c in extends.split(','):
                                parts.append('template_util.get_base_class(%s, __file__)' % c)
                        parts.append('BaseTemplate')
                        decl.append(','.join(parts))
                        decl.append('):')
                        code = self.class_code
                        code.start_block(''.join(decl))
                        code.line('_match_templates = []')
                        code = self.expand_code
                        del decl, parts
                    self.def_proc(item, item.attrib, code)
                    if layout is not None:
                        old_code = code
                        code = CodeGenerator(level=1)
                        code.start_block("def _pull(self):")
                        code.line('kw = dict(layout_params)')
                        code.line('kw.update(self.__dict__)')
                        # XXX hack: this could be avoided if template args were not stored in self.__dict__
                        # Note: these names cannot be passed to the layout template via layout_params
                        code.line('kw.pop("assume_encoding", None)')
                        code.line('kw.pop("_layout_classes", None)')
                        code.line('temp = template_util.get_base_class(%s, __file__)(**kw)' % layout)
                        code.line('temp._match_templates = self._match_templates + temp._match_templates')
                        code.line('return temp._pull()')
                        code.end_block()
                        self.inst_defs.append(code)
                        code = old_code
            elif ev == END and not item.tag in (ProcessingInstruction, Comment):
                break
            elif ev == TEXT:
                self.text_interpolate(item, code)
            elif ev == XML_DECL and item[1] is not None:
                self.module_code.line('encoding = %r' % item[1])
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
            code.line('layout_params["%s"] = %s' % (name, name))
            self.module_defs.append(code)

            # instance method code
            code = CodeGenerator(level=1)
            code.start_block('def %s:' % class_decl)
            code.line('exec template_util.get_locals(self, locals())')
            code.line('current, ancestors = None, []')
            self.inst_defs.append(code)
            self.match_proc(item, attrib, code)
            code.end_block()
            if attr_name == QNAME_SLOT:
                old_code.line('for _e in template_util.generate_content(self.%s()): yield _e' % name)
        else:
            self.match_proc(item, attrib, code)

    def match_proc(self, item, attrib, code):
        expr = attrib.get(QNAME_MATCH)
        if expr is not None:
            del attrib[QNAME_MATCH]
            old_code = code
            code = CodeGenerator(level=1)
            code.start_block('def _match_func(self, item, apply):')
            code.line('exec template_util.get_locals(self, locals())')
            code.line('current, ancestors = None, []')
            self.for_proc(item, attrib, code)
            code.end_block()
            code.line('_match_templates.append((lambda item: %s, _match_func))' \
                      % expr)
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
        has_content = self.content_proc(item, attrib, code)
        expr, attr = (attrib.get(QNAME_STRIP), QNAME_STRIP)
        if expr is None:
            # XXX py:omit is deprecated equivalent of py:strip
            expr, attr = (attrib.get(QNAME_OMIT), QNAME_OMIT)
        start_block, end_block = (code.start_block, code.end_block)
        line = code.line
        if expr is not None:
            del attrib[attr]
            if expr != '':
                start_block("if not (%s):" % expr)
                self.attrib_proc(item, attrib, code)
                end_block()
            else:
                # element is always stripped
                pass
        else:
            self.attrib_proc(item, attrib, code)
        if has_content:
            code.start_block(
                'for _e in template_util.generate_content(_cont, current):')
            line('yield _e')
            line('del _e')
            code.end_block()
            # XXX should we use the hardcoded content if py:content is
            # specified but returns None?
            self.stream.eat()
        else:
            self.depth += 1
            self.proc_stream(code)
            self.depth -= 1
        if expr:
            start_block("if not (%s):" % expr)
            line('yield (END, current)')
            line('current = ancestors.pop(0)')
            end_block()
        elif expr != '':
            line('yield (END, current)')
            line('current = ancestors.pop(0)')

    def attrib_proc(self, item, attrib, code):
        interp = 0
        line = code.line
        need_interpolation = 0
        names = namespaces(item, remove=1)
        for (k,v) in attrib.items():
            sub = interpolate(v)
            if id(sub) != id(v):
                attrib[k] = sub
                if isinstance(sub, list):
                    need_interpolation = 1
        expr = attrib.get(QNAME_ATTRIBUTES)

        if expr is not None:
            del attrib[QNAME_ATTRIBUTES]
            attr_text = 'template_util.update_dict(%r, "%s", globals(), locals())' \
                % (attrib, expr.replace('"', '\\\"'))
            attr_text = 'template_util.make_attrib(%s,self._get_assume_encoding())' % attr_text
        else:
            if attrib:
                if need_interpolation:
                    attr_text = 'template_util.make_attrib(%r,self._get_assume_encoding())' % attrib
                else:
                    attr_text = repr(attrib)
            else:
                attr_text = '{}'
        line('ancestors.insert(0, current)')
        line('current = Element(%r, %s)' % (item.tag, attr_text))
        if len(names):
            code.start_block('for _p, _u in %r.items():' % names)
            line('if not _u in omit_namespaces: yield (START_NS, (_p,_u))')
            code.end_block()
        line('yield (START, current)')

    def content_proc(self, item, attrib, code):
        expr = attrib.get(QNAME_CONTENT)
        if expr is not None:
            del attrib[QNAME_CONTENT]
            code.line('_cont = %s' % expr)
            return 1

    def text_interpolate(self, text, code):
        interp = 0
        line = code.line
        sub = interpolate(text)
        if isinstance(sub, list):
            code.start_block('for _e in %r:' % sub)
            code.line('for _e2 in template_util.generate_content(_e): yield _e2')
            code.end_block()
        else:
            line('yield (TEXT, %r)' % sub)

class SubExpression(list):
    def __repr__(self):
        return "[%s]" % ', '.join(self)

_sub_expr = re.compile(r"(?<!\$)\$\{(.+?)\}")
_sub_expr_short = re.compile(r"(?<!\$)\$([a-zA-Z][a-zA-Z0-9_\.]*)")

def interpolate(text):
    parts = _sub_expr.split(text)
    if len(parts) == 1:
        parts = _sub_expr_short.split(text)
        if len(parts) == 1:
            return text.replace('$$', '$')
        else:
            last_checked = len(parts)
    else:
        last_checked = -1
    new_parts = SubExpression()
    i = 0
    while i < len(parts):
        part = parts[i]
        if (i % 2) == 1:
            # odd positioned elements are code
            new_parts.append(part)
        elif part:
            # even positioned elements are text
            if i >= last_checked:
                more_parts = _sub_expr_short.split(part)
                parts[i:i+1] = more_parts
                last_checked = i + len(more_parts)
                continue
            else:
                new_parts.append(repr(part.replace('$$', '$')))
        i += 1
    return new_parts


class CodeGenerator:
    """A simple Python code generator."""

    level = 0
    tab = '\t'

    def __init__(self, code=None, level=0, tab='\t'):
        self.code = code or []
        if level != self.level:
            self.level = level
        if tab != self.tab:
            self.tab = tab

    def line(self, text):
        self.code.append('%s%s' % (self.tab * self.level, text))

    def start_block(self, text):
        self.line(text)
        self.level+=1

    def end_block(self, nblocks=1, with_pass=False):
        for n in range(nblocks):
            if with_pass:
                self.line('pass')
            self.level-=1

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

# Auxiliary function

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

# Python < 2.3 compatibility
try:
    enumerate
except NameError:
    def enumerate(seq):
        for i, elem in zip(range(len(seq)), seq):
            yield (i, elem)
