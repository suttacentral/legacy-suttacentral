import regex
from collections import namedtuple

import sc
from sc.views import ViewBase
from sc.util import Timer


import pathlib

index = {}

def update_symlinks(n=0):
    """ Symlinks are used mainly for the ease of serving with Nginx """
    
    source_files = [f for 
             f in sc.text_image_source_dir.glob('**/*') 
             if f.suffix in {'.png', '.jpg'}]
    source_files.sort(key=str)

    
    symlink_dir = sc.text_image_symlink_dir.absolute()
    for file in source_files:
        normalized_id = normalize_id(file.stem)
        symlink = (symlink_dir / normalized_id).with_suffix(file.suffix)
        if normalized_id in index:
            raise ValueError('Duplicate filename detected: {!s}'.format(file))
        index[normalized_id] = symlink.name
        if symlink.is_symlink():
            if symlink.resolve() == file:
                continue
            else:
                symlink.unlink()    
        if not symlink.parent.exists():
            symlink.parent.mkdir(parents=True)
        
        symlink.symlink_to(file)
    

def normalize_id(value, _divs=set()):
    # Normalize into form:
    # manuscript-book-vol-page
    # pts-mn-1-96
    # vl
    
    if not _divs:
        import sc.scimm
        imm = sc.scimm.imm()
        _divs.update(imm.divisions)
        _divs.add('vi')
    
    if 'pts' in value:
        value = value.replace('-pg.', '-').replace('-vol.', '').replace('.', '-').replace('-pg-', '-').replace('--', '-').replace('-jat', '-ja')
        value = regex.sub(r'\d+', lambda m: str(int(m[0])), value)
        value = regex.sub(r'[a-z]+(?=\d)', lambda m: m[0] + '-' if m[0] in _divs else m[0], value)
    return value

def get(sutta_uid, volpage):
    
    m = regex.match('[a-z]+', sutta_uid)
    if not m:
        return None
    div = m[0]
    
    if volpage.startswith('pts'):
        if volpage.startswith('pts-vp-pi'):
            # This is vinaya
            volpage = normalize_id('pts-vi-' + volpage[9:])
        else:
            volpage = normalize_id('pts-' + div + '-' + volpage[3:])
        
    result = index.get(volpage, None)
    return result
