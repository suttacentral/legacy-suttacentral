import sys
sys.path.append('..')
import env

import lhtmlx
from lhtmlx.builder import *

import regex, itertools, logging

logger = logging.getLogger(__name__)

def getnthancestor(element, n, sentinel='body'):
    "Get the nth ancestor, or the ancestor beneath the sentinel"
    if n == 0:
        return element
    last_e = e
    for j, e in enumerate(element.iterancestors()):
        if e.tag == sentinel:
            return last_e
        if j == n:
            return e
        last_e = e

def filterdescendents(elements):
    """Returns a new list of elements, none of which is a descendent of another
    
    >>> dom = BODY(DIV(DIV(P, P, P)), DIV(EM))
    >>> [str(e) for e in dom.select('div')]
    ['<div><div><p>...</div>', '<div><p>...</div>', '<div><em></em></div>']
    >>> [str(e) for e in filterdescendents(dom.select('div'))]
    ['<div><p></p><p></p><p></p></div>', '<div><em></em></div>']
    
    """
    ancestors = []
    for e in elements:
        ancestors.append(set(e.iterancestors()))
    for i, e in enumerate(elements):
        for j, e2 in enumerate(elements):
            if i == j or e2 is None:
                continue
            if e in ancestors[j]:
                elements[i] = None
                break
    return [e for e in elements if e is not None]



def xhtml_to_html(dom):
    return lhtmlx._html.xhtml_to_html(dom)

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)