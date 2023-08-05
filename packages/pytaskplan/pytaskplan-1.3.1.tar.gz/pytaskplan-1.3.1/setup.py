#! /usr/bin/env python
#
# $Id: setup.py,v 1.2 2003/09/29 04:59:34 richard Exp $

from distutils.core import setup

# perform the setup action
from taskplan import __version__
setup(
    name = "pytaskplan", 
    version = __version__,
    description = "Python task planner",
    long_description = 
'''A simple task planner capable of:

- resource allocation
- interruptions (holidays, etc)
- HTML plan generation
- HTML gantt chart generation

Changes for 1.3.0 (thanks Rijk Stofberg):

- fixed bug in gantt generation
- added colours to people.csv which is much more manageable

''',
    author = "Richard Jones",
    author_email = "richard@mechanicalcat.net",
    url = 'http://mechanicalcat.net/tech/pytaskplan/',
    download_url = 'http://mechanicalcat.net/tech/pytaskplan/pytaskplan-%s.tar.gz'%__version__,
    packages = ['taskplan'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Office/Business :: Scheduling',
    ],
    scripts = ['pytaskplan']
)

# vim: set filetype=python ts=4 sw=4 et si
