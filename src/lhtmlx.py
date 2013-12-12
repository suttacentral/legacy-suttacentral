"""
lxml.html extended.

Makes lxml.html easier to use in the python3 ecosystem and also
correctly handles text/tail transformations for some common
manipulations.

The only HtmlElement method which is overidden by this module is __str__, 
which now returns the html code of the element.
    
"""

import lxml.html as _html
import lxml.etree as _etree
import functools as _functools
from html import escape # lxml.html doesn't define it's own escape
import regex as _regex

class HtHtmlElementMixin:
    """ Adds methods primarly to aid with proper handling of text/tail.
    
    Also adds some convenience methods.
    
    """
    
    def __str__(self): 
        return _html.tostring(self, encoding='utf8').decode()
    
    def detach(self):
        """ Detach the element from the tree for re-insertion
        
        Like drop_tree but there are two differences, first, the
        tail is automatically removed (drop_tree always leaves the tail
        in the document, but it also leaves it attached to the dropped
        tag), secondly, the dropped element is returned as a convenience
        for re-insertion.
        
        >>> p = fromstring('<p><em>p1</em>Once upon a time...</p>')
        >>> p.append(p.find('em').detach())
        >>> str(p)
        '<p>Once upon a time...<em>p1</em></p>'
        
        
        """
        
        self.drop_tree()
        self.tail = None
        return self
    
    def prepend(self, other):
        """Inserts other at the start of self.
        
        Unlike .insert(0, other), handles text properly.
        
        >>> p = fromstring('<p>There can be only one.</p>')
        >>> p.insert(0, p.makeelement('a', {'id': 'wrong'}))
        >>> str(p)
        '<p>There can be only one.<a id="wrong"></a></p>'
        >>> p.prepend(p.makeelement('a', {'id': 'right'}))
        >>> str(p)
        '<p><a id="right"></a>There can be only one.<a id="wrong"></a></p>'
        
        
        """
        
        self.insert(0, other)
        if self.text:
            other.tail = self.text + (other.tail or '')
            self.text = None
    
    def wrap_outer(self, other):
        """Wrap self in other
        
        >>> dom = fromstring('<div><a>foo</a>bar</div>')
        >>> dom.find('a').wrap_outer(dom.makeelement('b'))
        >>> str(dom)
        '<div><b><a>foo</a></b>bar</div>'
        
        """
        
        self.addprevious(other)
        other.tail = self.tail; self.tail = None
        other.append(self)

    def wrap_inner(self, other):
        """Wrap the contents of self inside other
        
        >>> dom = fromstring('<div><a>foo</a>bar</div>')
        >>> dom.find('a').wrap_inner(dom.makeelement('i'))
        >>> str(dom)
        '<div><a><i>foo</i></a>bar</div>'
        
        """
        
        other.extend(self)
        other.text = self.text; self.text = None
        self.append(other)
        
    def select(self, selector):
        """ Shorthand for csssselect, less sss's
        
        Also much faster for the simple case of selecting simply by tag 
        name(s), cssselect is quite slow especially when many elements are
        returned, the highly optimized iter can be 5-400x faster.
        
        """
        
        parts = [s.strip() for s in selector.split(',')]
        if all(map(str.isalpha, parts)):
            return list(self.iter(*parts))
        return self.cssselect(selector)
    
    def convert_bad_tags(self):
        """ Convert invalid html tags into div/span class="tag"
        
        Uses a simple heurestic to decide whether it should be a span
        or div, an element which contains block level elements will
        be a div, otherwise it will be span.
        
        >>> dom = fromstring('<baa><p><moo>Goes the cow</namo> ...')
        >>> dom.convert_bad_tags()
        >>> str(dom)
        '<div class="baa"><p><span class="moo">Goes the cow ...</span></p></div>'
        
        
        """
        
        validtags = _html.defs.tags
        blocktags = _html.defs.block_tags
        
        for e in self.iter():
            if e.tag not in validtags:
                e.attrib['class'] = (e.attrib['class'] + ' ' + e.tag 
                                        if 'class' in e.attrib 
                                        else e.tag)
                e.tag='span'
                for desc in e.iterdescendants():
                    print(e.tag)
                    if desc.tag in blocktags:
                        e.tag='div'
                        break
            
    
    def pretty(self):
        """ Return a string with prettified whitespace """
        string = _html.tostring(self, encoding='utf8', pretty_print=True).decode()
        extra_tags = ('article', 'section', 'hgroup')
        string = _regex.sub(r'(<(?:{})[^>]*>)'.format('|'.join(extra_tags)), r'\n\1\n', string)
        string = _regex.sub(r'(</(?:{})>)'.format('|'.join(extra_tags)), r'\1\n', string)
        string = string.replace('<br>', '<br>\n')
        string = string.replace('\n\n', '\n')
        return string
    
# We need to jump through some hoops to ensure the mixins are included
# in all Element class for every tag type. (in lxml.html, some, like input
# and select, have a custom element type, these require the mixins parameter
# to set_element_class_lookup, but there the mixins don't apply to any
# non-customized tag, so we also need to manually mix them into a new
# HtmlElement and create a CustomLookup class which returns our new
# HtmlElement class as the default)
class HtHtmlElement(_html.HtmlElement, HtHtmlElementMixin):
    pass

class CustomLookup(_html.HtmlElementClassLookup):
    """ Returns CustomHtmlElement by default
    
    Oddly enough HtmlElement is hardcoded as the default in
    lxml.html.HtmlElementClassLookup which seems really strange, mixins will be
    properly mixed into custom classes (like Select) but not the default.
    """
    def lookup(self, node_type, document, namespace, name):
        if node_type == 'element':
            return self._element_classes.get(name.lower(), HtHtmlElement)
        super().lookup(node_type, document, namespace, name)

# lxml still has a number of issues handling utf8. We need to
# explicitly define that our parser is using utf-8 for some systems.
# http://stackoverflow.com/questions/15302125/html-encoding-and-lxml-parsing        

utf8parser = _html.HTMLParser(encoding='utf-8')
utf8parser.set_element_class_lookup(CustomLookup(mixins=[('*', HtHtmlElementMixin)]))

def fromstring(string):
    return _html.fromstring(string, parser=utf8parser)

def fragment_fromstring(string):
    return _html.fragment_fromstring(string, parser=utf8parser)

def fragments_fromstring(string):
    return _html.fragments_fromstring(string, parser=utf8parser)

def document_fromstring(string):
    return _html.document_fromstring(string, parser=utf8parser)

def parse(filename):
    return _html.parse(filename, parser=utf8parser)

def htmlfiles(path):
    """Iterates over all html files in ``path``
    """
    import os
    for dirpath, dirnames, filenames in os.walk(path):
        filenames.sort(key=lambda s: [int(i) for i in _regex.findall('\d+', s)])
        filenames.sort(key=lambda s: _regex.match('(\p{alpha}*)', s)[0])
        for filename in filenames:
            infile = os.path.join(dirpath, filename)
            if filename.endswith('.html') or filename.endswith('.htm'):
                yield infile

if __name__ == "__main__":
    import doctest
    doctest.testmod()
