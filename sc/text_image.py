import regex
from collections import namedtuple

import sc
from sc.views import ViewBase
from sc.util import Timer


import pathlib

text_image_index = {}

TextPageImage = namedtuple('TextPageImage', ['ed', 'vol', 'page'])
# NamedTuple meaning it compares equal to a simple tuple (ed,vol,page)

def make_text_image_index():

    files = [f for 
             f in sc.text_image_source_dir.glob('**/*') 
             if f.suffix in {'.png', '.jpg'}]
    files.sort(key=lambda f: sc.util.numericsortkey(str(f)))
    
    out = {}
    prev = None
    for file in files:
        m = regex.match(r'(?<ed>\w+)-(?<book_acro>\w+)-vol\.(?<book_num>\d+)-pg\.(?<page>\d+)', file.stem)
        if m:
            ed = m['ed']
            vol = m['book_acro'] + m['book_num'].lstrip('0')
            page = m['page'].lstrip('0')
            tpi = TextPageImage(ed, vol, page)
            out[tpi] = {'file' : file.absolute(),
                        'url': '{}-{}-{}{}'.format(ed,
                                                   vol,
                                                   page,
                                                   file.suffix)}
            if prev:
                if prev.vol == tpi.vol:
                    out[prev]['next'] = tpi
                    out[tpi]['prev'] = prev
            prev = tpi
            
    return out


# The index key is a TextPageImage, value is a Path
index = make_text_image_index()

def update_symlinks(n):
    """ Symlinks are used mainly for the ease of serving with Nginx """
    if n > 0: return
    symlink_dir = sc.text_image_symlink_dir.absolute()
    for tpi, info in sorted(index.items(), key=lambda t: t[0]):
        symlink = symlink_dir / info['url']
        if symlink.is_symlink():
            if symlink.resolve() == info['file']:
                continue
            else:
                symlink.unlink()
        if not symlink.parent.exists():
            symlink.parent.mkdir(parents=True)
        symlink.symlink_to(info['file'])
    

def get(sutta_uid, volpage_id):
    uid_m = regex.match(r'(?<vol>[a-z]+)', sutta_uid)
    vp_m = regex.match(r'(?<ed>[a-z]+)(?:(?<vol_num>[0-9]+)\.)?(?<page_num>[0-9.]+)', volpage_id)
    
    if uid_m is None or vp_m is None:
        return None
        
    ed = vp_m['ed']
    if vp_m['vol_num']:
        vol = uid_m['vol'] + vp_m['vol_num']
    else:
        vol = uid_m['vol']
    page = vp_m['page_num']
    print((ed, vol, page))
    result = index.get((ed, vol, page), None)
    return result
