#!/usr/bin/env python
import os
from setuptools import setup

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name='gtkeggdeps',
    version='0.0.7',
    author='Marius Gedminas',
    author_email='marius@gedmin.as',
    url='http://mg.pov.lt/gtkeggdeps/',
    download_url='http://cheeseshop.python.org/pypi/gtkeggdeps',
    description='Interactive egg dependency browser',
    long_description=read('README.txt') + '\n\n' + read('CHANGES.txt'),
    license='ZPL 2.1',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
    ],

    py_modules=['gtkeggdeps'],
    install_requires=['tl.eggdeps'],
    zip_safe=False,
    entry_points="""
    [console_scripts]
    gtkeggdeps = gtkeggdeps:main
    """,
)
