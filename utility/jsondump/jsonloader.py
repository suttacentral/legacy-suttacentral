import sys
sys.path.insert(0, '../..')
from sc.util import recursive_merge

import time
import json
import pathlib

import time

from contextlib import contextmanager

@contextmanager
def timed(name):
    startTime = time.time()
    yield
    elapsedTime = time.time() - startTime
    print('[{}] finished in {} ms'.format(name, int(elapsedTime * 1000)))
    
def load(path):
    out = {}
    for file in path.iterdir():
        key = file.stem
        if file.is_dir():
            subtree = load(file)
        elif file.suffix == '.json':
            with file.open('r', encoding='UTF-8') as f:
                subtree = json.load(f)
        if key not in out:
            out[key] = subtree
        else:
            recursive_merge(out[key], subtree)
    return out



class Section(dict):
    uid = None
    parent = None
    children = ()
    
    @property
    def ancestors(self):
        section = self.parent
        out = []
        while section:
            out.append(section)
        

def build_section_tree(obj):
    out = Section(obj)
    for key, value in obj.items():
        if isinstance(value, dict):
            child = build_section_tree(value)
            child.parent = out
            child.uid = key
            if not out.children:
                out.children = []
            out.children.append(child)
            out[key] = child
    return out


def build_uid_mapping(obj):
    mapping = {}
    stack = [obj]
    while stack:
        current = stack.pop()
        for key, value in current.items():
            if isinstance(value, dict):
                stack.append(value)
                mapping[key] = value
    return mapping


with timed('Load Raw Json'):
    with open('root.json') as f:
        foo = json.load(f)

with timed('Load Raw Json w/o whitespace'):
    with open('root_no_ws.js') as f:
        foo = json.load(f)

import pickle
with timed("Load Pickle data"):
    with open('root.pickle', 'rb') as f:
        root_pickle = pickle.load(f)




with timed("load JSON data"):
    json_root = load(pathlib.Path('sectioned'))

with timed("load JSON data (No whitespace)"):
    json_root = load(pathlib.Path('sectioned'))


with timed("convert to fancy dicts"):
    root = build_section_tree(json_root)

with timed("Build inverse index"):
    uid_index = build_uid_mapping(root)




def load_parallels(file):
    with file.open('r', encoding='UTF-8') as f:
        return json.load(f)

def build_parallels_index(parallels):
    parallels_index = {}

    for obj in parallels:
        for uid in obj['group']:
            if uid[0] in {'?', '-'}:
                continue
            if uid not in parallels_index:
                parallels_index[uid] = []
            parallels_index[uid].append(obj)
    return parallels_index
        
def calculate_parallels(uid, index):
    results = []
    seen = {}
    for obj in index[uid]:
        for ll_uid in obj['group']:
            if ll_uid == uid:
                continue
            if ll_uid in seen:
                ll = seen[ll_uid]
            else:
                if ll_uid.startswith('-'):
                    ll['negated'] = True
                    ll = {'uid': ll_uid[1:]}
                elif ll_uid.startswith('?'):
                    ll['maybe'] = True
                    ll = {'uid': ll_uid[1:]}
                else:
                    ll = {'uid': ll_uid}
                    if 'partial' in obj:
                        ll['partial'] = True
            if 'note' in obj:
                ll['note'] = obj['note']
            if ll_uid not in seen:
                results.append(ll)
                seen[ll_uid] = ll
    return results

with timed("Loading Parallels JSON"):
    parallels = load_parallels(pathlib.Path('ll.json.txt'))

with timed("Build Inverted Index for Parallels"):
    parallels_index = build_parallels_index(parallels)


with timed("Calculate parallels for DN16"):
    dn16ll = calculate_parallels('dn16', parallels_index)
print(dn16ll)

def verify_parallels(*uids):
    import sc.scimm
    imm = sc.scimm.imm()
    for uid in uids:
        calc = {p['uid'] for p in calculate_parallels(uid, parallels_index)}
        simm = {p.sutta.uid for p in imm.suttas[uid].parallels}
        if calc==simm:
            print('{} passes'.format(uid))
        else:
            print('{} fails'.format(uid))

verify_parallels('dn16', 'dn2', 'mn1', 'mn10', 'mn16')
