import plumbum
import config

def git(*args):
    with plumbum.local.cwd(config.base_dir):
        return plumbum.local['git'](*args).strip()

def get_revision():
    return git('log', '-1', '--format=%H')

def get_timestamp():
    return int(git('log', '-1', '--format=%at'))

def get_branch():
    return git('rev-parse', '--abbrev-ref', 'HEAD')

def get_tag():
    try:
        return git('describe', '--abbrev=0', '--tags')
    except plumbum.commands.processes.ProcessExecutionError as e:
        return None

def refresh():
    global revision, timestamp, branch, tag
    revision = get_revision()
    timestamp = get_timestamp()
    branch = get_branch()
    tag = get_tag()

refresh()
