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
import io as _io

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
    
    """

    # The open tag for these elements are put on it's own line.
    # (Exception: If close tag immediately follows)
    block_ownline_open = {'html','head','body','div','section',
        'article', 'hgroup', 'blockquote', 'header', 'footer', 'nav', 'menu',
        'meta', 'ul', 'ol', 'table', 'tr', 'tbody', 'thead', 'p'}

    block_ownline_close = block_ownline_open - {'p', 'li', 'td', 'html'}

    # These can be lumped with elements that follow
    block_ownline_if_followed_by_text = {'li', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}

    # These are placed on their own line as a whole (\n<tag>text</tag>\n)
    inline_newline_open_before = {'a', 'span', 'strong', 'em', 'title', 'cite'}
    inline_newline_close_after = {'a'}


    always_newline_after = {'br', 'hr', 'p'}

    preserve = {'script', 'style', 'pre'}

    opentagrex = _regex.compile(r'''<(?<name>\w+)\s*(?<attrs>[\w-]+(?:\s*=\s*(?:'[^']*'|"[^"]*"|\S+))?\s*)*(?<selfclosing>/?)>''')
    closetagrex = _regex.compile(r'</(?<name>\w+)>')
    doctyperex = _regex.compile(r'<!DOCTYPE (?<type>[^>]+>)')
    commentrex = _regex.compile(r'<!--.*?-->')
    datarex = _regex.compile(r'[^<]+')
    script_content_rex = _regex.compile(r'.*?(?=</script>)')
    def __init__(self, output=None):
        from textwrap import TextWrapper
        self.wrap = 79
        self.output = output
        self.line = ''
        self.text_wrapper = TextWrapper(width=self.wrap, 
                replace_whitespace=False, drop_whitespace=False,
                break_long_words=False, break_on_hyphens=False)
        self.nl_please = False # Convert the next space into a nl
        self.nl_okay = False # A nl can be inserted without altering appearance.
    
    def feed(self, data):
        m = None
        token = None
        start = 0
        while True:
            if m: # This is the match from the previous token
                start = m.end()
                if start == len(data):
                    return

            m = None
            if data[start] == '<':
                m = self.opentagrex.match(data, pos=start)
                if m:
                    if m['selfclosing']:
                        self.selfclosingtag(m['name'].lower(), m['attrs'], m[0])
                    else:
                        self.opentag(m['name'].lower(), m['attrs'], m[0])
                    continue

                m = self.closetagrex.match(data, pos=start)
                if m:
                    self.closetag(m['name'].lower(), m[0])
                    continue
                
                m = self.commentrex.match(data, pos=start)
                if m:
                    self.comment(m[0])
                    continue
                
                m = self.doctyperex.match(data, pos=start)
                if m:
                    self.doctype(m[0])
                    continue
            else:
                m = self.datarex.match(data, pos=start)
                if m:
                    self.data(m[0])
                    continue

            from .webtools import ProcessingError
            raise ProcessingError('Unable to parse: {}'.format(data[start:start+150] + ' ...'))

    def doctype(self, raw):
        self.write(raw)
        self.nl()

    def opentag(self, tag, attrs, raw):
        tag = tag
        if tag in self.block_ownline_open:
            self.nl()
            self.nl_okay = True
        elif tag in self.inline_newline_open_before:
            if self.line.endswith(' ') or self.nl_okay:
                self.nl()
            else:
                self.nl_please = True

        self.write(raw)
        
        if (tag in self.block_ownline_open or
            tag in self.always_newline_after):
            self.nl()

    def closetag(self, tag, raw):
        tag = tag
        if tag in self.block_ownline_close:
            self.nl()
        self.write(raw)

        if (tag in self.block_ownline_close or
                tag in self.block_ownline_if_followed_by_text or
                tag in self.always_newline_after):
            self.nl()
        elif tag in self.inline_newline_close_after:
            if self.line.endswith(' ') or self.nl_okay:
                self.nl()
            else:
                self.nl_please = True

    def selfclosingtag(self, tag, attrs, raw):
        tag = tag
        if (tag in self.block_ownline_open or 
            tag in self.block_ownline_if_followed_by_text):
            self.nl()
        self.write(raw)
        
        if (tag in block_ownline_close or 
            tag in self.block_ownline_if_followed_by_text or 
            tag in self.always_newline_after):
            self.nl()

    def comment(self, raw):
        self.write(raw)
        self.nl()

    def data(self, raw):
        # Data is the only thing we split.
        self.write(raw, True)
        self.nl_okay = False

    # Out commands
    def nl(self):
        self.nl_please = False
        self.nl_okay = True # A forced nl implies that newlines are okay.
        if not self.line:
            return
        else:
            self.output.write(self.line.rstrip())
            self.output.write('\n')
            self.line = ''

    def write(self, string, splittable=False):
        if self.line == '':
            string = string.lstrip()
            if not string:
                return
        
        if not splittable:
            if (self.line.endswith(' ') or self.nl_okay) and len(self.line) + len(string) > self.wrap:
                self.nl()
            self.line += string
        else:
            # We can split! Use TextWrapper class to do heavy lifting.
            # TextWrapper is a bit relaxed about overlong words when
            # not allowed to break them, it lets the sentence overrun
            # when it could break it before the overlong word, but
            # this is a tolerable way of handling overlong words.

            if self.nl_please:
                if string.startswith(' '):
                    string = string[1:]
                    self.nl()
                    if not string:
                        return
                elif self.nl_okay:
                    self.nl()
            
            # Attempt to split the line at the last space
            m = _regex.match(r'(.*)( [^<>]*)$', self.line)
            if m:
                self.line = m[1]
                string = m[2] + string

            self.text_wrapper.initial_indent = self.line
            lines = self.text_wrapper.wrap(string)
            if not lines:
                self.line += string
                return
            
            for line in lines[:-1]:
                if not line:
                    continue
                self.output.write(line.strip())
                self.output.write('\n')

            self.line = self.laststr = self.lastdata = lines[-1].lstrip()

    def flush(self):
        if self.line and self.output:
            self.output.write(self.line)
            self.line = self.laststr = self.lastdata = ''

    def __del__(self):
        self.flush()

    def prettyprint(self, text, filename='(-)', output=None):
        self.output = output or _io.StringIO()
        

        rex = _regex.compile(r'(?si)<({0}).*?</\1>|(?:(?:[^<]+)|<(?!{0}))+'.format('|'.join(self.preserve)))
        
        for m in rex.finditer(text):
            if m[1]:
                self.nl()
                self.output.write(m[0].strip())
                self.nl()
            else:
                chunk = m[0].replace('\n', ' ')
                chunk = _regex.sub(r' {2,}', ' ', chunk)
                self.feed(chunk)
                self.flush()

        if output:
            return
        else:
            out = self.output.getvalue()
            out = _regex.sub(r' ++(?=</(?:p|li|td)>|<br>|$)', '', out)
            return out

prettyprint = PrettyPrinter().prettyprint

if __name__ == "__main__":
    import doctest
    doctest.testmod()
