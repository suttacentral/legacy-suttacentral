from invoke import Collection

from tasks.deploy import production, staging

ns = Collection()
ns.add_collection(production)
ns.add_collection(staging)
