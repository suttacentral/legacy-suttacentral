import babel.dates
import errno
import fcntl
import os
import pathlib
import textwrap
import time
from contextlib import contextmanager
from datetime import datetime

from sc import config

@contextmanager
def filelock(path, block=True):
    """A simple, file-based exclusive-lock pattern.

    Blocking Example:
        >>> with filelock('mylock'):
        >>>     print('Lock acquired.')

    Non-blocking Example:
        >>> with filelock('mylock', block=False) as acquired:
        >>>     if acquired:
        >>>         print('Sweet! Lock acquired.')
        >>>     else:
        >>>         print('Bummer. Could not acquire lock.')
    """
    path = pathlib.Path(path)
    with path.open('w') as f:
        operation = fcntl.LOCK_EX
        if not block:
            operation |= fcntl.LOCK_NB
        try:
            fcntl.flock(f, operation)
            acquired = True
        except OSError as e:
            if e.errno == errno.EACCES or e.errno == errno.EAGAIN:
                acquired = False
            else:
                raise
        yield acquired

def format_date(value, format='short', locale=config.default_locale):
    return babel.dates.format_date(value, format=format, locale=locale)

def format_datetime(value, format='short', locale=config.default_locale):
    rfc3339 = format == 'rfc3339'
    if rfc3339:
        format = 'yyyy-MM-ddTHH:mm:ssZ'
    datetime = babel.dates.format_datetime(value, format=format, locale=locale)
    if rfc3339:
        datetime = datetime[:-2] + ':' + datetime[-2:]
    return datetime

def format_time(value, format='short', locale=config.default_locale):
    return babel.dates.format_time(value, format=format, locale=locale)

def format_timedelta(value, locale=config.default_locale):
    delta = datetime.now() - value
    return babel.dates.format_timedelta(delta, locale=locale)

def wrap(text, width=80, indent=0):
    """Returns text wrapped and indented."""
    text = '\n'.join([
        textwrap.fill(line, width - indent, break_long_words=False,
            break_on_hyphens=False) for line in text.splitlines()
    ])
    return textwrap.indent(text.strip(), ' ' * indent)
