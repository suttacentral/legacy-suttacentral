import inspect
import os
from invoke import Collection
from invoke.tasks import Task

from tasks.helpers import *

ns = Collection()
os.chdir(root_path)

import tasks.root
for name, obj in inspect.getmembers(tasks.root):
    if isinstance(obj, Task):
        ns.add_task(obj)

import tasks.assets
ns.add_collection(tasks.assets)
