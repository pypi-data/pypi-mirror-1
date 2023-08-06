from xml.sax.saxutils import XMLGenerator
try:
    import cStringIO as stringio
except:
    import StringIO as stringio

import os.path as op

from curtain import Template, Location
from repoze.bfg.settings import get_settings

def resolve_resource_specification(resource_specification):
    module, subpath = resource_specification.split(':')
    modpath = op.dirname(__import__(module).__file__)
    return op.join(modpath, subpath)

class CurtainRenderer(object):
    def __init__(self, path):
        self.__filename = path
        settings = get_settings()
        auto_reload = settings and settings['reload_templates']
        if ':' in path:
            path = resolve_resource_specification(path)
        self.__template = Template(file_source = path,
            auto_reload = auto_reload)
    def __call__(self, value, system):
        out = stringio.StringIO()
        xml_generator = XMLGenerator(out, 'utf8')
        system.update(value)
        location = Location()
        try:
            self.__template(xml_generator, system,
                translation_context = system['context'],
                location = location)
        except Exception, e:
            raise TemplateError(self.__filename, location, e)
        return out.getvalue()

class TemplateError(Exception):
    def __init__(self, filename, location, inner_exception):
        self.__filename = filename
        self.__line, self.__column = location.current or (0, 0)
        self.__inner_exception = inner_exception
    def __str__(self):
        return 'Error in curtain template %s (line %d, column %d): %s' % (
            self.__filename, self.__line, self.__column,
            self.__inner_exception)
