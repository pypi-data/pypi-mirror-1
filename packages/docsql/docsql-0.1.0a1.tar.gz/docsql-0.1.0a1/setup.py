#!/usr/bin/env python

"""docsql: Easy access to Python DB API databases

Docsql allows one to access databases in Python in a straightforward
manner.
"""

__version__ = "0.1.0a1"

# Copyright $Year$ Michael M. Hoffman <hoffman+software@ebi.ac.uk>

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

doclines = __doc__.splitlines()
name, short_description = doclines[0].split(": ")
long_description = "\n".join(doclines[2:])

url = "http://noble.gs.washington.edu/~mmh1/software/%s/" % name.lower()
download_url = "%s%s-%s.tar.gz" % (url, name, __version__)

classifiers = ["License :: OSI Approved :: GNU General Public License (GPL)",
               "Natural Language :: English",
               "Programming Language :: Python"]

install_requires = ["MySQL-python>=1.2.2"]

setup(name=name,
      version=__version__,
      description=short_description,
      author="Michael Hoffman",
      author_email="hoffman+%s@ebi.ac.uk" % name.lower(),
      url=url,
      download_url=download_url,
      install_requires=install_requires,
      license="GNU GPLv2",
      classifiers=classifiers,
      long_description=long_description,
      zip_safe=True,
      package_dir = {'': 'lib'},
      py_modules = ['docsql', 'dboptions']
      )
