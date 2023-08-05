#!/usr/bin/env python

"""textinput: streamlined version of stdlib fileinput

Typical use is:

    import textinput
    for line in textinput.lines():
        process(line)

This iterates over the lines of all files listed in sys.argv[1:],
defaulting to sys.stdin if the list is empty.  If a filename is '-' it
is also replaced by sys.stdin.  To specify an alternative list of
filenames, pass it as the argument to input().  A single file name is
also allowed.
"""

__version__ = "0.1.0"

from distutils.core import setup
import warnings

warnings.filterwarnings('ignore', 'Unknown distribution option')

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
      license="GNU GPL",
      classifiers=classifiers,
      long_description = long_description,
      package_dir = {'': 'lib'},
      py_modules = ['tabdelim', 'textinput'],
      scripts = ['scripts/innerjoin',
                 'scripts/filter',
                 'scripts/nohead',
                 'scripts/mean',
                 'scripts/hidehead',
                 'scripts/intersect'],
      zip_safe=True
      )
