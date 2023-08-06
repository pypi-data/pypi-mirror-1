from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

setup(name="golem",
      version="0.99b",
      description="Ontology language and toolkit for semantic processing of scientific data",
      long_description="""\
Golem is an ontology language - primarily (but not exclusively) designed to be used with CML, the Chemical Markup Language. pyGolem is its supporting toolkit, written in Python.

Together, they help scientists use, and write, tools which make it easier to process very large volumes of scientific data by reference to the concepts found in it, rather than having to fight with the files' formats and syntax.
""",
      author="Andrew Walkingshaw",
      author_email="andrew@lexical.org.uk",
      url="http://www.lexical.org.uk/golem/",
      download_url="http://code.google.com/p/pygolem/downloads",
      packages=["golem", "golem/helpers", "golem/db"],
      package_data={'golem': ['../dictionaries/*']},
      scripts=['bin/summon', 'bin/lexicographer', 'bin/make_dictionary'],
      install_requires=['lxml', 'simplejson==1.8.1'],
)
