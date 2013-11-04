# Setup sys.path to import modules from the project directory.

from os.path import dirname, join, realpath
import sys

sys.path.insert(1, join(dirname(dirname(dirname(realpath(__file__)))), 'src'))
