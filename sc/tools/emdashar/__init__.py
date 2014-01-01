#!/usr/bin/env python

import regex
from .mutablesuperstring import MutableSuperString, wraptext, unwraptext
from .loggers import SortedLogger, SilentLogger

class Rule:
    """Contains a Regex pattern => replacement rule"""
    def __init__(self, label, pattern, repl, flags=None, _seen=set()):
        if label in _seen:
            raise ValueError('label must be unique')
        _seen.add(label)
        self.label = label
        self.pattern = regex.compile(pattern)
        self.repl = repl
        self.flags = list(flags) if flags is not None else []
    def __lt__(self, other):
        return self.label < other.label
    def __eq__(self, other):
        return self.label == other.label

R = Rule

abbrs = r'etc|lit|viz|cf|s\.v\.|ff|\d\p{alpha}|Skt'
rules = [
    # All rules must use lookahead/behind assertions wherever possible
    # because content in a seperate tag can only be 'seen' with
    # lookahead/behind assertions.
    # As a further constraint:
    # -regexes which replace content must match only what is to be repaced
    # -regexes which remove content must match only what is to be removed
    # -regexes which insert content should match zero or one characters.
    # Provided these restraints are honored, emdashar will deal seamlessly
    # with xml and HTML. Single character matches will always work
    # perfectly, multiple-character matches will break when intersected
    # by a tag, thus single character matches are to be preferred.
    

    # Remove superflous spaces
    R(0, r"\n +", "\n"),
    R(2, r"  +", r" "),
    
    # Periods should be converted to ellipses
    R(4, r"\.{3,}", r"…"),
    R(5, r"\. \. \.", r"…"),

    R(6, r"(?<!(?:"+abbrs+"))\.[.,]?", r"."),

    # Period followed by ! or ?
    R(8, r"\.([?!])\1*", r"\1"),
    
    # Duplicate Puncuation
    R(10, r"([!?])[!?.]+", r"\1"),

    # Ellipses should have a space on either side, except '.,?!'
    R(12, r"(?<=\S)…(?!\p{Term})", r" …"),
    R(13, r"…(?![\s.,;!?])", r"… "),

    #Fake doubleopenquote >> actual quote
    R(20, r"``((?:(?!''|``).){,500})''", r"“\1”"), # evil regex
    R(21, r"``", "“"),
    R(22, r"''", '"'), # Apply later functions to this case.
    R(23, r"‘‘([^‘’]+)’’", '“\1”'),
    R(24, r"‘‘", '“'),
    R(25, r"’’", '”'),

    # Tick in a word, as in isn't. Treating as close quote is okay except
    # in one case: Then I said'Foo!'. Between two lowercase is okay.
    # This would be a good candidate for interactive.
    R(26, r"'(?=.(?<=\p{Lower}'\p{Lower}))", "’"),

    #Evil ascii single quotes >> unicode single quotes (common case)
    R(28, r"(?<=\s)`([^`']+)'(?=[\s.,?!\]\)])", r"‘\1’"),

    #Evil ascii double quotes >> unicode double quotes (common case)
    R(29, r'(?<=\s|^)"(?=\w)([^"“”]+)"(?=[\s.,?!:;\)\]]|$)', r"“\1”"),

    #Use neighbouring newlines to definitely determine open/close quotes.
    R(30, r'^ ?"', r"“"),
    R(32, r'^ ?”', r"“"),
    R(34, r'(?<!\n\w*)"(?=\W*\n)', r"”"),

    R(35, r"(?<=^|\n\W*)'(?!\W*\n)", r"‘"),
    R(36, r"(?<!\n\w*)'(?=\W*\n)", r"’"),
    
    #Straight double quotes >> open quote
    R(37, r"""(?x)
            (?<=\s|[:—]\s+)  # Preceeded by nearby space or emdash/colon
            "                # Doubletick
            (?=\w|\S{3})     # Proceeded by no nearby space.
        """, "“"),
    #Straight single quote >> open quote
    R(358, r"""(?x)
            (?<=\s.{,2})     # Preceeded by a nearby space.
            '                # Singlequote
            (?=\S{3})        # Proceeded by no nearby space.""",
        "‘"),
    #Straight double quote >> close quote
    R(39, r"""(?x)
            (?<=\S{3})    # Preceeded by no nearby space.
            "             # Doublequote
            (?=.{,2}\s)   # Proceeded by a nearby space.""",
        "”"),
    #straight single quote >> close quote
    R(40, r"""(?x)
            (?<=\S{3})       # Preceeded by no nearby space.
            '                # Singlequote (not isn't)
            (?=.{,2}\s)      # Proceeded by a nearby space.""",
        "’"),
    #Obviously mismatched close-quote
    R(41, r"(?<=\w)“(?=\.(?:\s|$))", "”"),
    R(42, r"(?<=\w[.?!]?)“(?=\s*\n)", "”"),

    R(45, r"(?<=\w)”(?=s)", r"’"),
    
    #Ambigious straight quote decided as 'close' by proceeding open quote.
    R(46, r"\"(?=[^”\"]+“)", "”"),
    #Ambigious close quote decided as 'open' by proceeding close quote.
    R(47, r"\"(?=[^“\"]+”)", "“"),
    #Ambigious straight quote decided as 'close' by proceeding open quote.
    R(48, r"'(?=[^’']+‘)", "‘"),
    #Ambigious straight quote decided as 'open' by proceeding close quote (complexity is mainly filtering out isn't types)
    R(49, r"'(?=[^‘']+’(?=.(?<!\w’\w)))", "‘"),
    R(50, r"(?<=\w)`(?=[^‘']+’(?=.(?<!\w’\w)))", " ‘"),
    
    R(51, r'“ ‘', '“‘'),

    # A colon possibly followed by by space/hyphens and a quote => emdash
    # newlines are preserved, hyphens and spaces eliminated.
    R(60, r'(”.\s+)\p{dash}+(\s*“)', r'\1—\2'),
    R(60.1, r'(?<=[”’]) -[- ]*(?=[“‘\p{alpha}])', r'—'),
    R(61, r': ?(\n*)[ -]*(?<!:\n+)(?=[“‘])', r': \1'),
    R(62, r'(?<=[\w\.]) -[- ]*(?=[”’])', r':'),
    R(63, r'(?<=[\w\.])- [- ]*(?=[”’])', r':'),

    #Dash -> Colon
    R(64, r'(?<!”\s*)\p{dash}(?:\s(?<=\n)(?=\s))?(?=\W*[“‘])', r':'),
    
    # Catchall colon+hyphen with no quote.
    R(65, r'(?<=\p{alpha}):\s?-[-\s]*', r'—'),
    R(66, r'(?<=\p{alpha}),\s?-[-\s]*', r'—'),
    R(67, r'--\s*', r'—'),
    R(68, r'(?<=\p{alpha}) -\s*(?=\p{alpha})', r'—'),
    R(69, r'— +(?!“)', r'—'),
    
    
    # Special case involving spaced hyphen between numbers
    R(70, r"(?=\d) -[- ]*(?=\d)", r"–"),
    # Any kind of dash between numbers.
    R(71, r"""(?x)# Verbose
        (?<=\d+)        # number
        (?<!\d+-\d+)    # date (negates match)
        \p{dash}\s?+ # (spaced) dash of some kind
        (?=.(?<!\d–\d)) # A good honest non-spaced endash negates previous
        (?!\d+-\d+)     # date (negates match)
        (?=\d+)         # number""", r"–"),
        
    # Emdash 
    R(72, r"""(?x)
        (?<=[[:alpha:]])    # An alphabetical character
        \p{dash}-*\ ?+   # A possibly spaced dash of some kind
        (?<!\S—(?=\w|\s+[“‘]))# Which is not a good honest emdash
        (?<!\w-(?=\w))      # Or a good honest hyphen
        (?=[[:alpha:]]|$)   # Followed by an alphabetical character or EOL
        """, r'—'),
    # Emdash2
    R(73, r"""(?x)
        ”             # A close quote (anchors pattern)
        (?:-- *|\ -+\ *) # Followed by an ascii emdash
        (?=\p{alpha}) # An an alphabetical character
        """, r"” —"),

    #Unspaced Open Puncuation
    R(80, r"(?<![\s‘—/(/[]|^)“", r" “"),
    R(81, r"(?<![\s“—/(/[]|^)‘", r" ‘"),
    
    #Unspaced Close Puncuation
    R(82, r"”(?!$|\p{Term}|\s|’|—|ti)", r"” "),
    #There's not much we can do with the single quote

    #Pre-spaced comma/period
    R(83, r" (\p{Term})", r"\1"),
    
    #Unspaced comma
    R(84, r",(?=\p{alpha})", r", "),
    R(85, r"\?(?=\p{alpha})", r"? "),
    R(86, r"!(?=\p{alpha})", r"! "),

    #Unspaced period - More care is required here. To be conservative
    #only replace 'Foobar.Baz' and some other dodgies)
    R(87, r"\.(?=.(?<=\p{Lower}\.[\p{Upper}\(\[{]))", r". "),
    
    #Fix mis-matched brackets (permit smileys out of kindness of heart :-])
    #R(, r"\((?!-?[:;])([^(]*)\](?<![:;]-?])", r"(\1)"),
    #R(, r"\[(?!-?[:;])([^(]*)\)(?<![:;]-?\))", r"(\1)"),
    R(88, r"\((\w+)\]", r"(\1)"),
    R(89, r"\[(\w+)\)", r"(\1)"),
    
    # Add space to front of [({, end of ])}
    R(90, r"(?<=\p{alpha})(\p{gc=Open_Punctuation})(?!\p{alpha}\p{gc=Close_Punctuation})", r" \1"),
    R(91, r"(\p{gc=Close_Punctuation})(?=\p{alpha})", r"\1 "),

    # Fix capitalization
    R(92, r"(?<=\p{Lower}(?<!"+abbrs+"))(\.\s+)(\p{Lower})", lambda m: m[1] + m[2].upper()),
    R(93, r"(?<=\p{Lower})(\?\s+)(\p{Lower})", lambda m: m[1] + m[2].upper()),
    R(94, r"(?<=\p{Lower})(\!\s+)(\p{Lower})", lambda m: m[1] + m[2].upper()),
    
    R(100, r"À(?=[^‘]+’)", "‘A"),
    R(101, r"Ì(?=[^‘]+’)", "‘I"),
    
    ]

class Emdashar:
    """Responsible for emdashing an input element"""

    def __init__(self, logger = None):
        if logger is None:
            logger = SilentLogger()
        self.logger = logger
    
    _texttag = 'x27bVcHfS' # Probably not an existing tag name.    
    
    def text_iter(self, element, ignore_tags = None, permit_tags = None):
        """Iterate over special 'text' elements

        if permit is specified, matching tags are permitted.
        if ignore is specified, matching tags are ignored.
        Permit and ignore may be space or comma seperated tag names,
        or they may be a iterable of strings."""
        if type(ignore_tags) is str:
            ignore_tags = set(regex.split(r'[,\s]+', ignore_tags))
        elif ignore_tags is not None:
            ignore_tags = set(ignore_tags)
        
        if type(permit_tags) is str:
            permit_tags = set(regex.split(r'[,\s]+', permit_tags))
        elif permit_tags is not None:
            permit_tags = set(permit_tags)
        
        for e in element.iter(self._texttag):
            parent = e.getparent()
            if permit_tags is None or parent.tag in permit_tags:
                if ignore_tags is None or parent.tag not in ignore_tags:
                    yield e
    
    def emdash(self, element, ignore_tags = None, permit_tags = None):
        
        wraptext(element, self._texttag)
        try:
            textiter, sourcelineiter = zip(*((e.text, e.sourceline)
                                        for e in list(self.text_iter(element, ignore_tags=ignore_tags))))
            resultiter = self.apply_rules(textiter, sourcelineiter)
            for node, text in zip(self.text_iter(element, ignore_tags=ignore_tags), resultiter):
                node.text = text
        except ValueError:
            pass
        finally:
            unwraptext(element, self._texttag)
        
        return element
    
    def apply_rules(self, strings, sourcelines=None):
        """Process all strings in iter"""

        #Build a MSS from the text content of the element (in-order)

        mss = MutableSuperString(strings, sourcelines=sourcelines, logger=self.logger)
        for rule in rules:
            #self.logger.print(" === Applying rule {:<2} === ".format(rule.label))
            self.logger.rule = rule
            mss.sub(rule.pattern, rule.repl)
        
        return mss
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
