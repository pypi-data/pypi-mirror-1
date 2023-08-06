#       setup.py
#       
#       Copyright 2009 ahmed youssef <xmonader@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from distutils.core import setup
 
 
setup(name='pybloomfilter',
      version='1.0',
      author = "Ahmed Youssef",
      author_email="xmonader@gmail.com",
      description='bloomfilter for Python',
      long_description='A bloom filter is a space efficient data structure that can be used to test whether a given element is part of a set. Lookups will occasionally generate false positives, but never false negatives. check: http://c-algorithms.sourceforge.net/',
      py_modules=['pybloomfilter'],
      url="http://programming-fr34ks.net",
      license="GPL v2",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Database :: Database Engines/Servers',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
       )

