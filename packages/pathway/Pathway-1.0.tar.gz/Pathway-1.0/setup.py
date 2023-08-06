#!/usr/bin/env python
# distutils setup script for Pathway

from distutils.core import setup

info = '''\
Pathway is a module for interacting with the filesystem in a clean,
object-oriented manner. For example, instead of::

    datafile = os.path.join(datapath, 'somedata.txt')
    if os.path.exists(datafile)
        os.rename(datafile, datafile + '.old')
    fd = open(datafile, 'w')
    fd.write(data)
    fd.close()

You can write the much cleaner:

    datadir = pathway.new(datapath)
    if 'somedata.txt' in datadir:
        datadir['somedata.txt'].rename('somedata.txt.old', overwrite=True)
    datadir.create('somedata.txt', data)

The majority of filesystem operations have corresponding methods. The module
itself has no dependencies besides Python.
'''

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Topic :: System :: Filesystems'
]

setup(
    name='Pathway',
    version='1.0',
    description='A library for interacting with the filesystem',
    long_description=info,
    author='LeafStorm',
    author_email='leafstormrush@gmail.com',
    py_modules=['pathway'],
    provides=['pathway'],
    classifiers=classifiers
)
