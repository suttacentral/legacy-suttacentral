from invoke import Collection

from . import production
from . import staging

ns = Collection()
ns.add_collection(production)
ns.add_collection(staging)
