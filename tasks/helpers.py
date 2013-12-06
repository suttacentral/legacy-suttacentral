"""Task helpers."""

import colorama
import os
import os.path
from invoke import task

root_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(
    __file__))))

def rm_rf(*files):
    """Recursively remove files."""
    run('rm -rf {}'.format(' '.join(files)))

def run_sc(statement):
    """Run a core SuttaCentral method in src.

    Example:
        run_sc('assets.compile()')

    """
    module = statement.split('.')[0]
    code = 'import {}; {}'.format(module, statement)
    run('cd src && python -c \'{}\''.format(code))

def run(command):
    print(colorama.Fore.BLUE, end='')
    print(command, end='')
    print(colorama.Fore.RESET)
    os.system(command)
