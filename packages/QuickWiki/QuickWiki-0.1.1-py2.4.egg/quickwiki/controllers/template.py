from quickwiki.lib.base import *

class TemplateController(BaseController):
    def view(self, url):
        """
        This is the last place which is tried during a request to try to find a 
        file to serve. It could be used for example to display a template::
        
            def view(self, url):
                return render_response(url+'.myt')
        
        The default is just to abort the request with a 404 File not found
        status message.
        """
        abort(404)
