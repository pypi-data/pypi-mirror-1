#!/usr/bin/env python2.4
#
# (c) 2007 Andreas Kostyrka
#

from distutils.core import setup
setup(name='pulp',
      description="""Commandline tool to access www.gulp.de.
      Currently it only supports setting the availability of a freelancer and exporting profiles for paying members.""",
      download_url="http://heaven.kostyrka.org/pulp/",
      author="Andreas Kostyrka",
      license='http://www.gnu.org/licenses/gpl.txt',
      author_email="andreas@kostyrka.org",
      classifiers = ['Development Status :: 4 - Beta',
                     'Environment :: Console',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: GNU General Public License (GPL)',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Topic :: Office/Business',
                     ],
      version='0.2.3',
      packages=["pulp",],
      scripts=['scripts/pulp', ]
      )
