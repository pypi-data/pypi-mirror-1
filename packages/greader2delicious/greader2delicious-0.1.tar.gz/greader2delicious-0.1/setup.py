##
# License: greader2delicious is released under the bsd license.
# See 'license.txt' for more informations.
#

dev = 0
if dev:
    raise Exception, \
          ("""
This does not work as intended right now.
Dont use it. Will be fixed.""")

from distutils.core import setup
import os
import greader2delicious

setup(
    name='greader2delicious',
    version=greader2delicious.__version__,
    author=greader2delicious.__author__,
    author_email=greader2delicious.__email__,
    url=greader2delicious.__url__,
    description=greader2delicious.__description__,
    long_description=greader2delicious.__long_description__,
    py_modules=['greader2delicious'],
    )

