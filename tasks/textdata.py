"""Tasks related to the TextDataModel (TIM).

Both refresh(force=True) and rebuild() will re-index every single file,
the difference between them is that rebuild will start with a fresh
database, and refresh will use the existing database. Because of how
SQLite connections work rebuild() requires the server to be restarted
and refresh does not.

Use refresh unless there have been schema changes or database corruption.

"""

from tasks.helpers import *

@task
def refresh(force=False):
    """Ensure TIM is up-to-date."""
    blurb(refresh)
    from sc import textdata
    tim = textdata.tim()


@task
def rebuild():
    """ Perform complete rebuild """
    # This is useful after changes to TextData that require every
    # entry be updated.
    blurb(rebuild)
    from sc import textdata
    tim = textdata.rebuild_tim()
