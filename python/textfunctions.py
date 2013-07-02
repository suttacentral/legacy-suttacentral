import regex, unicodedata


def simplify(string, lang='pi'):
    if lang == 'pi':
        rules = (
            (r'\P{alpha}', r''), #Non-alphabetical characters
            (r'nny', 'nn'), # nny (ññ) -> n
            (r'(.)(?=\1)', r''), #Remove duplicates
            (r'(?<=[kgcjtdbp])h', r''), # Remove aspiration
            (r'[ṁṃṅ](?=[gk])', r'n'), # 'n' before a 'g' or 'k'
            (r'by', 'vy'), # vy always, never by
            
        )
        
        out = string.casefold()
        for rule in rules:
            out = regex.sub(rule[0], rule[1], out)
        out = unicodedata.normalize('NFD', out)
        out = regex.sub(r'\p{dia}', '', out)
        out = regex.sub(r'm\b', '', out) # Remove trailing m
        return out
    return ''