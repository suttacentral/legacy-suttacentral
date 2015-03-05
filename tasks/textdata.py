from tasks.helpers import *

@task
def rebuild():
    """ Perform complete rebuild """
    # This is useful after changes to TextData that require every
    # entry be updated.
    blurb(rebuild)
    from sc import textdata
    tim = textdata.rebuild_tim()

@task
def deletelang(lang):
    from sc import textdata
    tim = textdata.SqliteBackedTIM()
    con = tim._con
    count = con.execute('SELECT COUNT(lang) FROM data WHERE lang = ?', (lang,)).fetchone()[0]
    notice('Removing {} enties from database'.format(count))
    con.execute('DELETE FROM data WHERE lang = ?', (lang,))
    con.execute('DELETE FROM mtimes WHERE path LIKE ?', ('{}%'.format(lang), ))
    con.commit()
    notice('Done')
    
@task
def update_cmdate():
    "Updating creation and modification dates database"
    from sc import textdata
    tim = textdate.tim_no_update()
    tim.update_cmdate()
