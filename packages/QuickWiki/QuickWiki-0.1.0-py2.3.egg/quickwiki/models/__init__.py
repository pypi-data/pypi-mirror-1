from pylons import h
import re
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")
from docutils.core import publish_parts
    
import sqlalchemy.mods.threadlocal
from sqlalchemy import *

meta = DynamicMetaData()

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
        titles = wikiwords.findall(content)
        if titles:
            for title in titles:
                content = content.replace(
                    title, 
                    h.link_to(
                        title, 
                        h.url_for(
                            controller='page',
                            action='index', 
                            title=title
                        ),
                    ),
                )
        return content
        
page_mapper = mapper(Page, pages_table)