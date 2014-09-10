import json
import sc
from sc.util import recursive_merge

import logging
logger = logging.getLogger(__name__)

def load_index_config(name, _seen=None):
    if _seen is None:
        _seen = set()

    if name in _seen:
        logger.Error("Inherited file {} already encountered, skipping".format(name))
        return out
    _seen.add(name)

    file = (sc.indexer_dir / name).with_suffix('.json')

    out = {}
    
    with file.open('r', encoding='utf8') as f:
        try:
            config = json.load(f)
        except ValueError:
            logger.error('An error occured while parsing {!s}'.format(file))
            raise
        
    for filename in config.get("inherits", []):
        inherited_config = load_index_config(filename, _seen)
        recursive_merge(out, inherited_config)
    recursive_merge(out, config.get("index", {}))
    return out
