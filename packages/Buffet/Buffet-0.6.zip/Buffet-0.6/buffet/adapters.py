from os import path
from cStringIO import StringIO
import cherrypy

template_engines = {'kid':('kid',[]),
                    'string':('string',[]),
                    'Cheetah':('Cheetah.Template',['Template']),
                    'myghty':('myghty.interp',['interp']),
                    'cherrytemplate': ('cherrytemplate', []),
                    'Ft': ('Ft', []),
                    }

available_adapters = {}

for template_name, module_data in template_engines.iteritems():
    try:
        module, sub_modules = module_data
        globals()[template_name] = __import__(module, globals(), locals(), sub_modules)
##        print "Imported %s" % template_name
    except ImportError:
##        print "Failed to import %s" % template_name
        pass

def kid_adapter(file_name, params):
    template = kid.Template(file_name, **params)
    return template.serialize()

def string_adapter(file_name, params):
    tf = open(file_name)
    template = string.Template(tf.read())
    tf.close()
    return template.substitute(**params)

def myghty_adapter(file_name, params):
    component_dir, template = path.split(file_name)
    interpreter = myghty.Interpreter(component_root = component_dir,
                                     allow_globals=['cherrypy'],
                                     global_args={'cherrypy':cherrypy})
    buf = StringIO()
    interpreter.execute(template, request_args=params, out_buffer=buf)
    return buf.getvalue()

def cheetah_adapter(file_name, params):
    template = Cheetah.Template(file=file_name, searchList=[params])
    return str(template)

def cherrytemplate_adapter(file_name, params):
    return cherrytemplate.renderTemplate(file=file_name, loc=params)

def ft_adapter(file_name, params):
    # Parses the XML document source
    from Ft.Xml import InputSource
    # we will be using the 'xml' key in params to store the XML document string
    document = params.get('xml', '<root />')
    source = InputSource.DefaultFactory.fromString(document, 'http://none.xml')
    
    # Load the XSL stylesheet
    from Ft.Lib.Uri import OsPathToUri
    stylesheet_as_uri = OsPathToUri(file_name)
    transform = InputSource.DefaultFactory.fromUri(stylesheet_as_uri)
    
    # Create an XSLT processor
    from Ft.Xml.Xslt import Processor
    processor = Processor.Processor()
    processor.appendStylesheet(transform)
    
    # Do the transformation
    return processor.run(source, topLevelParams=params)