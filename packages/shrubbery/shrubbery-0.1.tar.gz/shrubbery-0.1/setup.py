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

version = '0.1'

setup(name='shrubbery',
      version=version,
      description="Simple template engine to convert JSON to HTML/XML",
      long_description="""\
A simple template engine designed to convert JSON to HTML or XML. Templates hold no logic whatsoever, with nodes being repeated as needed by the replacement data::
    
    >>> from shrubbery import Template
    >>> template = "<ul><li>{todo}</li></ul>"
    >>> print Template(template, {"todo": "nothing"})
    <ul><li>nothing</li></ul>
    >>> print Template(template, {"todo": ["work", "work", "work"]})
    <ul><li>work</li><li>work</li><li>work</li></ul>

""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='json template html xml',
      author='Roberto De Almeida',
      author_email='roberto@dealmeida.net',
      url='http://taoetc.org/46',
      download_url = "http://cheeseshop.python.org/packages/source/s/shrubbery/shrubbery-%s.tar.gz" % version,
      license='MIT',
      py_modules=['shrubbery'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          "BeautifulSoup",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
      
