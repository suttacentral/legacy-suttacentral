import pathlib
import sys
from invoke import Collection

from tasks.root import *

ns = Collection.from_module(sys.modules[__name__])

collections = [
    'assets',
    'analysis',
    'deploy',
    'dictionary',
    'exports',
    'fonts',
    'jsdata',
    'log',
    'newrelic',
    'search',
    'test',
    'textdata',
    'tmp',
    'travis',
]

for collection in collections:
    exec('from tasks import {} as module'.format(collection))
    ns.add_collection(module)
