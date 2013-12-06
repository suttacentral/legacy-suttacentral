from invoke import Collection

from . import root
from . import assets
from . import db
from . import travis

ns = Collection.from_module(root)
ns.add_collection(assets)
ns.add_collection(db)
ns.collections['db'].add_collection(db.dump)
ns.add_collection(travis)
