import pathlib
import sys

# Setup sys.path to import modules from the project directory.
src_path = str(pathlib.Path(__file__).resolve().parents[1] / 'src')
if src_path not in sys.path:
    sys.path.insert(1, src_path)
del src_path

from invoke import Collection

from .root import *

from . import assets
from . import analysis
from . import deploy
from . import dictionary
from . import exports
from . import fonts
from . import log
from . import newrelic
from . import search
from . import test
from . import tmp
from . import travis

ns = Collection.from_module(sys.modules[__name__])
ns.add_collection(assets)
ns.add_collection(analysis)
ns.add_collection(deploy)
ns.add_collection(dictionary)
ns.add_collection(exports)
ns.add_collection(fonts)
ns.add_collection(log)
ns.add_collection(newrelic)
ns.add_collection(search)
ns.add_collection(test)
ns.add_collection(tmp)
ns.add_collection(travis)
