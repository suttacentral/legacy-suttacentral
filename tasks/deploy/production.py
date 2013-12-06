"""Deploy to production server tasks."""

from ..helpers import *

@task
def full():
    """Full deploy to the production server."""
    remote_run('sc-production@vps.suttacentral.net', [
        'source $HOME/.virtualenvs/suttacentral/bin/activate',
        'cd $HOME/suttacentral',
        'touch tmp/maintenance',
        'sudo supervisorctl stop sc-production',
        'git pull',
        'cd text',
        'git pull',
        'cd ..',
        'pip install -q -r requirements.txt',
        'invoke assets.compile',
        'sudo supervisorctl start sc-production',
        'sudo service apache2 reload',
        'rm -f tmp/maintenance',
        'invoke dictionary.build',
        'invoke search.index',
        'invoke assets.clean --older',
    ])

@task
def quick():
    """Quick deploy to the production server."""
    remote_run('sc-production@vps.suttacentral.net', [
        'source $HOME/.virtualenvs/suttacentral/bin/activate',
        'cd $HOME/suttacentral',
        'git pull',
        'cd text',
        'git pull',
        'cd ..',
        'pip install -q -r requirements.txt',
        'invoke assets.compile',
        'sudo supervisorctl restart sc-production',
        'invoke assets.clean --older',
    ])

@task
def text():
    """Text-only deploy to the production server."""
    remote_run('sc-production@vps.suttacentral.net', [
        'source $HOME/.virtualenvs/suttacentral/bin/activate',
        'cd $HOME/suttacentral',
        'cd text',
        'git pull',
        'cd ..',
        'invoke search.index',
    ])
