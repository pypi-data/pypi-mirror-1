import os
from paste.deploy import loadapp, appconfig
from paste.fixture import TestApp

base_dir = os.path.dirname(os.path.dirname(__file__))
doc_dir = os.path.join(base_dir, 'docs')
config_uri = 'config:devel_config.ini#test'

def setup_module(mod):
    mod.wsgiapp = get_wsgi_app()
    mod.app = TestApp(mod.wsgiapp)
    mod.config = get_config()
    
def get_wsgi_app():
    return loadapp(config_uri, relative_to=doc_dir)
    
def get_config():
    return appconfig(config_uri, relative_to=doc_dir)
