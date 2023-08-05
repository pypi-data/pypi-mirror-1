import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(name = "Buffet", version = "0.6",
      author = "Christian Wyglendowski",
      author_email = "christian@dowski.com",
      url = "http://projects.dowski.com/projects/buffet",
      ##install_requires = ['CherryPy == 2.1'],
      zip_safe=False,
      description = "Buffet is a universal templating system for CherryPy.",
      packages = find_packages(),
      )
