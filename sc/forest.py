import json
import regex
import hashlib
import logging
from colorama import Fore, Back
from collections import OrderedDict, defaultdict


import sc
import sc.tools.html
from sc.util import humansortkey

logger = logging.getLogger(__name__)

source_dir = sc.base_dir / 'newdata'
db_dir = sc.db_dir / 'forest'

if not db_dir.exists():
    db_dir.mkdir()


def make_file_key(file):
    key = str(file) + str(file.stat().st_mtime)
    return hashlib.sha1(key.encode()).hexdigest()[:12]

class Node(dict):
    """ A Node is dict with properties
    
    The dictionary key/values are serializable
    It also has helper *properties* that contain information
    that can be readily deduced from the structure and so do not
    need to be serialized, or cannot be serialized due to 
    circular references.
    
    """
    
    def __init__(self, *, parent=None, depth=0):
        self.parent = None
        self.depth = 0
        self.types = {}
    
    def has_as_ancestor(self, uid):
        if not self.parent:
            return False
        elif self.parent['uid'] == uid:
            return True
        elif self.parent.has_as_ancestor(uid):
            return True
        else:
            return False

class Forest:        
    def __init__(self, source_dir, db_dir):
        self.print('Loading Data Trees')
        self.mapping = defaultdict(list)
        self.parents = defaultdict(list)
        self.root_level_stems = [f.stem for f in source_dir.glob('*.json')]
        self.top_level_stems = [f.stem for f in source_dir.glob('*/*.json')]
        self.top_level_objects = {}
        self._file_to_object_mapping = {}
        self.source_dir = source_dir
        
        self._root = self.load_tree(target=source_dir)
        self.scan_html_files(data_cache_file = db_dir / 'data_cache.json')
        self.print('Building Mapping')
        self.build_mapping(self._root)
        self.print('Assigning types and properties')
        self.add_types(self._root)
        self.print('Everything Okay')
    
    def print(self, *args, **kwargs):
        print(Fore.WHITE + Back.GREEN + 'Forest:' + Fore.RESET + Back.RESET, *args, **kwargs)

    def load_tree(self, *, target, parent=None, depth=0):
        uid = target.stem
        out = Node(depth=depth)
        out['uid'] = uid
            
        if target.is_dir():
            children = [self.load_tree(target=child, parent=out, depth=depth+1) 
                        for child in sorted(target.iterdir(), key=lambda f: humansortkey(f.stem))
                        if child.stem not in self.root_level_stems]
            out['children'] = [child for child in children if child]
        elif target.suffix == '.json':
            with target.open('r', encoding='utf8') as f:
                data = json.load(f)
            if isinstance(data, list):
                out['children'] = self.promote_json_types(data)
            elif isinstance(data, dict):
                type_name = target.stem
                parent.types[type_name] = data
                return None
            else:
                raise ValueError('Malformed JSON Data in {}'.format(target.relative_to(self.source_dir)))
        elif target.suffix == '.html':
            out['file'] = str(target.relative_to(self.source_dir))
            self._file_to_object_mapping[target] = out
        return out
    
    def promote_json_types(self, data):
        if isinstance(data, list):
            return [self.promote_json_types(child) for child in data]
        elif isinstance(data, dict):
            node = Node()
            for k, v in data.items():
                node[k] = self.promote_json_types(v)
            return node
        else:
            return data
        
    
    def build_mapping(self, obj):
        if 'uid' in obj:
            self.mapping[obj['uid']].append(obj)
        if 'children' in obj:
            for child in obj['children']:
                try:
                    child.parent = obj
                except AttributeError:
                    print(child)
                    raise
                self.build_mapping(child)
    
    def add_types(self, obj):
        self.add_types_inner(obj)
        if 'children' in obj:
            for child in obj['children']:
                self.add_types(child)
    
    def add_types_inner(self, to_obj, from_obj=None):
        if not from_obj:
            from_obj = to_obj.parent
            if not from_obj:
                return
        uid = to_obj['uid']
        for type_name, type_mapping in from_obj.types.items():
            if uid in type_mapping:
                to_obj['type'] = type_name
                if isinstance(type_mapping[uid], str):
                    to_obj['name'] = type_mapping[uid]
                else:
                    to_obj.update(type_mapping[uid])
        if from_obj.parent:
            self.add_types_inner(to_obj, from_obj.parent)
    
    def scan_html_files(self, data_cache_file):
        
        # Load Cache
        
        file_data_cache = None
        
        try:
            with data_cache_file.open('r', encoding='utf8') as f:
                file_data_cache = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            pass
        
        if not type(file_data_cache) == dict:
            file_data_cache = {}
        
        # This is to check what contents of the cache are used
        seen = set()
        
        unexamined_files = []
        
        for file, obj in self._file_to_object_mapping.items():
            file_key = make_file_key(file)
            if file_key in file_data_cache:
                obj.update(file_data_cache[file_key])
                seen.add(file_key)
            else:
                unexamined_files.append( (file_key, file) )
        
        # clear cache of obsolete entries
        for key in list(file_data_cache):
            if key not in seen:
                del file_data_cache[key]
        
        if len(unexamined_files) > 0:
            self.print('{} new or modified text files to be scanned'.format(len(unexamined_files)))
        else:
            self.print('No new or modified text files')
        
        try:
            for file_key, file in unexamined_files:
                print('Forest: Extracting data from {!s}'.format(file.relative_to(self.source_dir)))
                root = sc.tools.html.parse(str(file)).getroot()
                name = self._get_name(root, file)
                file_data = {
                    'name': name
                }
                
                self._file_to_object_mapping[file].update(file_data)
                
                file_data_cache[file_key] = file_data
        
        finally:
            # Even if the processing is aborted, we want to save what
            # has been done so far.
            with data_cache_file.open('w', encoding='utf8') as f:
                json.dump(file_data_cache, f, ensure_ascii=False, indent=2)            
            
    def _get_name(self, root, file):
        try:
            hgroup = root.select_one('.hgroup')
            h1 = hgroup.select_one('h1')
            return regex.sub(r'^\P{alpha}*', '', h1.text_content())
        except Exception as e:
            logger.warn('Could not determine name for {!s}'.format(file.relative_to(self.source_dir)))
            return ''
            
            
class API:
    def __init__(self, forest):
        self.forest = forest
        self._subtree_hash_cache = {}
    
    def uids(self, *uids):
        if not uids:
            return {}
        depth = None
        if isinstance(uids[-1], int) or uids[-1].isdigit():
            depth = int(uids[-1])
            uids = uids[:-1]
        
        results = self.get_by_uids(*uids)
        
        return [self.make_pruned_subtree(obj=obj, depth=depth) for obj in results]
    
    def make_pruned_subtree(self, obj, depth):
        obj = dict(obj)
        if 'children' in obj:            
            if depth == 0:
                obj['children'] = len(obj['children'])
            else:
                if depth is not None:
                    depth = depth - 1
                obj['children'] = [self.make_pruned_subtree(child, depth) for child in obj['children']]
        return obj        
    
    def get_by_uids(self, *uids):
        uids = set(uids)
        
        results = []
        
        for uid in uids:
            other_uids = uids.difference({uid})
            for obj in self.forest.mapping[uid]:
                for other_uid in other_uids:
                    if not obj.has_as_ancestor(other_uid):
                        break
                else:
                    results.append(obj)
        return results
    
    def get_subtree_hash(self, *uids):
        key = tuple(uids)
        if key not in self._subtree_hash_cache:
            subtree = self.get_by_uids(*uids)
            self._subtree_hash_cache[key] = hashlib.blake2s(json.dumps(subtree, sort_keys=1, ensure_ascii=0).encode(encoding='utf8')).hexdigest()[:12]
            
        return self._subtree_hash_cache[key]
        
            
forest = Forest(source_dir=source_dir, db_dir=db_dir)
api = API(forest=forest)
