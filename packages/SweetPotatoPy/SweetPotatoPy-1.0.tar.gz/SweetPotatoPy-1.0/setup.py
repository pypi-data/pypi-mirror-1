#!/usr/bin/env python

from distutils.core import setup

documentation = """
SweetPotatoPy (or SPP) is a considerably advanced Page Publishing System for CGI
using the PyTin_ framework and Jinja2_ templating.

.. _PyTin: /index.cgi/swproj/pytin
.. _Jinja2: http://jinja.pocoo.org/2/

Features
========
- Pages are written in the flexible reStructuredText format.
- Pages can be hierarchically nested.
- A flexible navbar generator can dynamically hide and show navigation bars.
- Uses the ultra-powerful Jinja2 templating system.
- The PyTin framework lets you store the code in one place while keeping a short
  initialization script on your server, while still letting you keep SPP itself
  in your CGI-bin if you want to.
- All filesystem-based: no database needed to store pages.

Be sure to read README.txt for all the essential documentation!
"""

setup(name="SweetPotatoPy",
      version="1.0",
      author="LeafStorm/Pacific Science",
      author_email="pacsciadmin@gmail.com",
      description="A Page Publishing System that uses PyTin and Jinja2.",
      long_description=documentation,
      py_modules=['spp'],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Intended Audience :: Information Technology',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.5',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content'],
      requires=['pytin', 'jinja2'])
