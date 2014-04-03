"""Deploy to production server tasks."""

from tasks.helpers import *


def _production_run(*commands):
    remote_run('sc-production@vps.suttacentral.net', [
        'source $HOME/.virtualenvs/suttacentral/bin/activate',
        'cd $HOME/suttacentral',
    ] + list(commands))


@task
def full():
    """Deploy to the production server."""
    blurb(full)
    _production_run(
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
        'invoke assets.clean --older'
    )


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
    _production_run(
        'git pull',
        'pip install -q -r requirements.txt',
        'invoke assets.compile',
        #'invoke textdata.refresh',
        'sudo supervisorctl restart sc-production',
        'invoke assets.clean --older'
    )


@task
def update_data():
    """Deploy data changes to the production server."""
    blurb(update_data)
    _production_run(
        'cd data',
        'git pull'
    )


@task
def update_search():
    """Update dictionary and search index on the production server."""
    blurb(update_search)
    _production_run(
        'invoke dictionary.build',
        'invoke search.index'
    )
