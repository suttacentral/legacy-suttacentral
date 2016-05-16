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
    remote_run('sc-staging@vps.suttacentral.net', [
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
def full():
    """Deploy to the staging server."""
    blurb(full)
    _staging_run(
        'touch tmp/maintenance',
        'git pull',
        'cd data',
        'git pull',
        'cd ..',
        'pip install -q -r requirements.txt',
        'invoke jsdata.build',
        'invoke assets.compile --precompress',
        'invoke textdata.ensure_loads',
        'sudo supervisorctl restart sc-staging',
        'invoke assets.clean --older'
    )

@task
def quick():
    """Deploy simple changes to the staging server."""
    blurb(quick)
    _staging_run(
        'git pull',
        'cd data',
        'git pull',
        'cd ..',
        'echo "Requesting the server reload assets"',
        'curl -s -XPOST "http://localhost:8087/admin/reload" -d "{}"',
        'invoke assets.clean --older'
    )

@task
def push_fonts(delete=False):
    """Copy local fonts to the staging server."""
    blurb(push_fonts)
    run('rsync -avz ' +
        '--exclude="compiled" ' +
        '--include="*.woff" --include="*.woff2" --include="*.ttf" --include="*.otf" --include="nonfree"' +
        '--exclude="*" ' +
        ('--delete ' if delete else '') +
        'static/fonts/ ' +
        'sc-staging@vps.suttacentral.net:' +
        '/home/sc-staging/suttacentral/static/fonts/', fg=True)

@task
def pull_fonts(delete=False):
    """Copy fonts from the staging server to local"""
    blurb(pull_fonts)
    run('rsync -avz ' +
        '--exclude="compiled" ' +
        '--include="*.woff" --include="*.woff2" --include="*.ttf" --include="*.otf" --include="nonfree"' +
        '--exclude="*" ' +
        ('--delete ' if delete else '') +
        'sc-staging@vps.suttacentral.net:' + 
        '/home/sc-staging/suttacentral/static/fonts/' +
        'static/fonts/ '
        , fg=True)
        
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
