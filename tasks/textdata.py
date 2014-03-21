"""Tasks related to the TextDataModel (TIM)."""

from tasks.helpers import *

@task
def refresh():
    """Ensure TIM is up-to-date."""
    blurb(refresh)
    from sc import textdata
    tim = textdata.tim()
