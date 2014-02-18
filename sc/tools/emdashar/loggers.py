
def pad(seq, length, padding):
    diff = length - len(seq)
    if diff <= 0:
        return seq
    ret = list(seq)
    ret.extend(padding for i in range(0, diff))
    return tuple(ret)

class DefaultLogger:
    rule = None
    mss = None
    count = 0
    ignore = []
    file=None
    def __init__(self):
        self.file = sys.stdout
        
        pass
    def register_mss(self, mss):
        self.mss = mss
    def __call__(self, match, orig, repl):
        pass
    def flush(self):
        pass
    def print(self, message):
        self.flush()
        print(message, file=self.file)

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
            print(self.fmt1.format(*row1), file=self.file)
            print(self.fmt2.format(*row2), file=self.file)
    def flush(self):
        while len(self.buffer) > 0:
            diff = self.columns - len(self.buffer)
            row1, row2 = zip(*pad(self.buffer[:self.columns], diff, ('', '') ))
            row1 = pad(row1, self.columns, '')
            row2 = pad(row2, self.columns, '')
            self.buffer[:self.columns] = []
            print(self.fmt1.format(*row1), file=self.file)
            print(self.fmt2.format(*row2), file=self.file)

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
            print(self.fmt.format(lineno=lineno, orig=orig, repl=repl, 
                                    rule=rule), file=self.file)
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
