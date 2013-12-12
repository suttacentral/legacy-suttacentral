import datetime
import pathlib
from plumbum.commands.processes import ProcessExecutionError
from unittest.mock import MagicMock

from ..helper import SCTestCase

from scm import Scm

def test_revision():
    scm = Scm('/foo')
    scm._git = MagicMock(return_value='0101beef')
    assert scm.revision == '0101beef'

def test_datetime():
    scm = Scm('/foo')
    scm._git = MagicMock(return_value='1386816309')
    assert scm.datetime == datetime.datetime(2013, 12, 12, 2, 45, 9)

def test_branch():
    scm = Scm('/foo')
    scm._git = MagicMock(return_value='master')
    assert scm.branch == 'master'

def test_some_tag():
    scm = Scm('/foo')
    scm._git = MagicMock(return_value='v1.2')
    assert scm.tag == 'v1.2'

def test_no_tag():
    scm = Scm('/foo')
    scm._git = MagicMock(side_effect=ProcessExecutionError([], 1, '!', '!'))
    assert scm.tag == None
