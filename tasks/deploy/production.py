"""Deploy to production server tasks."""

from tasks.helpers import *


def _production_run(*commands):
    remote_run('sc-production@vps.suttacentral.net', [
        'source $HOME/.pyenv/versions/suttacentral/bin/activate',
        'cd $HOME/suttacentral',
    ] + list(commands))

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
        'cd data',
        'git pull',
        'cd ..',
        'echo "Requesting the server reload assets"',
        'curl -s -XPOST "http://localhost:8086/admin/reload" -d "{}"',
        'invoke assets.clean --older'
    )

@task
def full(branch=None):
    """Deploy to the staging server."""
    blurb(full)
    _production_run(
        'git pull',
        'cd data',
        'git pull',
        'cd ..',
        'pip install -q -r requirements.txt',
        'invoke jsdata.build',
        'invoke assets.compile --precompress',
        'invoke textdata.ensure_loads',
        'sudo supervisorctl restart sc-production',
        'invoke assets.clean --older'
    )

@task
def test():
    _production_run(
        'git pull',
        'cd data',
        'git pull',
        'cd ..',
        'pip install -q -r requirements.txt',
        'invoke jsdata.build --minify',
        'invoke assets.compile --precompress',
        'invoke textdata.ensure_loads',
        'invoke test_server'
    )

@task
def rebuild_tim():
    """ Rebuild TIM on the production server """
    blurb(rebuild_tim)
    _production_run(
        'invoke textdata.rebuild',
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

@task
def elastic_restart():
    """Restart elasticsearch service"""
    blurb(elastic_restart)
    _production_run(
        'sudo service elasticsearch restart'
    )

@task
def elastic_nuke():
    """Nuke elasticsearch search indexes"""
    blurb(elastic_nuke)
    _production_run(
        "curl -s -XDELETE 'http://localhost:9200/_all'",
        'sleep 5',
        'curl -s -XPOST "http://localhost:8086/admin/reload" -d "{}"'
        )
    
