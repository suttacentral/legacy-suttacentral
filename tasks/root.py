"""Common tasks."""

import os

import sc
from sc import config

import tasks
from tasks.helpers import *


@task
def clean(ctx, aggressive=False):
    """Remove unnecessary files."""
    tasks.log.clean(ctx)
    tasks.tmp.clean(ctx)
    if aggressive:
        tasks.assets.clean(ctx, older=False)
        tasks.dictionary.clean(ctx)
        tasks.exports.offline.clean(ctx, older=False)
        tasks.search.clean(ctx)
        for file in sc.db_dir.glob('*'):
            if not file.isdir():
                file.unlink()
    else:
        tasks.assets.clean(ctx, older=True)
        tasks.exports.offline.clean(ctx, older=True)


@task
def reset(ctx):
    """Reset the environment."""
    blurb(reset)
    clean(ctx, aggressive=True)
    update_data(ctx)
    tasks.dictionary.build(ctx)
    tasks.search.index(ctx)

@task
def server(ctx, v=False):
    """Run the server."""
    blurb(server)
    if config.newrelic_license_key:
        tasks.newrelic.update_ini(ctx)
        os.environ['NEW_RELIC_ENVIRONMENT'] = config.newrelic_environment
        os.environ['NEW_RELIC_CONFIG_FILE'] = str(sc.base_dir / 'newrelic.ini')
        os.execlp('newrelic-admin', 'newrelic-admin', 'run-program', 'cherryd',
                  '-i', 'sc.server')
    else:
        os.execlp('cherryd', 'cherryd', '-i', 'sc.server')

@task
def elastic_indexer(ctx):
    """Run the Elasticsearch Indexer Daemon """
    blurb(elastic_indexer)
    import sc.search.updater
    sc.search.updater.start()

@task
def test_server(ctx):
    """Run test server to validate code."""
    blurb(test_server)
    os.execlp('cherryd', 'cherryd', '-i', 'sc.test_server')

@task
def update_data(ctx):
    """Update the data repository."""
    blurb(update_data)
    with local.cwd(sc.data_dir):
        run('git pull')
