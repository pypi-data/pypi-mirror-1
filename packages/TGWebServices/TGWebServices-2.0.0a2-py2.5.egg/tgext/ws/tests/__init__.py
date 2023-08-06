import os.path

from tg import config
from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand

from tg.configuration import AppConfig

from routes import Mapper

import tgext
from tgext.ws import xml_, json

from webtest import TestApp

class lib(object):
    class app_globals(object):
        class Globals(object):
            pass
    class helpers(object):
        pass

class TestConfig(AppConfig):
    def __init__(self):
        import tgext.ws.tests
        super(TestConfig, self).__init__()
        self.renderers = []
        self.package = tgext.ws.tests
        self.default_renderer = 'genshi'
        self.renderers.append('genshi')

        self.use_sqlalchemy = False
        self.render_functions['wsautoxml'] = xml_.render_autoxml
        self.render_functions['wsautojson'] = json.render_autojson

    def setup_paths(self):
        super(TestConfig, self).setup_paths()
        self.paths['controllers'] = os.path.join(self.paths['root'], 'fixtures')

def app_factory(global_conf, full_stack=True, **app_conf):
    print global_conf, app_conf

    app_config = TestConfig()
    app_config.use_sqlalchemy = False

    load_environment = app_config.make_load_environment()
    make_base_app = app_config.setup_tg_wsgi_app(load_environment)

    app = make_base_app(global_conf, full_stack=True, **app_conf)
    return app
    
class TestController(object):
    def setUp(self):
        wsgiapp = loadapp('config:test.ini#main', relative_to='.')
        self.app = TestApp(wsgiapp)

