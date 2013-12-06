"""Task helpers."""

import colorama
import os
import os.path
import sys
from invoke import task

root_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(
    __file__))))

def notice(string):
    """Print string in blue."""
    color_print(string, colorama.Fore.BLUE)

def color_print(string, color):
    """Print string in color."""
    print(color, end='')
    print(string, end='')
    print(colorama.Fore.RESET)
    sys.stdout.flush()

def remote_run(login, commands):
    """Print string in blue."""
    remote_command = ' && '.join(commands)
    command = "ssh {} '{}'".format(login, remote_command)
    run(command)

def rm_rf(*files):
    """Recursively remove files."""
    run('rm -rf {}'.format(' '.join(files)))

def run(command):
    """Runs command in a subprocess."""
    notice(command)
    os.system(command)

def run_sc(statement):
    """Run a core SuttaCentral method in src.

    Example:
        run_sc('assets.compile()')

    """
    module = statement.split('.')[0]
    code = 'import {}; {}'.format(module, statement)
    run('cd src && python -c \'{}\''.format(code))

def warning(string):
    """Print string in red."""
    color_print(string, colorama.Fore.RED)
