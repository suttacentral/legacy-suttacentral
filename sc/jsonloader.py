
import json
import regex
import logging

from enum import Enum
from itertools import chain
from collections import defaultdict

from sc.util import unique


logger = logging.getLogger(__name__)

import sc

relationship_types = ['parallels', 'mentions']

class Relationship:
    def __init__(self, uid, other_uid, relationship_type, partial):
        self.uid = uid
        self.other_uid = other_uid
        self.relationship_type = relationship_type
        self.partial = partial

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
            
            if 'uids' in entry:
                seen_in_entry = set()
                for uid in unique(entry.get('parallels', []) + entry.get('mentions', [])):
                    normalized_uid = uid.lstrip('~').split('#')[0]
                    if normalized_uid in seen_in_entry:
                        logger.error('uid {} appears multiple times in entry: {}'.format(uid, entry))
                    uid_mapping[normalized_uid].append(entry)
            
        self.uid_mapping = uid_mapping
    
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
            if 'parallels' in entry:
                uids = entry['parallels']
                for parallel_uid in uids:
                    if parallel_uid.lstrip('~').split('#')[0] == uid:
                        this_uid = parallel_uid
                        found = True
                        break
                
                for parallel_uid in uids:
                    if parallel_uid == this_uid:
                        continue
                    if is_partial(this_uid) and is_partial(parallel_uid):
                        # a partial is not parallel to a partial
                        continue
                    relationships.append(Relationship(uid=this_uid, other_uid=parallel_uid, relationship="parallels", self.is_partial(this_uid))
                    
                        
                    
                
            

def load_json_file(name):
    with (sc.json_data_dir / name).with_suffix('.json').open(encoding='utf8') as f:
        return json.load(f)
    

def load_parallels():
    data = load_json_file('parallels')
    return ParallelsManager(data)

parallels_manager = load_parallels()
