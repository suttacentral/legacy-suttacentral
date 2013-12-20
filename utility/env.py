# Setup sys.path to import modules from the project directory.

from pathlib import Path
import sys

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
