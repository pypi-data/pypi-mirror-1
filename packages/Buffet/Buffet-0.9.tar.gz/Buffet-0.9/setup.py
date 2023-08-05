import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(name = "Buffet", version = "0.9",
      author = "Christian Wyglendowski",
      author_email = "christian@dowski.com",
      url = "http://projects.dowski.com/projects/buffet",
      license="MIT",
      ##install_requires = ['CherryPy == 2.1.1],
      zip_safe=False,
      description = "Buffet is a universal templating system for CherryPy.",
      long_description="""
Buffet is a universal templating system for CherryPy.  It supports plugins that follow the interface defined at http://www.turbogears.org/docs/plugins/template.html and register setuptools entry points in the 'python.templating.engines' entry point group.

Some available template plugins as of this release:

 * TurboCheetah - Cheetah template support
 * TurboKid - Kid template support
 * BuffetMyghty - Myghty template support
 * BuffetString - Python string Template support
 * TurboStan - Nevow Stan support
 * TurboHtmlPy - Formencode.htmlgen support

You should simply be able to do "easy_install [PluginName]" to get quick support for each engine in Buffet.""",
      packages = find_packages(),
      )
