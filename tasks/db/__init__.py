import sys

from invoke import Collection

from .root import *

from . import dump

ns = Collection.from_module(sys.modules[__name__])
ns.add_collection(dump)
