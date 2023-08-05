"""Kid tranformations"""

from __future__ import generators

__revision__ = "$Rev: 53 $"
__date__ = "$Date: 2005-02-15 08:10:35 -0500 (Tue, 15 Feb 2005) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

from types import GeneratorType
from kid.pull import ElementStream, START, XML_DECL,  _coalesce
from kid.namespace import Namespace
from template_util import generate_content

def transform_filter(stream, template):
    templates = template._get_match_templates()
    def apply_func(item):
        return transform_filter(generate_content(item), template)
    stream = ElementStream.ensure(stream)
    for ev, item in apply_matches(stream, template, templates, apply_func):
        yield ev, item

def apply_matches(stream, template, templates, apply_func):
    for ev, item in stream:
        if ev == START:
            matched = 0
            for i in range(0, len(templates)):
                (match, call) = templates[i]
                if match(item):
                    item = stream.expand()
                    newstream = _coalesce(call(template, item, apply_func),
                        template._get_assume_encoding())
                    if len(templates) < 2:
                        for ev, item in newstream:
                            yield (ev, item)
                    else:
                        for ev, item in apply_matches(ElementStream(newstream),
                            template, templates[:i] + templates[i+1:], apply_func):
                                yield ev, item
                    matched = 1
                    break
            if matched:
                continue
        yield (ev, item)

# XXX haven't tested this yet..
def xinclude_filter(stream, template):
    xi = Namespace('http://www.w3.org/2001/XInclude')
    include = xi.include
    fallback = xi.fallback
    for ev, item in stream:
        if ev == START and item.tag == xi.include:
            item = item.expand()
            href = item.get('href')
            try:
                doc = document(href, template._get_assume_encoding())
            except:
                fallback_elm = item.find(fallback)
                for ev, item in ElementStream(fallback_elm).strip(1):
                    yield ev, item
            else:
                for ev, item in doc:
                    if ev != XML_DECL:
                        yield ev
