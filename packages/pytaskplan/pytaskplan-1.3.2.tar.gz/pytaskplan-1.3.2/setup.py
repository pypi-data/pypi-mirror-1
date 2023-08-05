#! /usr/bin/env python
#
# $Id$

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

Changes for 1.3.2 (thanks Rijk Stofberg):

- several bug fixes
- truncate labels in plan.html display (tooltips for whole label)

''',
    author = "Richard Jones",
    author_email = "richard@mechanicalcat.net",
    url = 'http://mechanicalcat.net/tech/pytaskplan/',
    packages = ['taskplan'],
    scripts = ['pytaskplan']
)

# vim: set filetype=python ts=4 sw=4 et si
