"""Deploy to staging server tasks."""

from ..helpers import *

def _branch_or_pull(branch):
    if branch:
        return ('git fetch && ' + \
                'git checkout {0} || git checkout -t origin/{0} && ' + \
                'git pull').format(branch)
    else:
        return 'git pull'

@task
@blurb
def full(branch=None):
    """Deploy to the staging server."""
    remote_run('sc-staging@vps.suttacentral.net', [
        'source $HOME/.virtualenvs/suttacentral/bin/activate',
        'cd $HOME/suttacentral',
        'touch tmp/maintenance',
        'sudo supervisorctl stop sc-staging',
        _branch_or_pull(branch),
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
@blurb
def nonfree_fonts():
    """Copy local nonfree fonts to the staging server."""
    run('rsync -avz ' + \
        'static/fonts/nonfree/ ' + \
        'sc-staging@vps.suttacentral.net:' + \
        '/home/sc-staging/suttacentral/static/fonts/nonfree/', fg=True)

@task
@blurb
def quick(branch=None):
    """Deploy simple changes to the staging server."""
    remote_run('sc-staging@vps.suttacentral.net', [
        'source $HOME/.virtualenvs/suttacentral/bin/activate',
        'cd $HOME/suttacentral',
        _branch_or_pull(branch),
        'cd text',
        'git pull',
        'cd ..',
        'pip install -q -r requirements.txt',
        'invoke assets.compile',
        'sudo supervisorctl restart sc-staging',
        'invoke assets.clean --older',
    ])
