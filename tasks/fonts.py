"""Font tasks."""

from tasks.helpers import *


@task
def download_nonfree():
    """Download nonfree fonts from the production server."""
    blurb(download_nonfree)
    run('rsync -avz sc-production@vps.suttacentral.net:' +
        '/home/sc-production/suttacentral/static/fonts/nonfree/ ' +
        'static/fonts/nonfree/', fg=True)
