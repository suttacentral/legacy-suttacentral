import lxml.html

def wrap_text(tag, tagname = 'text', tail_only = False):
    """Wrap text in psuedo text nodes

    These nodes will be named 'tagname', if tail_only is 'False' then both
    text and tail text will be converted into text nodes. If set to 'True'
    then only tail text will be converted into text nodes.
    The point of 'tail_only' is to permit inorder iteration of nodes
    containing text, the point of 'all' is for further consistency, not
    only may every piece of text be manipulated inorder, the containing
    element can be discovered directly using 'getparent'."""
    tags = list(tag.iter())
    for i in range(0,len(tags)):
        e = tags[i]
        if not isinstance(e, lxml.html.HtmlElement):
             continue
        if e.tail:
            try:
                sourceline = tags[i + 1].sourceline
            except IndexError:
                sourceline = e.sourceline
            text = e.tail
            e.tail = None
            a = e.makeelement(tagname)
            a.text = text
            a.sourceline = sourceline
            e.addnext(a)
        if not tail_only and e.text:
            text = e.text
            e.text = None
            a = e.makeelement(tagname)
            a.text = text
            e.insert(0, a)

def unwrap_text(tag, tagname = 'text'):
    for e in list(tag.iter(tagname)):
        e.drop_tag()