import regex
import env
import sc

chars = set()

try:
    with open('usedchars.txt') as f:
        chars = f.read()
except FileNotFoundError as e:
    for file in sc.text_dir.glob('**/*.html'):
        with file.open('r') as f:
            chars.update(f.read())
    chars = ''.join(sorted(chars))
    with open('usedchars.txt', 'w') as f:
        f.write(chars)

all_chars = ''.join(chr(i) for i in range(0, ord('\uffff')))


letter_points = [ord(c) for c in regex.findall(r'\p{L}', all_chars)]

used_points = [ord(c) for c in regex.findall(r'\p{L}', chars)]

def get_ranges(codepoints):
    ranges = []
    last_i = -1
    for i in codepoints:
        if i != last_i + 1:
            if ranges:
                ranges[-1].append(chr(last_i))
            ranges.append([chr(i)])
        last_i = i
    if i:
        ranges[-1].append(chr(i))
    return {tuple(t) for t in ranges}

def get_used_ranges(codepoints, base_ranges):
    base_ranges
    mapping = {}
    for t in base_ranges:
        try:
            for i in range(ord(t[0]), ord(t[1])):
                mapping[i] = t
        except:
            print(t)
            raise
    seen = set()
    for c in codepoints:
        if c in mapping:
            seen.add(mapping[c])
    return seen
        
    

all_ranges = get_ranges(letter_points)

used_ranges = get_used_ranges(used_points, all_ranges)
