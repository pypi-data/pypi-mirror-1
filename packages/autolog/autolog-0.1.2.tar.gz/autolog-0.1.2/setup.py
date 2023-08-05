#!/usr/bin/env python

"""autolog: quick and easy logging setup

Autolog makes the standard Python logging module easier to set up.
"""

__version__ = "0.1.2"

from distutils.core import setup

doclines = __doc__.splitlines()
name, short_description = doclines[0].split(": ")
long_description = "\n".join(doclines[2:])

url = "http://www.ebi.ac.uk/~hoffman/software/%s/" % name.lower()
download_url = "%s/%s-%s.tar.gz" % (url, name, __version__)

classifiers = ["License :: OSI Approved :: GNU General Public License (GPL)",
               "Natural Language :: English",
               "Programming Language :: Python"]

setup(name=name,
      version=__version__,
      description=short_description,
      author="Michael Hoffman",
      author_email="hoffman+%s@ebi.ac.uk" % name.lower(),
      url=url,
      download_url=download_url,
      license="GNU GPL v2",
      classifiers=classifiers,
      long_description = long_description,
      package_dir = {'': 'lib'},
      py_modules = ['autolog'],
      requires=['path'],
      setup_requires=['path']
      )
