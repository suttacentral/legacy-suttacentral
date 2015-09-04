from invoke import Collection

from tasks.deploy import production, staging, cloudflare

ns = Collection()
ns.add_collection(production)
ns.add_collection(staging)
ns.add_collection(cloudflare)
