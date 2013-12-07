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

@task
def nonfree_fonts():
    """Copy local nonfree fonts to the staging server."""
    run('rsync -avz ' + \
        'static/fonts/nonfree/ ' + \
        'sc-staging@vps.suttacentral.net:' + \
        '/home/sc-staging/suttacentral/static/fonts/nonfree/')

@task
def quick():
    """Quick deploy to the staging server."""
    remote_run('sc-staging@vps.suttacentral.net', [
        'source $HOME/.virtualenvs/suttacentral/bin/activate',
        'cd $HOME/suttacentral',
        'git pull',
        'cd text',
        'git pull',
        'cd ..',
        'pip install -q -r requirements.txt',
        'invoke assets.compile',
        'sudo supervisorctl restart sc-staging',
        'invoke assets.clean --older',
    ])
