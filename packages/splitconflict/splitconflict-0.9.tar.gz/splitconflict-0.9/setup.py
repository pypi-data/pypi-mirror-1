#!/usr/bin/env python2.4
#
# (c) 2007 Andreas Kostyrka
#

from distutils.core import setup
setup(name='splitconflict',
      description="Helper script to extract the three versions of a SVK conflicted file.",
      download_url="http://heaven.kostyrka.org/splitconflict/",
      author="Andreas Kostyrka",
      author_email="andreas@kostyrka.org",
      classifiers = ['Development Status :: 4 - Beta',
                     'Environment :: Console',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: GNU General Public License (GPL)',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Topic :: Software Development :: Version Control'],
      version='0.9',
      scripts=['splitconflict.py', ]
      )
