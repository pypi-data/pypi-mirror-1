# -*- coding: utf-8 -*-
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

import pygments

auth = pygments.__author__

setup(
    name = 'Pygments',
    version = pygments.__version__,
    url = pygments.__url__,
    license = pygments.__license__,
    author = auth,
    author_email = auth[auth.index('<')+1:-1],
    description = 'Pygments is a syntax highlighting package written in Python.',
    long_description = pygments.__doc__,
    keywords = 'syntax highlighting',
    packages = find_packages(),
    scripts = ['pygmentize'],
    platforms = 'any',
    zip_safe = False,
    include_package_data = True,
    classifiers = [
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
    ]
)
