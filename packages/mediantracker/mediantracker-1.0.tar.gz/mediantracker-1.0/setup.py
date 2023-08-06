#!/usr/bin/env python

# Copyright (c) 2009 John Kleint
#
# This is free software, licensed under the MIT/X11 License,
# available in the accompanying LICENSE file or via the Internet at 
# http://www.opensource.net/licenses/mit-license.html


"""
Distutils setup script for mediantracker module.
"""

from distutils.core import setup

import mediantracker

setup(name='mediantracker',
      version='1.0',
      author='John Kleint',
      author_email='mediantracker-general@lists.sourceforge.net',
      url='http://sourceforge.net/projects/mediantracker/',
      description='Tracks the overall median of a stream of values "on-line" in reasonably efficient fashion.',
      long_description=mediantracker.__doc__,
      py_modules=['mediantracker'],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Science/Research',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'Topic :: Scientific/Engineering :: Mathematics',
                   'License :: OSI Approved :: MIT License'
                  ],
      keywords='median statistics online incremental dynamic mathematics',
      license='MIT License',
      test_suite='test.test_mediantracker',
      zip_safe=True,
     )

