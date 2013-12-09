"""Test tasks."""

from .helpers import *

def _run_tests(tests, url=None, phantomjs=False):
    environ = {}
    if url:
        environ['URL'] = self.url
    if phantomjs:
        environ['PHANTOMJS'] = '1'
    with local.env(**environ):
        run('py.test {}'.format(tests), fg=True)

@task
@blurb
def all(url=None, phantomjs=False):
    """Run all tests in the test suite."""
    _run_tests('tests', url=url, phantomjs=phantomjs)

@task
@blurb
def functional(url=None, phantomjs=False):
    """Run the functional test suite."""
    _run_tests('tests/functional', url=url, phantomjs=phantomjs)

@task
@blurb
def unit():
    """Run the unit test suite."""
    _run_tests('tests/unit')
