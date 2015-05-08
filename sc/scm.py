"""Git repository information.

Example:
    >>> from scm import scm
    >>> scm.last_revision
    '01798b77bdb2cb88e5996828662d1d8ebca0d9c2'
    >>> scm.last_commit_time
    datetime.datetime(2013, 12, 11, 18, 45, 9)
    >>> scm.last_commit_author
    'John Doe'
    >>> scm.last_commit_subject
    'Fix bugs'
    >>> scm.branch
    'master'
    >>> scm.tag
    >>>
"""

import pathlib
import plumbum
import time
from datetime import datetime
from plumbum.commands.processes import ProcessExecutionError

import sc
from sc import config

def _cached(function):
    key = function.__name__
    time_key = key + '_time'
    def wrapper(self):
        if key in self._cache and \
                (self.timeout is None or
                 self._cache.get(time_key, 0) > time.time() - self.timeout):
            value = self._cache[key]
        else:
            value = self._cache[key] = function(self)
            self._cache[time_key] = time.time()
        return value
    return wrapper

class Scm(object):
    """Git repository information."""

    def __init__(self, dir, timeout=10):
        self.dir = pathlib.Path(dir)
        self.timeout = timeout
        self.refresh()

    @property
    def last_commit_revision(self):
        """Return the revision of last commit."""
        return self._last_commit_info['revision']

    @property
    def last_commit_time(self):
        """Return the time of last commit."""
        return self._last_commit_info['time']

    @property
    def last_commit_author(self):
        """Return the author of last commit."""
        return self._last_commit_info['author']

    @property
    def last_commit_subject(self):
        """Return the subject (short message) of last commit."""
        return self._last_commit_info['subject']

    @property
    @_cached
    def branch(self):
        """Return the current branch."""
        return self._git('rev-parse', '--abbrev-ref', 'HEAD')

    @property
    @_cached
    def tag(self):
        """Return a tag for this revision or None."""
        try:
            return self._git('describe', '--abbrev=0', '--tags')
        except ProcessExecutionError as e:
            return None

    def refresh(self):
        """Clear the cache."""
        self._cache = {}

    @property
    @_cached
    def _last_commit_info(self):
        info = self._git('log', '-1', '--format=%H%n%at%n%an%n%s')
        revision, time, author, subject = info.split('\n', 3)
        return {
            'revision': revision,
            'time': datetime.fromtimestamp(int(time)),
            'author': author,
            'subject': subject,
        }
    
    def checkout(self, commit_id):
        self._git('checkout', commit_id)        

    def _git(self, *args):
        with plumbum.local.cwd(self.dir):
            return plumbum.local['git'](*args).strip()

_timeout = 120 if config['global']['engine.autoreload.on'] else 10
scm = Scm(sc.base_dir, _timeout)
data_scm = Scm(sc.data_dir, 1)
