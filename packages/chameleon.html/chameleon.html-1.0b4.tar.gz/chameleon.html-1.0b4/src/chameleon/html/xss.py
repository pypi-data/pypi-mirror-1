from repoze.cssutils import css
from repoze.cssutils.parser import CSSParseError

import re
import string
import chameleon.core.config

class Element(object):
    def __init__(self, selector, namespaces, name="",
                 attributes=None, structure=False, mode='content', **kwargs):
        if kwargs:
            for name in kwargs:
                raise ValueError("Unknown property: %s" % repr(name))
        self.namespaces = namespaces
        self.selector = selector
        self.name = name
        self.mode = mode
        self.attributes = attributes
        self.structure = structure

namespace = 'xmlns'
namespaces = {namespace: chameleon.core.config.XHTML_NS}

re_unqoute = re.compile(r'["\']')
re_tag = re.compile('([.#:])?([A-Za-z]+(\[[^\]]+\])?)')

def parse_xss(filename):
    stylesheet = open(filename, 'rb')
    parser = css.CSSParser()
    
    try:
        rules = parser.parseFile(stylesheet)
    except CSSParseError, e:
        e.setFilename(filename)
        raise
    
    elements = []    
    for selector, declarations in rules.items():            
        
        # reformat lists
        for k, v in declarations.items():
            if isinstance(v, list):
                declarations[k] = string.join(v,', ')
        
        selector_str = selector.asString()
        element = Element(selector_str, namespaces, **declarations)
        elements.append(element)
    
    return elements
