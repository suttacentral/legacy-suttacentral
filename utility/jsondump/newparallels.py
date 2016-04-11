import sys
sys.path.insert(0, '../..')

import sc, sc.scimm
from time import time as ttime
import collections

imm = sc.scimm.imm()

suttas = []
for c in imm.collections.values():
    for d in c.divisions:
        for sd in d.subdivisions:
            for v in sd.vaggas:
                suttas.extend(v.suttas)


from lxml import etree
parallels = etree.Element('parallels')



def is_valid_parallel(sutta, uid):
    for parallel in sutta.parallels:
        if parallel.sutta.uid == uid:
            if not parallel.partial:
                return True
            return False
    return False


parallel_groups_seen = set()
parallel_pairs_seen = set()

def make_key(uid, other_uid, partial):
    return tuple(sorted((uid, other_uid)) + [partial or None])

# Create Parallel Pairs
for sutta in suttas:
    uid = sutta.uid

    # Create a group for this sutta
    group = etree.SubElement(parallels, 'parallel')
    group_seen = set()

    if hasattr(sutta, 'parallel_group'):
        groups = [sutta.parallel_group]
        if isinstance(groups[0], sc.classes.MultiParallelSuttaGroup):
            groups = groups[0].groups

        for pg in groups:
            if pg in parallel_groups_seen:
                continue
            parallel_groups_seen.add(pg)
            groupe = etree.SubElement(parallels, 'parallel', type='group', name=pg.name)
            for entry in pg.entries:
                if isinstance(entry, sc.classes.GroupedSutta):
                    etree.SubElement(groupe, 'll', sutta=entry.uid)
                elif isinstance(entry, sc.classes.MaybeParallel):
                    etree.SubElement(groupe, 'maybe', division=entry.division.uid)
                elif isinstance(entry, sc.classes.NegatedParallel):
                    etree.SubElement(groupe, 'negated', division=entry.division.uid)
    
    for parallel in sutta.parallels:
        other_uid = parallel.sutta.uid
        partial = parallel.partial
        key = make_key(uid, other_uid, partial)
        if key in parallel_pairs_seen:
            continue

        # Can this sutta be added to the group?
        if not partial:
            for group_uid in group_seen:
                if not is_valid_parallel(imm.suttas[group_uid], other_uid):
                    break
            else:
                group.append(etree.Element('ll', sutta=other_uid))
                parallel_pairs_seen.add(key)
                group_seen.add(other_uid)
                continue
        
        e = etree.SubElement(parallels, 'parallel')
        
        if partial:
            e.set('partial', 'y')
        e.append(e.makeelement('ll', sutta=uid))
        e.append(e.makeelement('ll', sutta=other_uid))

        parallel_pairs_seen.add(key)
    
    if len(group_seen) > 1:
        for uid1 in group_seen:
            for uid2 in group_seen:
                if uid1 == uid2:
                    continue
                key = make_key(uid1, uid2, None)
                parallel_pairs_seen.add(key)
        

    if len(group) == 0:
        parallels.remove(group)
    else:
        group.insert(0, e.makeelement('ll', sutta=uid))

open('parallels.xml', 'wb').write(etree.tostring(parallels, encoding='utf8', xml_declaration=True, pretty_print=True))
uid_map = collections.defaultdict(list)
for e in parallels.iter():
    uid = e.get('sutta')
    if uid:
        uid_map[uid].append(e)



def get_parallels(uid):
    start=ttime()
    sutta_parallels = []
    for sut in parallels.findall('parallel/ll[@sutta="{}"]'.format(uid)):
        p = sut.getparent()
        sutta_parallels.extend((e.get('sutta'), p.get('partial', False), p.get('note', None)) for e in p if e is not sut)
    print('Parallels generation for {} took {} s'.format(uid, ttime() - start))
    return sutta_parallels

def get_parallels_accl(uid):
    start=ttime()
    sutta_parallels = []
    for sut in uid_map[uid]:
        p = sut.getparent()
        sutta_parallels.extend((e.get('sutta'), p.get('partial', False), p.get('note', None)) for e in p if e is not sut)
    print('Parallels generation for {} took {} s'.format(uid, ttime() - start))
    return sutta_parallels
    
print(get_parallels('dn16'))

def vinaya_ll(uid):
    start=ttime()
    out = []
    #groups = parallels.findall('parallel/ll[@sutta="{}"]/..'.format(uid))
    groups = [e.getparent() for e in uid_map[uid]]
    if len(set(len(g) for g in groups)) == 1:
        for elements in zip(*groups):
            seen = set()
            for e in elements:
                uid = e.get('sutta') or e.get('division')
                if uid in seen:
                    continue
                seen.add(uid)
                out.append(uid)
    else:
        seen = set()
        for elements in itertools.chain(*groups):
            pass
    print('Parallels generation for {} took {} s'.format(uid, ttime() - start))
    return out

print(vinaya_ll('pi-tv-bi-vb-ss3'))
from collections import OrderedDict

def xml_to_json(root):
    out = []
    for parallel in root:
        ll = OrderedDict()
        ll['group'] = group = []
        for child in parallel:
            if child.tag == 'll':
                group.append(child.get('sutta'))
            elif child.tag == 'maybe':
                group.append('?{}'.format(child.get('division')))
            elif child.tag == 'negated':
                group.append('-{}'.format(child.get('division')))
        for key in sorted(parallel.attrib):
            if key in {'sutta', 'division'}:
                pass
            if parallel.get('partial'):
                ll['partial'] = 1
            if parallel.get('note'):
                ll['note'] = parallel.get('note')
        out.append(ll)
    return out

ll_json = xml_to_json(parallels)

import regex
def fix_whitespace(m):
    return regex.sub(r'\s+', '', m[0]).replace('","', '", "')

import json
with open('ll.json.txt', 'w') as f:
    f.write(
        regex.sub(r'(?s)(?<=: )\[.*?\]', fix_whitespace,
              json.dumps(ll_json, ensure_ascii=0, indent=2)))
