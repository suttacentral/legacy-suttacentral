"""Search tasks."""

from tasks.helpers import *


@task
def delete(index='_all'):
    """Deleting specified Elasticsearch indexes"""
    blurb(delete)
    result = http_request(domain='localhost:9200', path='/{}'.format(index), method='DELETE')
    print(result)


@task
def index():
    """Create the search index SQLite databases."""
    blurb(index)
    import sc.search.texts
    textsearch.build()

@task
def dump_lookup_data(file='lookup-data.json'):
    """Dump non-reproducible data from the es indexes"""
    import sc.search.dumpload
    print('Dumping data to {!s}'.format(file))
    sc.search.dumpload.dump_lookup_data(file)
    print('Success')

@task
def load_lookup_data(file='lookup-data.json'):
    import sc.search.dumpload
    sc.search.dumpload.load_lookup_data(file)
    print('Success')
    
