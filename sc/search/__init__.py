import logging
import elasticsearch
from elasticsearch import ConnectionError

import sc.logger
logger = sc.logger.get_named_logger('search')

es = elasticsearch.Elasticsearch()

def is_available():
    if not es.ping():
        return False
    return True

# Make elasticsearch STFU
logging.getLogger('elasticsearch').setLevel('ERROR')
logging.getLogger('elasticsearch.trace').setLevel('ERROR')

def update_indexes():
    if not is_available():
        logger.error('Elasticsearch Not Available')
        return
    import sc.search.dicts
    import sc.search.texts
    import sc.search.suttas
    import sc.search.autocomplete

    sc.search.dicts.update()
    sc.search.suttas.update()
    sc.search.texts.update()
    sc.search.autocomplete.update()
    
