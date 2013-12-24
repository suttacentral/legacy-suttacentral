import datetime
import pathlib
from plumbum.commands.processes import ProcessExecutionError
from unittest.mock import MagicMock

from sc.scm import Scm

from tests.helper import SCTestCase

def setup_last_commit_scm():
    scm = Scm('/foo')
    git_result = '0101beef\n1386816309\nJohn Doe\nFix bugs'
    scm._git = MagicMock(return_value=git_result)
    return scm

def test_last_commit_revision():
    scm = setup_last_commit_scm()
    assert scm.last_commit_revision == '0101beef'

def test_last_commit_time():
    scm = setup_last_commit_scm()
    assert scm.last_commit_time == datetime.datetime(2013, 12, 12, 2, 45, 9)

def test_last_commit_author():
    scm = setup_last_commit_scm()
    assert scm.last_commit_author == 'John Doe'

def test_last_commit_subject():
    scm = setup_last_commit_scm()
    assert scm.last_commit_subject == 'Fix bugs'

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
