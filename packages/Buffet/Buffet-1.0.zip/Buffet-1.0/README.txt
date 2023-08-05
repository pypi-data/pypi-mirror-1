For the latest on Buffet, see http://projects.dowski.com/projects/buffet

Buffet is a universal templating system for CherryPy 2.2.x.  It supports plugins that follow the interface defined at http://www.turbogears.org/docs/plugins/template.html and register setuptools entry points in the 'python.templating.engines' entry point group.

Some available template plugins as of this release:

 * TurboCheetah - Cheetah template support
 * TurboKid - Kid template support
 * BuffetMyghty - Myghty template support
 * BuffetString - Python string Template support
 * BuffetXSLT - XSLT templating using Amara
 * TurboStan - Nevow Stan support
 * TurboHtmlPy - Formencode.htmlgen support

You should simply be able to do "easy_install [PluginName]" to get quick support for each engine in Buffet.
