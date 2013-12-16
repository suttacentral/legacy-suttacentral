try:
    import regex
except ImportError:
    import re as regex
    
from itertools import chain
from time import time

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
    >>> pieces[::2] = mss.reconstruct() # Set odd pieces to reconstructions
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
    def __init__(self, strings):
        self.pieces = tuple(strings)
        self._lengths = [len(s) for s in self.pieces]
        self._update()
        self.string = "".join(self.pieces)
        self._dirty = False
    
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
        diff = len(repl) - len(orig)
        if diff < 0:
            self._erase(m.span()[0], -diff)
            self._dirty = True
        elif diff > 0:
            self._insert(m.span()[0], diff)
            self._dirty = True
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

        sub returns the mss object, allowing subs to be chained together.
        """
        # The callback needs these variables.
        self._repl = repl
        self._hint = hint
        self._fast = fast
        self.string = regex.sub(pattern, self._callback, self.string)
        if self._dirty:
            self._update()
        return self

if __name__ == '__main__':
    import cProfile
    from time import time
    MSS = MutableSuperString
    try:
        sampletext = ["Hello ", "World"]
        j = MSS(sampletext)
        j.sub(' ', ' Cruel ')
        print(j.reconstruct())
        print("Test One: Insertion: Passes.")
    except:
        print("Test One: Insertion: Fails.")
        raise
    
    sampletext = """Once upon a time there was a farmer. He had a sheep. The name of his sheep was Harry. The farmer's name was Joe. Joe was an Australian. And you thought that was going to be a joke about Kiwis!.
Anyway, Joe loved Harry very much...\n"""
    try:
        pieces = regex.findall(r'[^.]+\.+', sampletext)
        j = MSS(pieces)
        j.sub('ee', 'o')
        j.sub('farmer', "merchant's son")
        j.sub('Harry', "Harrisons")
        j.sub('Australian', 'Austrian')
        j.sub(' And you.*Kiwis!.', '')
        j.sub('Joe', 'Arnold')
        j.sub('loved', 'hated')
        print(j.reconstruct())
        print("Test Two: Advanced: Passes.")
    except:
        print("Test Two: Advanced: Fails.")
        raise
    try:
        print("Test Three: Speed Test!")
        pieces = tuple(sampletext for i in range(0, 10000))
        string = "".join(pieces)
        start = time()
        #regstr = regex.sub(r'\b\w{7}\B', lambda m: 'SeVeNtY', string)
        regstr = regex.sub(r'\.', lambda m: '-', string)
        regtime = time() - start
        
        j = MSS(pieces)
        start = time()
        #cProfile.run(r"j.sub(r'\b\w{7}\B', 'SeVeNtY')", 'profile')
        j.sub(r'\.', '-')
        msstime = time() - start
        newstr = "".join(j.reconstruct())
        
        print("    Results Match: " + ('Pass' if newstr == regstr else 'Fail'))
        print("    Complete in: {}s, {}% as fast as regex.sub".format(
            msstime, int(100 * regtime / msstime)))
    except:
        print("Test Three: Fails")
        raise