"""Deploy to staging server tasks."""

from tasks.helpers import *


def _branch_or_pull(branch):
    if branch:
        return ('git fetch && ' +
                'git checkout {0} || git checkout -t origin/{0} && ' +
                'git pull').format(branch)
    else:
        return 'git pull'


def _staging_run(*commands):
    remote_run('sc-staging@linode.suttacentral.net', [
        'source $HOME/.pyenv/versions/suttacentral/bin/activate',
        'cd $HOME/suttacentral',
    ] + list(commands))


@task
def checkout_branch(code=None, data=None):
    "Check out specified branch"
    blurb(checkout_branch)
    commands = []
    if code:
        commands.append('git fetch && ' +
            'git checkout {0} || git checkout -t origin/{0}'.format(code))
    if data:
        commands.append('cd data')
        commands.append('git fetch && ' +
            'git checkout {0} || git checkout -t origin/{0}'.format(data))
    _staging_run(*commands)
        

@task
def full(branch=None):
    """Deploy to the staging server."""
    blurb(full)
    _staging_run(
        'touch tmp/maintenance',
        'sudo supervisorctl stop sc-staging',
        'git pull',
        'cd data',
        'git pull',
        'cd ..',
        'pip install -q -r requirements.txt',
        'invoke clean --aggressive',
        'invoke jsdata.build',
        'invoke assets.compile --precompress',
        'invoke textdata.ensure_loads',
        'sudo supervisorctl start sc-staging',
        'rm -f tmp/maintenance',
        'invoke dictionary.build',
        'invoke search.index'
    )


@task
def nonfree_fonts():
    """Copy local nonfree fonts to the staging server."""
    blurb(nonfree_fonts)
    run('rsync -avz ' +
        'static/fonts/nonfree/ ' +
        'sc-staging@vps.suttacentral.net:' +
        '/home/sc-staging/suttacentral/static/fonts/nonfree/', fg=True)


@task
def quick(branch=None):
    """Deploy simple changes to the staging server."""
    blurb(quick)
    _staging_run(
        'git pull',
        'cd data',
        'git pull',
        'cd ..',
        'pip install -q -r requirements.txt',
        'invoke assets.compile --precompress',
        'invoke textdata.ensure_loads',
        'sudo supervisorctl restart sc-staging',
        'invoke assets.clean --older'
    )

@task
def rebuild_tim():
    """ Rebuild TIM on the staging server """
    _staging_run(
        'invoke textdata.rebuild',
    )
    

@task
def update_data(branch=None):
    """Deploy data changes to the staging server."""
    blurb(update_data)
    _staging_run(
        'cd data',
        _branch_or_pull(branch)
    )


@task
def nuke_search():
    """Update dictionary and search index on the staging server."""
    blurb(update_search)
    _staging_run(
        'invoke search.delete'
    )
