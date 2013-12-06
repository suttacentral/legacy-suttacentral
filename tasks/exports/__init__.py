from invoke import Collection

from . import db
from . import offline

ns = Collection()
ns.add_collection(db)
ns.add_collection(offline)
