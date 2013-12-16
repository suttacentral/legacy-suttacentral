import regex, lxml.html
from itertools import chain
from time import time

class WrangleError(Exception):
    pass

def wraptext(tag, texttag = None, tail_only=False, force=False):
    """Wrap text in psuedo text nodes to facilitate text-wrangling

    Normally the presence of two different kinds of text - 'text' and
    'tail' makes certain kinds of operations harder than they need to be.
    This function simply wraps

    >>> from lxml.html import fromstring, tostring
    >>> e = fromstring("<p><b>It's <i>just a</i> fleshwound</b>.</p>")
    >>> tostring(e)
    b"<p><b>It's <i>just a</i> fleshwound</b>.</p>"

    >>> wraptext(e) # Returns the text tag name.
    'text'
    
    >>> tostring(e)
    b"<p><b><text>It's </text><i><text>just a</text></i><text> fleshwound</text></b><text>.</text></p>"

    >>> for t in e.iter('text'): t.text = t.text.upper()
    >>> unwraptext(e)
    >>> tostring(e)
    b"<p><b>IT'S <i>JUST A</i> FLESHWOUND</b>.</p>"
    
    """

    #This will usually be a mistake, so raise an exception by default.
    if hasattr(tag, 'wraptexttag'):
        if force == False:
            raise WrangleError("Text already wrapped.")
        else:
            texttag = tag.wraptexttag
    else:
        if texttag is None:
            texttag = 'text'
            for i in range(1, 1000):
                #See if the text tag name is already in use.
                try:
                    next(tag.iter(texttag))
                    # It is, so create a random text tag name.
                    import random.randint
                    texttag = 'text' + str(hex(random.randint(1, 16777215)))[:2]
                except StopIteration:
                    #Not found in tree. Use as texttag.
                    break
    tags = list(tag.iter())
    for i in range(0,len(tags)):
        e = tags[i]
        if not isinstance(e, lxml.html.HtmlElement):
             continue
        if e.tag == texttag:
            continue
        if e.tail:
            try:
                sourceline = tags[i + 1].sourceline
            except IndexError:
                sourceline = e.sourceline
            text = e.tail
            e.tail = None
            a = e.makeelement(texttag)
            a.text = text
            a.sourceline = sourceline
            e.addnext(a)
        if not tail_only and e.text:
            text = e.text
            e.text = None
            a = e.makeelement(texttag)
            a.text = text
            e.insert(0, a)
    tag.wraptexttag = texttag
    return texttag

def unwraptext(tag, texttag = None):
    """Unwrap text previously wrapped by wraptext
    
    >>> from lxml.html import fromstring, tostring
    >>> e = fromstring("<b><foo>I'm text!</foo><br><foo>Me too!</foo></b>")
    >>> unwraptext(e, texttag='foo') # An arbitary tag name can be used.
    >>> tostring(e)
    b"<b>I'm text!<br>Me too!</b>"

    """
    
    if texttag is None:
        try:
            texttag = tag.wraptexttag
            del tag.wraptexttag
        except AttributeError:
            raise WrangleError("Text not wrapped or texttag not given")
    for e in list(tag.iter(texttag)):
        e.drop_tag()

class MutableSuperString:
    """Creates a mutable psuedo-string out of an iterable of strings.

    Imagine a string like this:
    >>> hello = 'Hello <big>C</big>ruel World'
    
    We can not perform a normal regex substitution because of the XML tags:
    >>> regex.sub('Cruel', 'Hello', hello)
    'Hello <big>C</big>ruel World'

    But this is possible with MutableSuperString (to the rescue!)
    >>> pieces = regex.split(r'(<[^>]+>)', hello)
    >>> pieces
    ['Hello ', '<big>', 'C', '</big>', 'ruel World']
    >>> mss = MutableSuperString(pieces[::2]) # Get odd pieces only
    >>> mss.sub('Cruel', 'Happy')
    >>> pieces[::2] = iter(mss) # Set odd pieces to reconstructions
    >>> "".join(pieces)
    'Hello <big>H</big>appy World'

    >>> mss.sub('Happy', '')
    >>> pieces[::2] = iter(mss)
    >>> "".join(pieces)
    'Hello <big></big> World'

    Using this class, it is possible to perform regular expression
    substitutions which span string-boundaries, with reasonably small
    additional overhead. At worst, MSS.sub might run at about 25% of the
    speed of 'regex.sub' on the equivilant monolithic string.

    MSS will always produce output which will be textually identical to the results of running 'regex.sub' on the equivilant monolithic string.
    But of course outside of certain strict constraints it cannot guarantee that text will remain in logically 'proper' tags despite its best
    efforts to track what sub-string changes properly belong to.

    MSS can however take 'hints' on how to treat replacements, which are:
    'smart' is the default option and usually best.
    'head' means to stretch or shrink the first element the string spans.
    'tail' means to stretch or shrink the last element the string spans.

    Beyond this, one must simply be constrained in what one matches.
    Inserting/replacing/erasing the shortest possible matches will always
    improve accuracy. Lookahead/behind assertions are very helpful since
    they reduce the length of the actual match, and thus reduce the number
    of things that can go wrong when making the replacement.
    Not so good:
    >>> mss.sub(r'(\d)-(\d)', r'\1–\2')

    Better: Match only what needs to be replaced, using assertions to
    make the match precise (This will also be much faster)
    >>> mss.sub(r'(?<=\d)-(?=\d)', r'–')
    """    
    def __init__(self, strings, sourcelines = None, logger = None):
        """'logger' may be set to a function, which should receive a match
        object and the calculated replacement string."""
        self.pieces = tuple(strings)
        if sourcelines is not None:
            sourcelines = tuple(sourcelines)
        self._lengths = [len(s) for s in self.pieces]
        self._update()
        self.string = "".join(self.pieces)
        self._dirty = False
        if logger is not None:
            logger.register_mss(self)
        self.logger = logger
    
    def _update(self):
        #Tuple to emphasize that mapping is immutable. '_lengths' is the
        #mutable attribute which should be modified to reflect changes.
        self.mapping = tuple(chain(*((i,) * l for i, l in enumerate(self._lengths))))
    
    def __repr__(self):
        string = self.string.replace('\n', ' ')
        mapping = "".join(str(s) for s in self.mapping if s < 10).replace('\n', ' ')
        string = string[:len(mapping)]
        width = 79
        rep = [('<MutableSuperString:\n')]

        while len(mapping) > 0:
            rep.append(string[:width] + '\n')
            string = string[width:]
            if len(self._lengths) > 1:
                rep.append(mapping[:width] + '\n')
                mapping = mapping[width:]

        rep.append('>' + '\n')
        return "".join(rep)
    
    def reconstruct(self):
        """Return a new list of strings, corresponding to the original strings.

        These strings will reflect the changes performed by 'sub'."""
        return list(self.__iter__())

    def __iter__(self):
        "Iterate over replacement strings, in the original order"
        if len(self._lengths) == 1:
            yield self.string
        else:
            string = self.string
            sofar = 0
            for length in self._lengths:
                yield string[sofar:sofar + length]
                sofar += length
        while True:
            raise StopIteration
        
    def _erase(self, where, length = 1):
        "Records the deletion of one or more characters starting at where"
        # This might span multiple strings, carry erasors to the next length.
        if 'smart' in self._hint:
            for i in range(where, where + length):
                self._lengths[self.mapping[i]] -= 1
            return
        elif 'head' in self._hint:
            while True:
                target = self.mapping[where]
                self._lengths[target] -= length
                if self._lengths[target] >= 0:
                    return
                where += 1
                length = -self._lengths[target]
                self._lengths[target] = 0
        elif 'tail' in self._hint:
            while True:
                target = self.mapping[where + length]
                self._lengths[target] -= length
                if self._lengths[target] >= 0:
                    return
                where -= 1
                length = -self._lengths[target]
                self._lengths[target] = 0
        error = "Invalid value '{}' passed as hint.".format(self._hint)
        raise ValueError(error)
    
    def _insert(self, where, length = 1):
        if 'smart' in self._hint or 'head' in self._hint:
            self._lengths[self.mapping[where]] += length
        elif 'tail' in self._hint:
            self._lengths[self.mapping[where + length]] += length
        else:
            error = "Invalid value '{}' passed as hint.".format(self._hint)
            raise ValueError(error)
    
    def _callback(self, m, _cache = {}):
        orig = m.group()
        repl = self._repl
        if type(repl) is str:
            if self._format == False:
                if '\\' in repl:
                    if self._fast:
                        key = (m.groups(), self._repl)
                        try:
                            repl = _cache[key]
                        except KeyError:
                            if type(self._repl) is str:
                                repl = m.expand(self._repl)
                            else:
                                repl = self._repl(m)
                            _cache[key] = repl
                    else:
                        if type(self._repl) is str:
                            repl = m.expand(self._repl)
                        else:
                            repl = self._repl(m)
            else:
                if '{' in repl:
                    repl = m.expandf(repl)
        else:
            repl = repl(m)
        diff = len(repl) - len(orig)
        if len(self._lengths) > 1:
            if diff < 0:
                self._erase(m.span()[0], -diff)
                self._dirty = True
            elif diff > 0:
                self._insert(m.span()[0], diff)
                self._dirty = True
        if self.logger is not None:
            self.logger(m, orig, repl)
        return repl
    
    def sub(self, pattern, repl, hint = 'smart', fast = True):
        r"""Perform a regex substitution.

        'pattern' and 'repl' are the same as for re.sub/regex.sub (i.e.
        pattern can be a regex pattern or a compiled regex. Repl may be a string or a function which returns a string)
        'hint' may be 'smart', 'head', or 'tail' and indicates which string
        to shrink or stretch to accomodate a string-spanning substitution.
        The default 'smart' is usually best.
        
        If 'fast' is set to True, a simple optimization is performed which can result in 10x speed gains for replacements where the same
        match always maps to the same replacement. This is nearly always the case, an example when this invariant doesn't hold true is when
        a callback returns a random word or other dynamic content which
        doesn't relate directly to the input. In these cases, fast = False
        should be used. The fast flag is only required because of a weakness in the regex module.
        """
        # The callback needs these variables.
        self._repl = repl
        self._hint = hint
        self._fast = fast
        self._format = False
        self.string = regex.sub(pattern, self._callback, self.string)
        if self._dirty:
            self._update()

def pad(seq, length, padding):
    diff = length - len(seq)
    if diff <= 0:
        return seq
    ret = list(seq)
    ret.extend(padding for i in range(0, diff))
    return tuple(ret)

class Rule:
    """Contains a Regex pattern => replacement rule"""
    def __init__(self, label, pattern, repl, flags = None):
        self.label = label
        self.pattern = regex.compile(pattern)
        self.repl = repl
        self.flags = list(flags) if flags is not None else []
    def __lt__(self, other):
        return self.label < other.label
    def __eq__(self, other):
        return self.label == other.label


class DefaultLogger:
    rule = None
    mss = None
    count = 0
    ignore = []
    def __init__(self):
        pass
    def register_mss(self, mss):
        self.mss = mss
    def __call__(self, match, orig, repl):
        pass
    def flush(self):
        pass
    def print(self, message):
        self.flush()
        print(message)

class SilentLogger(DefaultLogger):
    def print(self, message):
        pass

class ColumnLogger(DefaultLogger):
    def __init__(self, columns = 4):
        self.columns = columns
        self.width = int(80 / columns - 3)
        self.buffer = [] #Could use a deque, but it doesn't grow long
        self.fmt1 = "|".join((' {:<' + str(self.width) + '} ',) * self.columns)
        self.fmt2 = self.fmt1 + '\n'
        
    def __call__(self, match, orig, repl):
        if orig == repl:
            return
        self.count += 1
        middle = sum(match.span()) / 2
        start = int(middle - self.width / 2)
        pre = match.string[start: match.start()]
        post = match.string[match.end():match.end() + self.width]
        orig = match.string[start:start + self.width].replace('\n', '↵')
        repl = (pre + repl + post)[:self.width].replace('\n', '↵')
        self.buffer.append( (orig, repl) )
        while len(self.buffer) >= self.columns:
            row1, row2 = zip(*self.buffer[:self.columns])
            self.buffer[:self.columns] = []
            print(self.fmt1.format(*row1))
            print(self.fmt2.format(*row2))
    def flush(self):
        while len(self.buffer) > 0:
            diff = self.columns - len(self.buffer)
            row1, row2 = zip(*pad(self.buffer[:self.columns], diff, ('', '') ))
            row1 = pad(row1, self.columns, '')
            row2 = pad(row2, self.columns, '')
            self.buffer[:self.columns] = []
            print(self.fmt1.format(*row1))
            print(self.fmt2.format(*row2))

class SortedLogger(DefaultLogger):
    """A logger which sorts results by line number.

    Because it sorts results before printing them, it only prints when
    print or flush is called.

    It is not always capable of giving precise line numbers, in particular
    if substitutions add or remove newlines it may descyncronize.

    """
    def __init__(self, mss = None, ignore = None):
        self.width = 30
        self.overlap = 3
        self.fmt = "{lineno:<5}{orig:<30} -> {repl:<30} ({rule.label})"
        self.mss = mss
        self.buffer = []
        if ignore is not None:
            self.ignore = ignore
        
        
    def __call__(self, match, orig, repl):
        if self.rule.label in self.ignore:
            return
        if orig == repl:
            return
        self.count += 1
        start = match.start()
        end = match.end()
        width = self.width
        overlap = self.overlap

        #Generate original snippet
        orig = match.string[end + overlap - width:end + overlap]
        
        #Generate replacement snippet
        pre = match.string[start - overlap: start]
        post = match.string[end: end + width - len(repl) - overlap]
        repl = pre + repl + post

        orig = orig.replace('\n', '↵')
        repl = repl.replace('\n', '↵')
        
        self.buffer.append( (self.calculateLineno(match), self.rule, orig, repl ) )
    def calculateLineno(self, match):
        return match.string.count('\n', 0, match.start())
    def flush(self):
        #When sorting, compare only the line number and rule number.
        self.buffer.sort(key=lambda a: (a[0], a[1]))
        for lineno, rule, orig, repl in self.buffer:
            print(self.fmt.format(lineno=lineno, orig=orig, repl=repl, rule=rule))
        self.buffer = []

class NaiveLogger(SortedLogger):
    def __init__(self, mss = None):
        self.width = 30
        self.overlap = 3
        self.fmt = "{lineno:<5}{orig:<30} -> {repl:<30} ({rule.label})"
        self.mss = mss
        self.buffer = []

    def __call__(self, match, orig, repl):
        self.count += 1

        if len(orig) > self.width:
            orig = orig[:self.width/2 - 2] + ' … ' + orig[:-self.width/2 + 1]
        if len(repl) > self.width:
            repl = repl[:self.width/2 - 2] + ' … ' + repl[:-self.width/2 + 1]

        orig = orig.replace('\n', '↵')
        repl = repl.replace('\n', '↵')

        self.buffer.append( (self.calculateLineno(match), self.rule, orig, repl ) )
    
class UniqueCounter:
    """A resettable counter class that guarantees every returned value is unqiue

    This is enforced simply by requiring that every value is larger than
    the previous value. Another way of putting this, is the counter may be
    advanced, but cannot ever be rewound.

    >>> counter = UniqueCounter(0)
    >>> next(counter); next(counter)
    1
    2

    >>> counter(10); next(counter)
    10
    11

    >>> counter.value
    11

    >>> counter(0)
    Traceback (most recent call last):
    ValueError: UniqueCounter may only be advanced, not rewound

    >>> counter()
    Traceback (most recent call last):
    ValueError: To increment counter, use next(counter)

    """
    
    def __init__(self, value = 0, increment = 1):
        self.value = value
        self.increment = increment
    def __call__(self, value = None):
        if value is None:
            raise ValueError('To increment counter, use next(counter)')
        if value < self.value:
            raise ValueError('UniqueCounter may only be advanced, not rewound')
        self.value = value
        return value
    def __next__(self):
        self.value += self.increment
        return self.value
    
        