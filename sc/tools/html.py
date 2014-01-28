"""
lxml.html extended.

Makes lxml.html easier to use in the python3 ecosystem and also
correctly handles text/tail transformations for some common
manipulations.

The only HtmlElement method which is overidden by this module is __str__, 
which now returns the html code of the element.
    
"""

import lxml.html as _html
from lxml.html import tostring, xhtml_to_html, defs
import lxml.etree as _etree
import functools as _functools
from html import escape # lxml.html doesn't define it's own escape
import regex as _regex

defs.html5_tags = frozenset({'section', 'article', 'hgroup'})

class CssSelectorFailed(Exception):
    " The exception returned by select_or_fail "
    def __init__(self, selector):
        self.selector = selector
    def __str__(self):
        return 'No matches for "{}"'.format(self.selector)

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
    
    def select_one(self, selector):
        """ Returns the first matching element, or None """
        
        result = self.select(selector)
        if result:
            return result[0]
        return None
    
    def select_or_fail(self, selector):
        """ Raises ``CssSelectorFailed`` instead of returning an empty list
        
        """
        
        result = self.select(selector)
        if not result:
            raise CssSelectorFailed(selector)
        return result
    
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
            
    
    def pretty(self, **kwargs):
        """ Return a string with prettified whitespace """
        string = _html.tostring(self, pretty_print=True, **kwargs).decode()
        extra_tags = ('article', 'section', 'hgroup')
        string = _regex.sub(r'(<(?:{})[^>]*>)'.format('|'.join(extra_tags)), r'\n\1\n', string)
        string = _regex.sub(r'(</(?:{})>)'.format('|'.join(extra_tags)), r'\n\1\n', string)
        string = string.replace('<br>', '<br>\n')
        string = string.replace('\n\n', '\n')
        string = _regex.sub(r'\n +', '\n', string)
        return string
    
    @property
    def headsure(self):
        """ Returns head, creating it if it doesn't exist """
        try:
            return self.head
        except IndexError:
            head = self.makeelement('head')
            root = self.getroottree().getroot()
            assert root.tag == 'html', "Incomplete HTML tree"
            root.insert(0, head)
            return head
    
    def __bool__(self):
        """ Objects are always truthy, as in future lxml 
        
        Use 'len' to discover if contains children.
        """
        return True
    
# We need to jump through some hoops to ensure the mixins are included
# in all Element class for every tag type. (in lxml.html, some, like input
# and select, have a custom element type, these require the mixins parameter
# to set_element_class_lookup, but there the mixins don't apply to any
# non-customized tag, so we also need to manually mix them into a new
# HtmlElement and create a CustomLookup class which returns our new
# HtmlElement class as the default)
class HtHtmlElement(HtHtmlElementMixin, _html.HtmlElement):
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
def get_parser(encoding='utf-8'):    
    parser = _html.HTMLParser(encoding=encoding)
    parser.set_element_class_lookup(CustomLookup(mixins=[('*', HtHtmlElementMixin)]))
    return parser

utf8parser = get_parser('utf-8')

def fromstring(string):
    return _html.fromstring(string, parser=utf8parser)

def fragment_fromstring(string):
    return _html.fragment_fromstring(string, parser=utf8parser)

def fragments_fromstring(string):
    return _html.fragments_fromstring(string, parser=utf8parser)

def document_fromstring(string):
    return _html.document_fromstring(string, parser=utf8parser)

def parse(filename, encoding='utf8'):
    # It seems that lxml.html always guesses the charset regardless
    # of charset declarations. On Linux, if a charset is not specified
    # it will correctly recognize utf8 and utf16. But on some systems
    # it wont recognize utf8?
    
    encoding = encoding.upper()
    if encoding in ('UTF8', 'UTF-8'):
        parser = utf8parser
    elif encoding in ('UTF16', 'UTF-16'):
        parser = get_parser('UTF-16')
    elif encoding == "DECLARED":
        if not hasattr(filename, 'read'):
            filename = open(filename, 'rb')
        start = filename.read(250)
        filename.seek(-250)
        if b'<\x00' in start:
               parser = get_parser("UTF-16LE")
        elif b'\x00<' in start:
            parser = get_parser("UTF-16BE")
        else:
            m = regex.search(r'charset=(["\']?)([\w-]+)\1', start)
            parser = get_parser(m[2])
    else:
        parser = get_parser(None)
        
    return _html.parse(filename, parser=parser)

def parseXML(filename):
    """ Parse an XML document, thus also suitable for XHTML """
    # XML doesn't require jumping through the same hoops as HTML since there
    # are no existing custom element classes.
    parser_lookup = _etree.ElementDefaultClassLookup(element=HtHtmlElement)
    parser = _etree.XMLParser()
    parser.set_element_class_lookup(parser_lookup)
    return _etree.parse(filename, parser=parser)

class PrettyPrinter:
    """ Pretty print HTML for Sutta Central
    
    Produces results which are exactly in accordance with Ven. Nandiya's
    arbitary standards for 'looks-right-ness'. Motivation is to provide
    git-friendlier HTML files by placing things which are more likely
    to be changed on their own lines and linebreaking longer
    paragraphs.
    
    The existing linebreaks are completely replaced. PrettyPrint makes
    no effort at all to reuse existing linebreaks. For this reason it
    should ideally be called *once* on each file. After that, the file
    should not be re pretty printed since doing so will cause git a hedaache.
    
    PrettyPrinter uses regular expressions and a very simple tokenizer
    to produce the desired result. It does not attempt to parse the
    document.
    
    For input it requires an HTML document with <html> tag.
    
    It does not respect '<pre>' blocks.
    
    """
    # The below sets are NOT in accordance with HTML4 or HTML5, they are
    # actually sets of tags used on Sutta Central.
    all_tags = {'a', 'address', 'article', 'b', 'big', 'blockquote', 'body',
                'cite', 'div', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'head',
                'hgroup', 'html', 'i', 'li', 'ol', 'p', 'section', 'span',
                'strong', 'sup', 'table', 'td', 'title', 'tr', 'ul'}
    
    block_tags = {'article', 'blockquote', 'body', 'div', 'h1', 'h2', 'h3', 
            'h4', 'h5', 'head', 'hgroup', 'html', 'li', 'ol', 'p', 'section', 
            'table', 'td', 'title', 'tr', 'ul'}

    inline_tags = all_tags - block_tags
    
    # These tags don't deserve an entire line to themselves
    # (i.e. <section> would be put on a line by itself)
    condense_tags = {'p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'td'}

    # This will match virtually all open-tags except extremely
    # corrupt ones (which browsers probably wouldn't handle either)
    # Slice the ends off opentag[1:-1] to make non-capturing
    opentag = r'''((?si)<(?:{})(?:[ \n\w=]+|"[^"]*"|'[^']*')*/?>)'''.format

    #slice closetag[1:-1] to make non-capturing
    closetag = r'((?si)</(?:{})>)'.format

    arex = _regex.compile(opentag('a') + '.*?' + closetag('a'))

    ownline = block_tags | {'a', 'meta', 'link', 'img'}

    ownlineopenrex = _regex.compile(opentag('|'.join(ownline)))
    ownlinecloserex = _regex.compile(closetag('|'.join(ownline)))

    nextblock = _regex.compile(r'[\w\p{{punct}}]+[ -]?|{0}.*?{1}|{0}|{1}|.'.format(
        opentag(r'\w+')[1:-1], closetag(r'\w+')[1:-1]))
        
    wrap = 78
    
    def linebreak(self, string):
        wrap = self.wrap
        if len(string) <= wrap:
            return string
        lines = ['']
        for m in self.nextblock.finditer(string):
            tok = m[0]
            if len(tok) + len(lines[-1]) < wrap or len(lines[-1]) == 0:
                lines[-1] += tok
            else:
                lines.append(tok)
        return '\n'.join(lines)

    def prettyprint(self, text, filename='(-)'):
        opentag = self.opentag
        closetag = self.closetag
        block_tags = self.block_tags
        condense_tags = self.condense_tags
        # Strip existing newlines.
        text = text.replace('\n', ' ')
        text = _regex.sub(' {2,}', ' ', text)

        # Eliminate spaces between block level tags
        text = _regex.sub(opentag('|'.join(block_tags)) + ' ', r'\1', text)
        text = _regex.sub(' ' + closetag('|'.join(block_tags)), r'\1', text)

        m = _regex.match(r'(?si)(.*?)(<html>.*</html>\n?)(.*)', text)
        preamble = m[1]
        middle = m[2]
        postamble = m[3]
        if postamble:
            if postamble.isspace():
                postamble = ''
            else:
                logger.warn('{} contains trailing content: {}'.format(filename, postamble))

        # Place certain tags on their own line
        middle = self.ownlineopenrex.sub(r'\n\1', middle)
        middle = self.ownlinecloserex.sub(r'\1\n', middle)
        middle = middle.replace('<br>', '<br>\n')
        prex = _regex.compile(r'({})(.*?)({})'.format(opentag('p')[1:-1],
            closetag('p')[1:-1]), flags=_regex.DOTALL)
        
        def parabreak(m):
            out = [m[1]]
            for line in m[2].split('\n'):
                out.append(self.linebreak(line))
            out.append(m[3])
            return '\n'.join(out)
        
        middle = prex.sub(parabreak, middle)
        
        out = '\n'.join([preamble, middle, postamble])
        
        out = out.replace('></head>', '>\n</head>')
        
        out = _regex.sub(r'\n[ \n]+', r'\n', out)
        out = _regex.sub(r'(?m) $', r'', out)
        out = _regex.sub(r'(<(?:{})>)\n'.format('|'.join(condense_tags)), r'\1', out)
        out = _regex.sub(r'\n(</(?:{})>)'.format('|'.join(condense_tags)), r'\1', out)
        
        if out.endswith('\n'):
            out = out[:-1]
        return out

prettyprint = PrettyPrinter().prettyprint

if __name__ == "__main__":
    import doctest
    doctest.testmod()
