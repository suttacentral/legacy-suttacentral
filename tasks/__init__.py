from invoke import Collection

from . import root
from . import assets
from . import db
from . import dictionary
from . import exports
from . import fonts
from . import newrelic
from . import search
from . import travis

ns = Collection.from_module(root)
ns.add_collection(assets)
ns.add_collection(db)
ns.collections['db'].add_collection(db.dump)
ns.add_collection(dictionary)
ns.add_collection(fonts)
ns.add_collection(Collection('exports'))
ns.collections['exports'].add_collection(exports.db)
ns.collections['exports'].add_collection(exports.offline)
ns.add_collection(newrelic)
ns.add_collection(search)
ns.add_collection(travis)
