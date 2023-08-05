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

version = '0.2.1'

setup(name='shrubbery',
      version=version,
      description="Simple and smart template engine to generate HTML/XML",
      long_description='''\
Shrubbery is a *Smart Html Renderer Using Blocks to Bind Expressions Repeatedly*. You can also think of it as the "world's easiest templating engine". Templates hold no logic whatsoever, with nodes being repeated as needed by the replacement data. Here's a simple example::
    
    >>> from shrubbery.template import Template
    >>> template = """
    ... <ul>
    ...     <li>{todo.task}: {todo.description}</li>
    ... </ul>"""
    >>> t = Template(template)

We can pass a single value as the ``todo`` expression::

    >>> data = {"todo": {"task": "Work",
    ...                  "description": "Finish article for GRL."}}
    >>> print t.process(data).prettify()
    <ul>
         <li>
          Work: Finish article for GRL.
         </li>
    </ul>

Nothing to see here. Let's pass a list instead, with more tasks::

    >>> data = {"todo": [{"task": "Work",
    ...                   "description": "Finish article for GRL."},
    ...                  {"task": "Play",
    ...                   "description": "Finish next version of Shrubbery"}]}
    >>> print t.process(data).prettify()
    <ul>
         <li>
          Work: Finish article for GRL.
         </li>     <li>
          Play: Finish next version of Shrubbery
         </li>
    </ul>

We can even pass a nested list::

    >>> data = {"todo": [{"task": "Work",
    ...                   "description": "Finish article for GRL."},
    ...                  {"task": "Play",
    ...                   "description": ["Finish next version of Shrubbery",
    ...                                   "Eat some pretzels"]}]}
    >>> print t.process(data).prettify()
    <ul>
         <li>
          Work: Finish article for GRL.
         </li>     <li>
          Play: Finish next version of Shrubbery
         </li>     <li>
          Play: Eat some pretzels
         </li>
    </ul>

''',
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
      shrubbery = shrubbery.buffet:ShrubberyTemplatePlugin
      """,
      )
     
