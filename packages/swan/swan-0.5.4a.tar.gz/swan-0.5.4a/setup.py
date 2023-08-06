#!/usr/bin/env python

from distutils.core import setup

classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: X11 Applications :: GTK',
      'Intended Audience :: End Users/Desktop',
      'License :: OSI Approved :: GNU General Public License (GPL)',
      'Operating System :: POSIX :: Linux',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering',
        ]

setup(name='swan',
        version = "0.5.4a",
        description = 'Easy continuous wavelet analysis',
        author = 'A. Brazhe',
        author_email = "brazhe@gmail.com",
        license = 'GNU GPL',
        url = "http://cell.biophys.msu.ru/static/swan",
        packages = ['swan_gui','iwavelets'],
        package_data = {'swan_gui': ["glade/swan.glade"]},
        scripts = ['swan'],
        long_description = \
                """swan is a tool for wavelet data analysis. 
                Its meant to be simple in use and easy to extend.""",
        classifiers=classifiers
        )

