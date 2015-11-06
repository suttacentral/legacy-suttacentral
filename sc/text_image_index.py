import regex
import threading
from collections import namedtuple
from typing import Mapping

import sc
from sc.views import ViewBase
from sc.util import Timer


import pathlib

_index_ready = threading.Event()
index = {}

class NormalizedId(str):
    pass

def build(n=0):
    global index
    index = create_index_and_update_symlinks()
    _index_ready.set()

cache_filename_template = 'text-image-index_{}.pklz'

def create_index_and_update_symlinks() -> Mapping[NormalizedId, str]:
    """ Symlinks are used mainly for the ease of serving with Nginx """
    
    def image_filter(filename):
        return filename.endswith('.png') or filename.endswith('.jpg')
    
    symlink_md5 = sc.util.get_folder_shallow_md5(folder=sc.text_image_symlink_dir, check_mtime=False, include_filter=image_filter)
    images_md5 = sc.util.get_folder_deep_md5(folder=sc.text_image_source_dir, check_mtime=True, include_filter=image_filter)
    
    combined_md5 = symlink_md5
    combined_md5.update(symlink_md5.digest())
    cache_file = sc.db_dir / cache_filename_template.format(combined_md5.hexdigest()[:10])
    if cache_file.exists():
        try:
            cached = sc.util.lz4_pickle_load(cache_file)
            print('Loading cached Text Image Index from disk')
            return cached
        except Exception as e:
            print(e)
            cache_file.unlink()
    
    tmp_index = {}
    
    source_files = [f for 
             f in sc.text_image_source_dir.glob('**/*') 
             if f.suffix in {'.png', '.jpg'}]
    source_files.sort(key=str)

    symlink_dir = sc.text_image_symlink_dir.absolute()
    for file in source_files:
        normalized_id = normalize_id(file.stem)
        symlink = (symlink_dir / normalized_id).with_suffix(file.suffix)
        if normalized_id in tmp_index:
            raise ValueError('Duplicate filename detected: {!s}'.format(file))
        tmp_index[normalized_id] = symlink.name
        if symlink.is_symlink():
            if symlink.resolve() == file:
                continue
            else:
                symlink.unlink()

        symlink.parent.mkdir(parents=True, exist_ok=True)
        symlink.symlink_to(file)
    print('Saving Text Image Index to disk')
    sc.util.lz4_pickle_dump(tmp_index, cache_file)
    clear_old_cache_files(newest=cache_file)
    return tmp_index

def clear_old_cache_files(newest):
    for file in sc.db_dir.glob(cache_filename_template.format('*')):
        if file == newest:
            continue
        else:
            file.unlink()

def normalize_id(value, _divs=set()) -> NormalizedId:
    # Normalize into form:
    # manuscript-book-vol-page
    # pts-mn-1-96
    # vl
    
    if not _divs:
        import sc.scimm
        imm = sc.scimm.imm()
        _divs.update(imm.divisions)
        _divs.update(subdiv.uid for subdiv in imm.divisions['kn'].subdivisions)
        _divs.add('vi')
    
    if 'pts' in value:
        value = value.replace('-pg.', '-').replace('-vol.', '').replace('.', '-').replace('-pg-', '-').replace('--', '-').replace('-jat', '-ja')
        value = regex.sub(r'\d+', lambda m: str(int(m[0])), value)
        value = regex.sub(r'[a-z]+(?=\d)', lambda m: m[0] + '-' if m[0] in _divs else m[0], value)
    return NormalizedId(value)

def get(sutta_uid, volpage) -> str:
    _index_ready.wait()
    m = regex.match('[a-z]+', sutta_uid)
    if not m:
        return None
    div = m[0]
    
    if volpage.startswith('pts'):
        if volpage.startswith('pts-vp-pi'):
            # This is vinaya
            volpage = normalize_id('pts-vi-' + volpage[9:])
        else:
            # check if uid is pre-hyphened as is the case with 
            # sn pts1 and pts2
            m = regex.match(r'^(pts[123]-)(.*)', volpage)
            if m:
                volpage = normalize_id(m[1] + div + '-' + m[2])
            else:
                volpage = normalize_id('pts-' + div + '-' + volpage[3:])
        
    result = index.get(volpage, None)
    if not result:
        print(volpage)
    return result
