from tasks.helpers import *

@task
def rebuild():
    """ Perform complete rebuild """
    # This is useful after changes to TextData that require every
    # entry be updated.
    blurb(rebuild)
    from sc import textdata
    tim = textdata.rebuild_tim()
