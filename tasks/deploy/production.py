"""Deploy to production server tasks."""

from ..helpers import *

@task
def full():
    """Deploy to the production server."""
    blurb(full)
    remote_run('sc-production@vps.suttacentral.net', [
        'source $HOME/.virtualenvs/suttacentral/bin/activate',
        'cd $HOME/suttacentral',
        'touch tmp/maintenance',
        'sudo supervisorctl stop sc-production',
        'git pull',
        'cd data',
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
def nonfree_fonts(force=False):
    """Copy local nonfree fonts to the production server."""
    blurb(nonfree_fonts)
    command = 'rsync -avz ' + \
        'static/fonts/nonfree/ ' + \
        'sc-production@vps.suttacentral.net:' + \
        '/home/sc-production/suttacentral/static/fonts/nonfree/'
    if not force:
        warning('*** Dry run...use the --force flag to make changes ***')
        command = command.replace('rsync', 'rsync -n')
    run(command, fg=True)

@task
def quick():
    """Deploy simple changes to the production server."""
    blurb(quick)
    remote_run('sc-production@vps.suttacentral.net', [
        'source $HOME/.virtualenvs/suttacentral/bin/activate',
        'cd $HOME/suttacentral',
        'git pull',
        'cd data',
        'git pull',
        'cd ..',
        'pip install -q -r requirements.txt',
        'invoke assets.compile',
        'sudo supervisorctl restart sc-production',
        'invoke assets.clean --older',
    ])

@task
def data():
    """Deploy data changes to the production server."""
    blurb(data)
    remote_run('sc-production@vps.suttacentral.net', [
        'source $HOME/.virtualenvs/suttacentral/bin/activate',
        'cd $HOME/suttacentral',
        'cd data',
        'git pull',
        'cd ..',
        'invoke search.index',
    ])
