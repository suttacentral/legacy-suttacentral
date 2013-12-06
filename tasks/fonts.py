"""Font tasks."""

from .helpers import *

@task
def download_nonfree():
    """Download nonfree fonts from the production server."""
    run('rsync -avz sc-production@vps.suttacentral.net:' + \
        '/home/sc-production/suttacentral/static/fonts/nonfree/ ' + \
        'static/fonts/nonfree/')
