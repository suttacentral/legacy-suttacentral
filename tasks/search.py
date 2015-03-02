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
