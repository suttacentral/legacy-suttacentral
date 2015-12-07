import regex


word_rex = regex.compile(r'\p{alpha}+')

def process_text_sub(text, sub_fn):
    if not text:
        return text
    return word_rex.sub(sub_fn, text)    

def process_text_nosub(text):
    if not text:
        return text
    words = word_rex.findall(text)
    for word in words:
        if is_spelled_correctly(word):
            continue
        else:
            unrecognized_words[word] += 1

def process_node(node, process_fn=process_text_nosub):
    if node.get('id') == 'metaarea':
        return
    node.text = process_fn(node.text)
    for child in node:
        process_node(child, process_fn)
    node.tail = process_fn(node.tail)
