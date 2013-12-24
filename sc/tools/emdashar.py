#!/usr/bin/env python

import regex, itertools, lxml.etree, lxml.html, os
import nandar.textwrangle as textwrangle
from nandar.textwrangle import MutableSuperString, wraptext, unwraptext, SortedLogger

R = textwrangle.Rule

c = textwrangle.UniqueCounter(0)
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

    # In terms of perfomance, one monolithic regex will perform MUCH better
    # than several smaller regexes, provided lookahead/behind assertions
    # are used wisely and appropriately.

    # Unicode properties are effecient to search, providing better
    # performance than a character range

    # Remove superfolous spaces
    R(next(c), r"\n +", "\n"),
    R(next(c), r"  +", r" "),
    
    # Periods should be converted to ellipses
    R(next(c), r"\.{3,}", r"…"),

    R(next(c), r"(?<!(?:"+abbrs+"))\.[.,]?", r"."),

    # Period followed by ! or ?
    R(next(c), r"\.([?!])\1*", r"\1"),
    
    # Duplicate Puncuation
    R(next(c), r"([!?])[!?.]+", r"\1"),

    # Ellipses should have a space on either side, except '.,?!'
    R(next(c), r"(?<=\S)…(?!\p{Term})", r" …"),
    R(next(c), r"…(?![\s.,;!?])", r"… "),

    #Fake doubleopenquote >> actual quote
    R(c(10), r"``((?:(?!''|``).){,500})''", r"“\1”"), # evil regex
    R(next(c), r"``", "“"),
    R(next(c), r"''", '"'), # Apply later functions to this case.
    R(next(c), r"‘‘([^‘’]+)’’", '“\1”'),
    R(next(c), r"‘‘", '“'),
    R(next(c), r"’’", '”'),

    # Tick in a word, as in isn't. Treating as close quote is okay except
    # in one case: Then I said'Foo!'. Between two lowercase is okay.
    # This would be a good candidate for interactive.
    R(next(c), r"'(?=.(?<=\p{Lower}'\p{Lower}))", "’"),

    #Evil ascii single quotes >> unicode single quotes (common case)
    R(next(c), r"(?<=\s)`([^`']+)'(?=[\s.,?!\]\)])", r"‘\1’"),

    #Evil ascii double quotes >> unicode double quotes (common case)
    R(next(c), r'(?<=\s)"(?=\w)([^"“”]+)"(?=[\s.,?!:;\)\]])', r"“\1”"),

    #Use neighbouring newlines to definitely determine open/close quotes.
    R(next(c), r'(?<=\n\W*)"(?!\W*\n)', r"“"),
    R(next(c), r'(?<!\n\w*)"(?=\W*\n)', r"”"),

    R(next(c), r"(?<=\n\W*)'(?!\W*\n)", r"‘"),
    R(next(c), r"(?<!\n\w*)'(?=\W*\n)", r"’"),
    
    #Straight double quotes >> open quote
    R(next(c), r"""(?x)
            (?<=\s|[:—]\s+)  # Preceeded by nearby space or emdash/colon
            "                # Doubletick
            (?=\w|\S{3})     # Proceeded by no nearby space.
        """, "“"),
    #Straight single quote >> open quote
    R(next(c), r"""(?x)
            (?<=\s.{,2})     # Preceeded by a nearby space.
            '                # Singlequote
            (?=\S{3})        # Proceeded by no nearby space.""",
        "‘"),
    #Straight double quote >> close quote
    R(next(c), r"""(?x)
            (?<=\S{3})    # Preceeded by no nearby space.
            "             # Doublequote
            (?=.{,2}\s)   # Proceeded by a nearby space.""",
        "”"),
    #straight single quote >> close quote
    R(next(c), r"""(?x)
            (?<=\S{3})       # Preceeded by no nearby space.
            '                # Singlequote (not isn't)
            (?=.{,2}\s)      # Proceeded by a nearby space.""",
        "’"),
    #Obviously mismatched close-quote
    R(next(c), r"(?<=\w)“(?=\.(?:\s|$))", "”"),
    R(next(c), r"(?<=\w[.?!]?)“(?=\s*\n)", "”"),

    R(next(c), r"(?<=\w)”(?=s)", r"’"),
    
    #Ambigious straight quote decided as 'close' by proceeding open quote.
    R(next(c), r"\"(?=[^”\"]+“)", "”"),
    #Ambigious close quote decided as 'open' by proceeding close quote.
    R(next(c), r"\"(?=[^“\"]+”)", "”"),
    #Ambigious straight quote decided as 'close' by proceeding open quote.
    R(next(c), r"'(?=[^’']+‘)", "‘"),
    #Ambigious straight quote decided as 'open' by proceeding close quote (complexity is mainly filtering out isn't types)
    R(next(c), r"'(?=[^‘']+’(?=.(?<!\w’\w)))", "‘"),
    R(next(c), r"(?<=\w)`(?=[^‘']+’(?=.(?<!\w’\w)))", " ‘"),


    # A colon possibly followed by by space/hyphens and a quote => emdash
    # newlines are preserved, hyphens and spaces eliminated.
    R(c(39), r'(”.\s+)\p{dash}+(\s*“)', r'\1\2'),
    R(c(40), r': ?(\n*)[ -]*(?<!:\n+)(?=[“‘])', r': \1'),
    R(next(c), r'(?<=[\w\.]) -[- ]*(?=[”’])', r':'),
    R(next(c), r'(?<=[\w\.])- [- ]*(?=[”’])', r':'),

    #Dash -> Colon
    R(next(c), r'\p{dash}(?:\s(?<=\n)(?=\s))?(?=\W*[“‘])', r':'),
    
    # Catchall colon+hyphen with no quote.
    R(next(c), r'(?<=\p{alpha}):\s?-[-\s]*', r'—'),
    R(next(c), r'(?<=\p{alpha}),\s?-[-\s]*', r'—'),
    R(next(c), r'--\s*', r'—'),
    R(next(c), r'(?<=\p{alpha}) -\s*(?=\p{alpha})', r'—'),
    R(next(c), r'— +(?!“)', r'—'),
    
    
    # Special case involving spaced hyphen between numbers
    R(next(c), r"(?=\d) -[- ]*(?=\d)", r"–"),
    # Any kind of dash between numbers.
    R(next(c), r"""(?x)# Verbose
        (?<=\d+)        # number
        (?<!\d+-\d+)    # date (negates match)
        \p{dash}\s?+ # (spaced) dash of some kind
        (?=.(?<!\d–\d)) # A good honest non-spaced endash negates previous
        (?!\d+-\d+)     # date (negates match)
        (?=\d+)         # number""", r"–"),
        
    # Emdash 
    R(next(c), r"""(?x)
        (?<=[[:alpha:]])    # An alphabetical character
        \p{dash}-*\ ?+   # A possibly spaced dash of some kind
        (?<!\S—(?=\w|\s+[“‘]))# Which is not a good honest emdash
        (?<!\w-(?=\w))      # Or a good honest hyphen
        (?=[[:alpha:]]|$)   # Followed by an alphabetical character or EOL
        """, r'—'),
    # Emdash2
    R(next(c), r"""(?x)
        ”             # A close quote (anchors pattern)
        (?:-- *|\ -+\ *) # Followed by an ascii emdash
        (?=\p{alpha}) # An an alphabetical character
        """, r"” —"),

    #Unspaced Open Puncuation
    R(c(60), r"(?<![\s‘/(/[]|^)“", r" “"),
    R(next(c), r"(?<![\s“/(/[]|^)‘", r" ‘"),
    
    #Unspaced Close Puncuation
    R(next(c), r"”(?!\p{Term}|\s|’|ti)", r"” "),
    #There's not much we can do with the single quote

    #Pre-spaced comma/period
    R(next(c), r" (\p{Term})", r"\1"),
    
    #Unspaced comma
    R(next(c), r",(?=\p{alpha})", r", "),
    R(next(c), r"\?(?=\p{alpha})", r"? "),
    R(next(c), r"!(?=\p{alpha})", r"! "),

    #Unspaced period - More care is required here. To be conservative
    #only replace 'Foobar.Baz' and some other dodgies)
    R(next(c), r"\.(?=.(?<=\p{Lower}\.[\p{Upper}\(\[{]))", r". "),
    
    #Fix mis-matched brackets (permit smileys out of kindness of heart :-])
    #R(next(c), r"\((?!-?[:;])([^(]*)\](?<![:;]-?])", r"(\1)"),
    #R(next(c), r"\[(?!-?[:;])([^(]*)\)(?<![:;]-?\))", r"(\1)"),
    R(next(c), r"\((\w+)\]", r"(\1)"),
    R(next(c), r"\[(\w+)\)", r"(\1)"),
    

    # Add space to front of [({, end of ])}
    R(next(c), r"(?<=\p{alpha})(\p{gc=Open_Punctuation})(?!\p{alpha}\p{gc=Close_Punctuation})", r" \1"),
    R(next(c), r"(\p{gc=Close_Punctuation})(?=\p{alpha})", r"\1 "),

    # Fix capitalization
    R(next(c), r"(?<=\p{Lower}(?<!"+abbrs+"))(\.\s+)(\p{Lower})", lambda m: m[1] + m[2].upper()),
    R(next(c), r"(?<=\p{Lower})(\?\s+)(\p{Lower})", lambda m: m[1] + m[2].upper()),
    R(next(c), r"(?<=\p{Lower})(\!\s+)(\p{Lower})", lambda m: m[1] + m[2].upper()),
    ]

class InputError(Exception):
    pass

class Emdashar:
    """Responsible for emdashing an input element"""
    _html = ('html', 'htm')
    _xml = ('xhtml', 'xml')
    _txt = ('txt',)
    text = None
    element = None
    preamble = ''
    postable = ''
    def __init__(self, logger = None):
        if logger is None:
            logger = textwrangle.SortedLogger()
        self.logger = logger
        
    def fromfile(self, filename, filetype = None):
        """Parse a file. Autodetect type from filename.

        filetype - ('html', 'htm', 'xhtml', 'xml', 'txt')

        """

        self.text = None
        self.element = None
        
        if filetype is None:
            try:
                filetype = regex.match(r'.*\.(.+)', filename)[1].lower()
            except TypeError:
                raise InputError('Filename <{}> cannot be recognized'.format(filename))
        else:
            filetype = filetype.lower()
            if filetype not in itertools.chain(self._html, self._xml, self._txt):
                emsg = 'Invalid filetype <{}>'.format(filetype)
                raise InputError(emsg)
        #Using python to read the file, for utf8 happiness.
        with open(filename) as f:
            m = regex.match(r'(.*)(<body.*</body>)(.*)', f.read(), flags=regex.DOTALL)
            filestring = m[2]
            self.preamble = m[1]
            self.postamble = m[3]
        if filetype in self._html:
            self.element = lxml.html.fromstring(filestring)
        elif filetype in self._xml:
            self.element = lxml.etree.fromstring(filestring)
        elif filetype in self._txt:
            self.text = filestring
        else:
            emsg = "Endashar doesn't know how to open <{}>.".format(filename)
            raise InputError(emsg)
    
        self.filetype = filetype
        return self
    
    def tofile(self, filename):
        if self.filetype in self._txt:
            with open(filename, 'w') as f:
                f.write(self.text)
        elif self.filetype in self._html:
            with open(filename, 'w') as f:
                f.write(self.preamble + lxml.html.tostring(self.element, encoding = 'utf8').decode() + self.postamble)
        elif self.filetype in self._xml:
            with open(filename, 'wb') as f:
                f.write(self.preamble + lxml.etree.tostring(self.element, encoding = 'utf8') + self.postamble)
        else:
            raise InputError('filetype not recognized')
        return

    def text_iter(self, ignore_tags = None, permit_tags = None):
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
        
        for e in self.element.iter(self.element.emdashar_texttag):
            parent = e.getparent()
            if permit_tags is None or parent.tag in permit_tags:
                if ignore_tags is None or parent.tag not in ignore_tags:
                    yield e
        
    def emdash(self, element = None, ignore_tags = None, permit_tags = None):
        if element is not None:
            self.element = element
        
        if self.text is not None:
            self.text = list(self._emdash( [self.text], [0] ))[0]
        elif self.element is not None:
            self._prepareelement(self.element)
            texttag = self.element.emdashar_texttag
            textiter, sourcelineiter = zip(*((e.text, e.sourceline)
                                        for e in list(self.text_iter(ignore_tags=ignore_tags))))
            resultiter = self._emdash(textiter, sourcelineiter)
            for node, text in zip(self.text_iter(ignore_tags=ignore_tags), resultiter):
                node.text = text
            self._finalizeelement(self.element)
            if element is not None:
                return element
            else:
                return
            
        raise InputError('No input')
    
    def _prepareelement(self, element):
        """Wrap the text inside element in temporary 'text' nodes"""
        texttag = 'text'
        for i in range(1, 1000):
            #See if the text tag name is already in use.
            try:
                next(element.iter(texttag))
                # It is, so create a random text tag name.
                import random
                texttag = 'text' + str(hex(random.randint(1, 16777215)))[:2]
            except StopIteration:
                #No element found.
                break
        else:
            #This should never happen. Because who would create an XML document
            #with thousands of variants of 'text' + 'hexcode'
            raise Exception("What the flaming hell?!")
        element.emdashar_texttag = texttag
        wraptext(element, texttag)

    def _finalizeelement(self, element):
        """Unwrap the elements, restoring the xml/html to it's original form"""
        texttag = element.emdashar_texttag
        unwraptext(element, texttag)

    def _emdash(self, strings, sourcelines=None):
        """Process all strings in iter"""

        #Build a MSS from the text content of the element (in-order)

        mss = MutableSuperString(strings, sourcelines=sourcelines, logger=self.logger)
        for rule in rules:
            #self.logger.print(" === Applying rule {:<2} === ".format(rule.label))
            self.logger.rule = rule
            mss.sub(rule.pattern, rule.repl)

        return mss

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description = "Fixes many common puncuation errors, typos and mistakes.", epilog = "Designed primarly to convert ascii->unicode, and correct typos. Has only a limited ability to work with already well-formed text (i.e. it is not a puncuation checker per-se, altough it can be used as such)")
    
    parser.add_argument("infiles", metavar = "infile", help = "the html, xml or txt files to operate on", nargs = "+");

    parser.add_argument('--fullpath', action="store_true", help='Preserve full path names')
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-o", "--out", default='./emdashed', help="The output folder (default=./emdashed)")
    
    group.add_argument("-m", '--modify', action="store_true", help = "Modify source-files in-place")
    
    group.add_argument("-n", '--no-act', action="store_true", help = "Make no changes, only print the changes which would be made.")

    parser.add_argument('-v', '-verbosity', dest= 'verbosity', default = 1, type = int, help = "Display changes.")
    parser.add_argument('-q', '--quiet', dest = 'verbosity', action = 'store_const', const = 0, help = "Produce no feedback")

    return parser.parse_args()

def getcommonprefix(input):
    "Takes an iterable of indexables (i.e. strings), returns a common prefix"
    inputiter = iter(input)
    commonprefix = list(next(inputiter))
    for item in inputiter:
        commonprefix[len(item):] = []
        for i, char in enumerate(commonprefix):
            if char != item[i]:
                commonprefix[i:] = []
    if len(commonprefix) == 0:
        return None
    try:
        return type(commonprefix[0])().join(commonprefix)
    except AttributeError:
        return commonprefix

def run():
    args = parse_args()
    commonpath = getcommonprefix(args.infiles)
    try:
        commonpath = regex.match(r'.*/', commonpath)[0]
    except TypeError:
        commonpath = ''
    print(args)
    logger = None
    if args.verbosity == 0:
        logger = textwrangle.SilentLogger()
    else:
        logger = textwrangle.SortedLogger(ignore=[1,2])
    dashar = Emdashar(logger=logger)
    totalcount = 0
    filecount = 0
    for file in args.infiles:
        dashar.fromfile(file)
        dashar.emdash(ignore_tags = 'a, pre, code')
        if args.no_act:
            continue
        elif args.modify:
            newfile = file
            dashar.tofile(newfile)
        elif args.out:
            # Trim the current suffix
            if args.fullpath:
                newfile = os.path.join(args.out, file)
            else:
                newfile = os.path.join(args.out, file[len(commonpath):])
            try:
                os.makedirs(os.path.split(newfile)[0])
            except OSError as err:
                if err.errno != os.errno.EEXIST:
                    raise
            dashar.tofile(newfile)
        logger.print('{} emdashed! {} bad punctuations corrected!'.format(newfile, logger.count))
        filecount += 1
        totalcount += logger.count        
        logger.count = 0
    if args.no_act == False:
        logger.print('{} files emdashed! {} bad puncuations corrected!'.format(
            filecount, totalcount))



def test_sample():
    """Runs a test case on the emdashar program"""
    
    sample = """<div>This is a 'document' which contains <i>many!!</i>!! examples of "<b>BAD"</b> puncuation , such as:"this starts a sentence,but doesn't finish,who needs spaces anyway“.\nSome-times we hyphenate words for no reason!! blah blah blah...\n blah... blah ...blah. You should know that ''some people'' don't know how to use ``quotes'' properly..<span>[other) people do [but] they will not, there is also some <b>(-:</b><i>evil stuff</i><b>;-]</b> which is okay but EVIL!.</span>\nOn"sum we Don't really know what we are talking about". That is what they said. Dejected. No-one delighted in anything<b>.</b>\n » "" «- wat the hell are these???!\n<b>look. we. are. many. examples. of. bad. things. which. should. die. quickly. quickly.<br>\n please.!</div>"""
    element = lxml.html.fromstring(sample)
    logger = SortedLogger()
    dashar = Emdashar(logger=logger)
    dashar.emdash(element)
    print(lxml.html.tostring(element, encoding = 'utf8').decode())

    dashar = Emdashar(logger=SortedLogger())
    dashar.fromfile('./nandar/testing/flatland.html')
    dashar.emdash()

def perftest():
    import time
    dataset = open('bigtext.txt').read()
    times = []
    for rule in rules:
        start = time.process_time()
        baz = regex.findall(rule.pattern, dataset)
        times.append( (rule.label, time.process_time() - start))
    total = sum(t[1] for t in times)
    for t in times:
        print('{}: {}%, {}'.format(t[0], int(100 * t[1] / total),
            t[1]))

def test(string):
    for rule in rules:
        print('{}: {}'.format(rule.label, regex.findall(rule.pattern, string)))

run()