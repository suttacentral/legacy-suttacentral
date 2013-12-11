import babel.dates
import os
import plumbum
import plumbum.commands
import tempfile
import textwrap
import time

import config

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

def wrap(text, width=80, indent=0):
    """Returns text wrapped and indented."""
    text = '\n'.join([
        textwrap.fill(line, width - indent, break_long_words=False,
            break_on_hyphens=False) for line in text.splitlines()
    ])
    return textwrap.indent(text.strip(), ' ' * indent)

def mysql(sql, host=None, port=None, user=None, password=None, db=None,
               runner=None):
    """A convinience wrapper for the mysql command line utility.

    For security, this function uses a temporary file instead of specifying the
    password as an argument.

    The sql argument can be a string or a plumbum command.

    If runner is specified, this function will pass runner the mysql plumbum
    command and return the results of runner.

    Otherwise, this function will return a tuple (retcode, stdout, stderr).
    """
    args = []
    try:
        if password is not None:
            tf = tempfile.NamedTemporaryFile(delete = False)
            my_cnf = '[client]\npassword="{}"\n'.format(password)
            tf.write(bytes(my_cnf, 'UTF-8'))
            tf.close()
            args += ['--defaults-file={}'.format(tf.name)]
        else:
            args += ['-p']
        if user:
            args += ['-u', user]
        if host:
            args += ['-h', host]
        if port:
            args += ['-P', str(port)]
        if db:
            args.append(db)
        command = plumbum.local['mysql'][tuple(args)]
        if isinstance(sql, plumbum.commands.BaseCommand):
            command = sql | command
        else:
            command = command << sql
        if runner:
            return runner(command)
        else:
            return command.run(retcode=None)
    finally:
        if password is not None:
            os.unlink(tf.name)

def set_timezone(tz=None):
    if not tz:
        tz = config.timezone
    os.environ['TZ'] = tz
    time.tzset()
