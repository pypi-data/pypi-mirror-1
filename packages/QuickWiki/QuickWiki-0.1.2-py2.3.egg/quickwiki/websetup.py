from sqlalchemy import *
from quickwiki.models import *
from paste.deploy import appconfig

def setup_config(command, filename, section, vars):

    app_conf = appconfig('config:'+filename)
    if not app_conf.has_key('sqlalchemy.dburi'):
        raise KeyError("No sqlalchemy database config found!")
    print "Connecting to database %s..."%repr(app_conf['sqlalchemy.dburi'])
    conn = meta.connect(app_conf['sqlalchemy.dburi'])
    
    print "Creating tables"
    meta.create_all()
    session = create_session()
    
    print "Adding front page data"
    page = Page()
    page.title = 'FrontPage'
    page.content = 'Welcome to the QuickWiki front page.'
    session.save(page)
    session.flush()
    
    print "Successfully setup"