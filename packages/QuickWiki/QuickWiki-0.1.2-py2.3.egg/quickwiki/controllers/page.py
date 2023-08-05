from quickwiki.lib.base import *
from quickwiki.lib.database import session_context

class PageController(BaseController):
    def index(self, title):
        page = self.query.get_by(title=title)
        if page: 
            c.content = page.get_wiki_content()
            return render_response('/page.myt')
        elif model.wikiwords.match(title):
            return render_response('/new_page.myt')
        abort(404)
        
    def __before__(self):
        self.session = session_context.current
        self.query = self.session.query(model.Page)
        
    def edit(self, title):
        page = self.query.get_by(title=title)
        if page:
            c.content = page.content
        return render_response('/edit.myt')
        
    def save(self, title):
        page = self.query.get_by(title=title)
        if not page:
            page = model.Page()
            self.session.save(page)
            page.title = title
        page.content = request.params['content']
        c.title = page.title
        c.content = page.get_wiki_content()
        c.message = 'Successfully saved'
        self.session.flush()
        return render_response('/page.myt')

    def list(self):
        c.titles = [page.title for page in self.query.select()]
        return render_response('/titles.myt')
        
    def delete(self):
        title = request.params['id'][5:]
        page = self.query.get_by(title=title)
        self.session.delete(page)
        self.session.flush()
        c.titles = self.query.select()
        return render_response('/list.myt', fragment=True)