#!/usr/bin/env python

from os.path import dirname, join
from distutils.core import setup

from pychoose_script import __version__


def get_long_description():
    readme = join(dirname(__file__), 'README.txt')
    return open(readme).read()

description = \
    'Windows command-line tool to switch between different installed versions ' \
    'of Python.'

setup(
    name='pychoose',
    version=__version__,
    description=description,
    long_description=get_long_description(),
    url='http://code.google.com/p/pychoose/',
    author='Jonathan Hartley',
    author_email='tartley@tartley.com',
    provides=['pychoose'],
    packages=[],
    py_modules=[],
    scripts=['pychoose_script.py', 'pychoose.bat'],
    # install_requires=['mock'], # setuptools only
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.4",
        "Topic :: Software Development",
    ],
)
