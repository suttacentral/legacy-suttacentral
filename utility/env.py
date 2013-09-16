# Setup sys.path to import modules from the main python directory.

from os.path import dirname, join, realpath
import sys

sys.path.insert(1, join(dirname(dirname(realpath(__file__))), 'python'))
