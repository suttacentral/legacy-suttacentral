"""Database dump tasks."""

import urllib

import config
import util
from ..helpers import *

remote_dump_url = 'http://suttacentral.net/exports/sc-db-latest.zip'
local_dump_path = os.path.join(config.base_dir, 'tmp',
    'sc-db-latest.zip')

@task
def clean():
    """Delete the downloaded MySQL database dump."""
    blurb(clean)
    rm_rf(local_dump_path)

@task(aliases=('fetch',))
def download():
    """Download the latest MySQL database dump from the production server."""
    blurb(download)
    r = urllib.request.urlopen(remote_dump_url)
    with open(local_dump_path, 'b+w') as f:
        f.write(r.read())

@task(name='import')
def import_():
    """Import the downloaded MySQL database dump into the local MySQL database."""
    blurb(import_)
    input_cmd = local['unzip']['-p', local_dump_path, '*/suttacentral.sql']
    mysql(input_cmd, db=True)
