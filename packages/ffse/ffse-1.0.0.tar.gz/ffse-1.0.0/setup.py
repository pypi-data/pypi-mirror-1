#!/usr/bin/env python

from distutils.core import setup

description = """\
Firefox Session Editor (FFSE) is a utility to delete entries from
the Firefox web browser's session store.  The most common reason
to do this is because you have stumbled upon a page which crashes
Firefox as soon as your session is restored.  Firefox only gives
you the option of erasing your entire session when this happens.
"""

classifiers = """\
Development Status :: 5 - Production/Stable
Intended Audience :: End Users/Desktop
License :: OSI Approved :: GNU General Public License (GPL)
Natural Language :: English
Operating System :: Microsoft :: Windows :: Windows NT/2000
Operating System :: MacOS :: MacOS X
Operating System :: POSIX :: Linux
Programming Language :: Python
Topic :: Utilities
"""


setup(name='ffse',
      version='1.0.0',
      description='Editor for the Firefox session store',
      long_description=description,
      author='Kevin Vance',
      author_email='kvance@kvance.com',
      url='http://kvance.com/project/ffse/',
      license='GPL',
      platforms='any',
      classifiers=filter(None, classifiers.split("\n")),
      packages=['FFSessionEditor'],
      scripts=['ffse.py'],
)
