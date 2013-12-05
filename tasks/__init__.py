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

for name in ['assets', 'db', 'travis']:
    __import__('tasks.' + name)
    ns.add_collection(eval('tasks.' + name))
