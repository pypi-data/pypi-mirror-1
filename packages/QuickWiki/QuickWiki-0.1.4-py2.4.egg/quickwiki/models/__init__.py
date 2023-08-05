
import re
import sets
import quickwiki.lib.helpers as h
from docutils.core import publish_parts

wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

from sqlalchemy import *
from sqlalchemy.ext.assignmapper import assign_mapper
from pylons.database import create_engine
from pylons.database import session_context as ctx

meta = MetaData()

pages_table = Table('pages', meta,
    Column('title', String(40), primary_key=True),
    Column('content', String(), default='')
)

class Page(object):
    content = None

    def __str__(self):
        return self.title

    def get_wiki_content(self):
        content = publish_parts(self.content, writer_name="html")["html_body"]
        titles = sets.Set(wikiwords.findall(content))
        for title in titles:
            title_url = h.url_for(controller='page', action='index', 
                                  title=title)
            content = content.replace(title, h.link_to(title, title_url))
        return content
        
            
page_mapper = assign_mapper(ctx, Page, pages_table)
