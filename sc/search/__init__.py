import logging
import elasticsearch
from elasticsearch import ConnectionError

logger = logging.getLogger(__name__)

es = elasticsearch.Elasticsearch()

def is_available():
    if not es.ping():
        return False
    return True
    

# Make elasticsearch STFU
logging.getLogger('elasticsearch').setLevel('ERROR')
logging.getLogger('elasticsearch.trace').setLevel('ERROR')
