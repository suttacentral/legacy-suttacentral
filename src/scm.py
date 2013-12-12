"""Git repository information.

Example:
    >>> from scm import scm
    >>> scm.revision
    '01798b77bdb2cb88e5996828662d1d8ebca0d9c2'
    >>> scm.datetime
    datetime.datetime(2013, 12, 11, 18, 45, 9)
    >>> scm.branch
    'master'
    >>> scm.tag
    >>>
"""

import pathlib
import plumbum
import time
from datetime import datetime as _datetime
from plumbum.commands.processes import ProcessExecutionError

import config

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
    @_cached
    def revision(self):
        """Return the revision of last commit."""
        return self._git('log', '-1', '--format=%H')

    @property
    @_cached
    def datetime(self):
        """Return the datetime of last commit."""
        time = int(self._git('log', '-1', '--format=%at'))
        return _datetime.fromtimestamp(time)

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

    def _git(self, *args):
        with plumbum.local.cwd(self.dir):
            return plumbum.local['git'](*args).strip()

_timeout = 10 if config['global']['engine.autoreload.on'] else None
scm = Scm(config.base_dir, _timeout)
