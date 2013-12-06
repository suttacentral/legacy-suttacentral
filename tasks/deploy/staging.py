"""Deploy to staging server tasks."""

from ..helpers import *

@task
def full():
    """Full deploy to the staging server."""
    remote_run('sc-staging@vps.suttacentral.net', [
        'source $HOME/.virtualenvs/suttacentral/bin/activate',
        'cd $HOME/suttacentral',
        'touch tmp/maintenance',
        'sudo supervisorctl stop sc-staging',
        'git pull',
        'cd text',
        'git pull',
        'cd ..',
        'pip install -q -r requirements.txt',
        'invoke clean --aggressive',
        'invoke db.reset',
        'invoke assets.compile',
        'sudo supervisorctl start sc-staging',
        'sudo service apache2 reload',
        'rm -f tmp/maintenance',
        'invoke dictionary.build',
        'invoke search.index',
    ])
