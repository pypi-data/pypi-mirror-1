"""
Setup your Routes options here
"""
import os
from routes import Mapper

def make_map(global_conf={}, app_conf={}):
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    map = Mapper(directory=os.path.join(root_path, 'controllers'))
    
    map.connect('/error/:action/:id', controller='error')
    map.connect(':controller/:action/:title', controller='page', action='index', title='FrontPage')
    map.connect(':title', controller='page', action='index', title='FrontPage')
    map.connect('*url', controller='template', action='view')

    return map
