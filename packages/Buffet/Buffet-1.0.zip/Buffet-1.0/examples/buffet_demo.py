import cherrypy

from buffet import TemplateFilter, using_template, TemplateEngineMissing

missing_messages = {'kid_section':'Plugin not installed.  Try "easy_install TurboKid" and restart this demo',
                    'cheetah_section': 'Plugin not installed.  Try "easy_install TurboCheetah" and restart this demo',
                    'string_section': 'Plugin not installed.  Try "easy_install BuffetString" and restart this demo',
                    'myghty_section': 'Plugin not installed.  Try "easy_install BuffetMyghty" and restart this demo',
                    }

class EmptySection(object):
    @cherrypy.expose
    def index(self):
        page_handler_name = cherrypy.request.path.rstrip('/').split('/').pop()
        return missing_messages.get(page_handler_name, "Plugin not installed")

try:    
    class StringSection(object):
        _cp_filters = [TemplateFilter('string', 'templates/string')]

        @cherrypy.expose
        @using_template('generic_template')
        def index(self):
            return dict(title="New String Test", message="""
            End Points are fun!<br>
            <a href="multi_test">Composition with multiple templates</a>
            """)

        @cherrypy.expose
        def multi_test(self):
            return (
                    ('head',
                        dict(title="Composition Test")
                        ),
                    ('body',
                        dict(message="Thanks to Bill Mill")
                        ),
                    ('foot', {}
                        )
                    )

except TemplateEngineMissing:
    StringSection = EmptySection
    
try:
    class CheetahSection(object):
        _cp_filters = [TemplateFilter('cheetah')]

        @cherrypy.expose
        @using_template('templates/cheetah/test')
        def index(self):
            return dict(title="New TurboCheetah Test", message="Buffet does TurboCheetah!")
except TemplateEngineMissing:
    CheetahSection = EmptySection

try:
    class KidSection(object):
        _cp_filters = [TemplateFilter('kid')]

        @cherrypy.expose
        @using_template('templates/kid/test')
        def index(self):
            return dict(title="Kid at a Buffet", message="All you can eat templates.")
except TemplateEngineMissing:
    KidSection = EmptySection

try:
    class MyghtySection(object):
        try:
            # attempt to import a Myghty-customized error handler
            from cpmyghty import _cp_on_error
        except ImportError:
            pass
        
        cherrypy.config.update({'myghty_app':{'component_root':'.',
                                              'raise_error':True,
                                              }
                                })
        _cp_filters = [TemplateFilter('myghty', config_section="myghty_app")]

        @cherrypy.expose
        @using_template('templates/myghty/test')
        def index(self):
            return dict(title="Myghty good Buffet", message="Fill up another template.")

        @cherrypy.expose
        @using_template('templates/myghty/test')
        def exception(self):
            return dict()

        @cherrypy.expose
        def cp_exc(self):
            3 /0
            return "ha"
        
except TemplateEngineMissing:
    MyghtySection = EmptySection
    
class TmplTest(object):
    string_section = StringSection()
    cheetah_section = CheetahSection()
    kid_section = KidSection()
    myghty_section = MyghtySection()
    
    def index(self):
        return "<a href='string_section'>string</a><br />\
        <a href='cheetah_section'>cheetah</a><br />\
        <a href='kid_section'>kid</a><br />\
        <a href='myghty_section'>myghty</a><br />\
        "
    index.exposed = True


cherrypy.root = TmplTest()

cherrypy.config.update({'global':{'autoreload.on':False,
                                 ## 'server.log_to_screen':False,
                                  }
                        })

cherrypy.server.start()
