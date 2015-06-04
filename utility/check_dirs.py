import pathlib

import env
import sc
import sc.scimm
imm = sc.scimm.imm()
import sc.updater
sc.updater.halt = 1
from sc.util import unique

def calculate_path(html_file):
   try:
    uid = html_file.stem
    sutta = imm.suttas.get(uid)
    subdivision = imm.subdivisions.get(uid)
    division = imm.divisions.get(uid)
    if not (sutta or subdivision or division):
        sliced = uid[:-1]
        while sliced:
            sutta = imm.suttas.get(sliced)
            subdivision = imm.subdivisions.get(sliced)
            division = imm.divisions.get(sliced)
            if sutta or subdivision or division:
                break
            sliced = sliced[:-1]
        else:
            print('Uid simply not recognized: {}'.format(uid))
            return None
            
    subdivision = subdivision or (sutta.subdivision if sutta else None)
    division = division or subdivision.division
    collection = division.collection
    pitaka = collection.pitaka
    language = collection.lang
    
    path = [language.uid, pitaka.uid, division.uid]
    if subdivision and subdivision.uid != division.uid:
        path.append(subdivision.uid)
    if path[-1] == uid:
        path = path[:-1]
    return path
    
   except:
       globals().update(locals())
       raise

good = []
bad = []
dirs = set()
renames = []
for text_dir in sc.text_dir.glob('*'):
    if text_dir.is_dir():
        print(text_dir.relative_to(sc.text_dir))
        for html_file in text_dir.glob('**/*.html'):
            if html_file.stem == 'metadata':
                continue

            parts = calculate_path(html_file)
            if not parts:
                print('Could not determine path for: {}'.format(html_file.relative_to(sc.text_dir)))
                continue
            
            if text_dir.stem == parts[0]:
                parts = parts[1:]
            new_path = pathlib.Path(text_dir, *parts)
            
            if new_path == html_file.parent:
                good.append(html_file)
            else:
                bad.append((html_file.relative_to(sc.text_dir), pathlib.Path(new_path)))
                dirs.add(html_file.parent)
                
                if not new_path.exists():
                    new_path.mkdir(parents=True)
                renames.append('git mv {!s} {!s}'.format(html_file, new_path / html_file.name))
                html_file.rename(new_path / html_file.name)
                
for dir in dirs:
    try:
        dir.unlink()
    except:
        pass
print('{} good, {} bad'.format(len(good), len(bad)))
