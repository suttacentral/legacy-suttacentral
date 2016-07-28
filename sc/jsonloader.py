
import json
import regex
import logging

from enum import Enum
from itertools import chain
from collections import defaultdict

from sc.util import unique, humansortkey


logger = logging.getLogger(__name__)

import sc

relationship_types = ['parallels', 'mentions', 'retells']

forward_relationship_names = {
    'parallels': 'parallels',
    'mentions': 'is mentioned in',
    'retells': 'is retold in'
}

inverse_relationship_names = {
    'parallels': 'parallels',
    'mentions': 'mentions',
    'retells': 'retells'
}

class Location:
    def __init__(self, uid, bookmark=None):
        self.partial = uid.startswith('~')
        uid = uid.lstrip('~')
        
        if '#' in uid:
            if bookmark:
                raise ValueError("Bookmark should be None if uid contains '#'")
            self.uid, self.bookmark = regex.match(r'(.*?)(#.*)', uid)[1:]
        else:
            self.uid = uid
            self.bookmark = bookmark
        self.node = None
        self.root_lang = None
    def __str__(self):
        if not self.bookmark:
            return self.uid
        else:
            return '{}{}'.format(self.uid, self.bookmark)
    def __repr__(self):
        return 'Location({}={}, {}={}, {}={})'.format(
            "uid", repr(self.uid),
            "bookmark", repr(self.bookmark),
            "node", repr(self.node)
        )
    
    def __hash__(self):
        return self.uid.__hash__() ^ self.bookmark.__hash__()
    
    @property
    def sort_key(self):
        return humansortkey(str(self))        
    
    def attach_node(self, imm):
        self.node = imm(self.uid)
        self.root_lang = imm.guess_lang(self.uid)

class Relationship:
    def __init__(self, left, right, relationship_type, relationship_name, partial):
        self.left = left
        self.right = right
        self.relationship_type = relationship_type
        self.relationship_name = relationship_name
        self.partial = partial
    
    def attach_nodes(self, imm):
        self.left.attach_node(imm)
        self.right.attach_node(imm)
        
    def __repr__(self):
        return '\nRelationship({}={},{}={},{}={},{}={})'.format(
            "left", repr(str(self.left)),
            "right", repr(str(self.right)),
            "relationship_type", repr(self.relationship_type),
            "relationship_name", repr(self.relationship_name),
            "partial", repr(self.partial)
        )
    def __str__(self):
        return '{} {}{} {}'.format(self.left.uid, '~' if self.partial else '', self.relationship_type, self.right.uid) 
    
    def __hash__(self):
        return self.left.__hash__() ^ self.right.__hash__() ^ self.relationship_type.__hash__() ^ self.partial.__hash__()

class ParallelsManager:
    def __init__(self, data):
        self.data = data
        self.update_mapping()
    
    def update_mapping(self):
        uid_mapping = defaultdict(list)
        for entry in self.data['suttas']:
            # when we have an entry like this:
            #{
            #   "uids": ["an8.81", "ma44", "~ma45", "~an7.65", "~an6.50", "~ma47", "~an11.3", "~an10.3", "~ma48", "~an11.4", "~an5.21", "~ma49", "~an5.22", "~ma50", "~an5.24", "~an5.168", "~ma46", "~sa495", "~an10.4"]
            #},
            # it means that an8.81 and ma44 are parallels of each other,
            # while ~ma45 and all other tidles are partially parallel to an8.81 and ma44
            # this means 
            
            seen_in_entry = set()
            for uid in unique(chain.from_iterable(entry.get(relationship_type, []) for relationship_type in relationship_types)):
                normalized_uid = self.normalize_uid(uid)
                if normalized_uid in seen_in_entry:
                    logger.error('uid {} appears multiple times in entry: {}'.format(uid, entry))
                uid_mapping[normalized_uid].append(entry)
            
        self.uid_mapping = uid_mapping
    
    def normalize_uid(self, uid):
        return uid.lstrip('~').split('#')[0]
    
    def is_partial(self, uid):
        if uid.startswith('~'):
            return True
        if uid.startswith('sht-'):
            return True
        return False
    
    def get_relationships(self, uid):
        uid_mapping = self.uid_mapping
        is_partial = self.is_partial
        
        relationships = []
        
        if not uid in uid_mapping:
            return None
        
        found = False
        for entry in uid_mapping[uid]:
            for relationship_type in relationship_types:
                if relationship_type not in entry:
                    continue
                
                locations = [Location(uid) for uid in entry[relationship_type]]
                for location in locations:
                    print(location.uid)
                    if location.uid == uid:
                            this_location = location
                            break
                else:
                    # It is possible a uid does not participate in every 
                    # clause in a group
                    continue                        
                
                if relationship_type == 'parallels':
                    for other_location in locations:
                        if other_location == this_location:
                            continue
                        if this_location.partial and other_location.partial:
                            # a partial is not parallel to a partial
                            continue
                        relationships.append(Relationship(left=this_location, 
                                                          right=other_location,
                                                          relationship_type=relationship_type,
                                                          relationship_name=forward_relationship_names[relationship_type],
                                                          partial=this_location.partial or other_location.partial))
                if relationship_type in {'mentions', 'retells'}:
                    if this_location == locations[0]:
                        # this sutta is the one which is mentioned
                        relationship_name = forward_relationship_names[relationship_type]
                        for other_location in locations:
                            if other_location == this_location:
                                continue
                            relationships.append(Relationship(this_location,
                                                              other_location,
                                                              relationship_type=relationship_type,
                                                              relationship_name=relationship_name,
                                                              partial = this_location.partial or other_location.partial))
                    else:
                        relationship_name = inverse_relationship_names[relationship_type]
                        other_location = locations[0]
                        relationships.append(Relationship(this_location,
                                                          other_location,
                                                          relationship_type=relationship_type,
                                                          relationship_name=relationship_name,
                                                          partial = this_location.partial or other_location.partial))
                
        return sorted(relationships, key=lambda o: humansortkey(str(o.left)))
                        
                    
                
            

def load_json_file(name):
    with (sc.json_data_dir / name).with_suffix('.json').open(encoding='utf8') as f:
        return json.load(f)
    

def load_parallels():
    data = load_json_file('parallels')
    return ParallelsManager(data)

parallels_manager = load_parallels()
