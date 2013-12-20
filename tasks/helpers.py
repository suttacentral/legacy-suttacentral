"""Task helpers."""

import colorama
import plumbum.commands
import regex
import sys
from invoke import task
from plumbum import local

from sc import config, util

_PP_HINTS = {
    'Compile': 'Compiling',
    'Create': 'Creating',
    'Delete': 'Deleting',
    'Drop': 'Dropping',
    'Prepare': 'Preparing',
    'Reset': 'Resetting',
    'Run': 'Running',
    'Setup': 'Setting up',
    'Stop': 'Stopping',
    'Update': 'Updating',
}

def _color_print(string, color):
    """Print string in color."""
    print(color, end='')
    print(string, end='')
    print(colorama.Fore.RESET)
    sys.stdout.flush()

def blurb(function):
    """Print the function's docstring in present participle tense."""
    text = function.__doc__
    first, rest = text.split(' ', 1)
    first = _PP_HINTS.get(first, first + 'ing')
    notice('{} {}..'.format(first, rest))

def notice(string):
    """Print string in blue."""
    _color_print(string, colorama.Fore.BLUE)

def remote_run(login, commands):
    """Print string in blue."""
    remote_command = ' && '.join(commands)
    command = "ssh {} '{}'".format(login, remote_command)
    run(command, echo=True, fg=True)

def rm_rf(*files):
    """Recursively remove files."""
    run('rm -rf {}'.format(' '.join(map(str, files))))

def run(command, echo=False, fg=False):
    """Runs command in a subprocess.

    If echo is True, then the command is echoed to screen.
    If fg is True, then command is run in the foreground.
    """
    if not isinstance(command, plumbum.commands.BaseCommand):
        command = local['bash']['-c', str(command)]

    # Code to deal with a bug in plumbum's str(command)...
    def flatten_list(lst):
        result = []
        for el in lst:
            if isinstance(el, (list, tuple)):
                result += flatten_list(el)
            else:
                result.append(el)
        return result
    command_string = ' '.join(flatten_list(command.formulate()))
    if echo:
        notice('Command:')
        notice(util.wrap(command_string, indent=4))
    kwargs = {'retcode': None}
    if fg:
        kwargs.update(stdin=None, stdout=None, stderr=None)
    retcode, stdout, stderr = command.run(**kwargs)
    if not echo and (stderr or retcode != 0):
        warning('Command:')
        warning(util.wrap(command_string, indent=4))
    if stderr:
        warning('Stderr:')
        warning(util.wrap(stderr, indent=4))
    if retcode != 0:
        warning('Command exited with return code {}'.format(retcode))
        warning('Exiting...')
        sys.exit(retcode)

def run_src(statement, **kwargs):
    """Runs Python statement in the src directory."""
    command = local['python']['-c', statement]
    with local.cwd(local.cwd / 'src'):
        run(command, **kwargs)

def warning(string):
    """Print string in red."""
    _color_print(string, colorama.Fore.RED)
