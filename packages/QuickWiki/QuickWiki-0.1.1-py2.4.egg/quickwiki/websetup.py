import sqlalchemy.mods.threadlocal
from sqlalchemy import *
from quickwiki.models import *
from paste.deploy import appconfig

def setup_config(command, filename, section, vars):
    app_conf = appconfig('config:'+filename)
    print "Connecting to database %s"%app_conf['dsn']
    meta.connect(app_conf['dsn'])
    print "Creating tables"
    meta.create_all()
    print "Adding front page data"
    page = Page()
    page.title = 'FrontPage'
    page.content = 'Welcome to the QuickWiki front page.'
    objectstore.flush()
    print "Successfully setup."