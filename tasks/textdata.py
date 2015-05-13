from tasks.helpers import *

@task
def rebuild():
    """ Rebuild Text Info Model without causing downtime """
    # This is useful after changes to TextData that require every
    # entry be updated.
    blurb(rebuild)
    import sc.textdata
    tim = sc.textdata.tim_no_update()
    tim.build(force=True)

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
def ensure_loads():
    "Updating creation and modification dates database"
    from sc import textdata
    textdata.tim_manager.load(quick=False)
