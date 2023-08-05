#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='gtkeggdeps',
    version='0.0.1',
    author='Marius Gedminas',
    author_email='marius@gedmin.as',
    url='http://mg.pov.lt/gtkeggdeps/',
    download_url='http://mg.pov.lt/gtkeggdeps/bzr#egg=gtkeggdeps-dev',
    description='Interactive egg dependency browser',
    license='ZPL 2.1',

    py_modules=['gtkeggdeps'],
    install_requires=['tl.eggdeps'],
    zip_safe=False,
    entry_points="""
    [console_scripts]
    gtkeggdeps = gtkeggdeps:main
    """,
)
