RELEASE = True

from setuptools import setup, find_packages
import sys, os

classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Text Processing :: Markup
"""

version = '0.1.1'

setup(name='shrubbery',
      version=version,
      description="Simple template engine to convert JSON to HTML/XML",
      long_description="""\
A simple template engine designed to convert JSON to HTML or XML. Templates hold no logic whatsoever, with nodes being repeated as needed by the replacement data. Here's a simple template::
    
    >>> from shrubbery.shrubbery import Template
    >>> template = "<ul><li>{todo}</li></ul>"  

We can pass a single value as the ``todo`` expression::

    >>> print Template(template, {"todo": "nothing"}) 
    <ul><li>nothing</li></ul>  

But if we pass a list instead, the node is repeated as necessary::

    >>> print Template(template, {"todo": ["one", "two", "three"]}) 
    <ul><li>one</li><li>two</li><li>three</li></ul> 

""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='json template html xml',
      author='Roberto De Almeida',
      author_email='roberto@dealmeida.net',
      url='http://taoetc.org/46',
      download_url = "http://cheeseshop.python.org/packages/source/s/shrubbery/shrubbery-%s.tar.gz" % version,
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          "BeautifulSoup",
      ],
      entry_points="""
      # -*- Entry points: -*-
      [python.templating.engines]
      shrubbery = shrubbery.buffet:TemplatePlugin
      """,
      )
     
