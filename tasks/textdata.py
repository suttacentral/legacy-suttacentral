from tasks.helpers import *

@task
def ensure_up_to_date():
    """ Ensure the TextInfoModel is up to date """
    blurb(ensure_up_to_date)
    import sc.textdata
    sc.textdata.ensure_up_to_date()

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
