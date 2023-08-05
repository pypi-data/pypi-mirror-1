from os import path

import cherrypy
from cherrypy.lib.filter.basefilter import BaseFilter
import pkg_resources

available_engines = {}

def cherrypy_vars():
    return {'cherrypy':cherrypy}

for entry_point in pkg_resources.iter_entry_points('python.templating.engines'):
    Engine = entry_point.load()
    available_engines[entry_point.name] = Engine

def using_template(template_name):
    def wrapper(f):
        def inner(*args, **params):
            return (template_name, f(*args, **params))
        return inner
    return wrapper

def _requires_template(body):
    if isinstance(body, tuple):
        if len(body) == 2:
            if isinstance(body[0], str):
                if isinstance(body[1], dict):
                    return True
    return False

class TemplateFilter(BaseFilter):
    def __init__(self, engine_name, template_root=None):
        if template_root:
            self.template_root = template_root
        else:
            self.template_root = '.'
	config_section = engine_name + '_settings'
	engine_opts = cherrypy.config.configMap.get(config_section, {})
	Engine = available_engines.get(engine_name, None)
        if not Engine:
            raise TemplateEngineMissing('Please install a plugin for "%s" to use its functionality' % engine_name)
        self.engine = Engine(cherrypy_vars, engine_opts)
        
    def beforeFinalize(self):
        body = cherrypy.response.body
        if _requires_template(body):
            template_path, vars = body
            base_path_parts = self.template_root.split('/')
            tmpl_path_parts = template_path.split('/')
            full_path = path.join(*(base_path_parts + tmpl_path_parts))
            # at this point, python.templating.engines plugins require a dotted
            # path to the template - blame TurboGears ;-)
            dotted_path = full_path.replace(path.sep, '.')
            dotted_path = dotted_path.lstrip('.')
            page_data = self.engine.render(vars, template=dotted_path)
            cherrypy.response.body = page_data.splitlines()
        return

class TemplateEngineMissing(Exception):
    pass

