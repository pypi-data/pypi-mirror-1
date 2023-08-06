from repoze.cssutils import css

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

def parse_xss(stream):
    stylesheet = open(stream, 'rb')
    parser = css.CSSParser()
    rules = parser.parseFile(stylesheet)
    
    elements = []    
    for selector, declarations in rules.items():            
        
        # reformat lists
        for k, v in declarations.items():
            if isinstance(v, list):
                declarations[k] = string.join(v,', ')
        
        selector_str = selector.asString()
        
        # append namepace when combination qualifier (ie. html>head)
        for q in selector.qualifiers:
            if isinstance(q, css.CSSSelectorCombinationQualifier):
                if q.asString().startswith('html'):
                    selector_str = '%s|%s' % (
                        namespace, selector.asString())

        element = Element(selector_str, namespaces, **declarations)
        elements.append(element)
    
    return elements