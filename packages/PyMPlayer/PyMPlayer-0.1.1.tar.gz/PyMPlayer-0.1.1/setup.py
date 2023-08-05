#!/usr/bin/env python
# $Id: setup.py 309 2008-01-10 17:54:47Z darwin $

from distutils.core import setup

from pymplayer import __version__


setup(
    name='PyMPlayer',
    version=__version__,
    description='MPlayer wrapper for Python',
    long_description='MPlayer wrapper for Python',
    author='Darwin M. Bautista',
    author_email='djclue917@gmail.com',
    url='http://bbs.eee.upd.edu.ph/',
    license='GPL & LGPL',
    py_modules=['pymplayer'],
    scripts=['pymplayer', 'pymplayerd'],
    platforms=['POSIX']
)
