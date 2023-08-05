"""setup - setuptools based setup for yaro

Copyright (C) 2006 Luke Arno - http://lukearno.com/

This program is free software; you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by the 
Free Software Foundation; either version 2 of the License, or (at your 
option) any later version.

This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to:

The Free Software Foundation, Inc., 
51 Franklin Street, Fifth Floor, 
Boston, MA  02110-1301, USA.

Luke Arno can be found at http://lukearno.com/

"""

try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name='yaro',
      version='0.5',
      description=\
        'A simple but non-restrictive abstraction of WSGI.',
      long_description="""\
This distribution provides Yet Another Request Object (for WSGI) in a 
way that is intended to be simple and useful for web developers who 
don't want to have to know a lot about WSGI to get the job done. It's 
also a handy convenience for those who do like to get under the hood 
but would be happy to eliminate some boilerplate without the 
encumbrance of some all-singing-all-dancing framework.""",
      author='Luke Arno',
      author_email='luke.arno@gmail.com',
      url='http://lukearno.com/projects/yaro/',
      license="GPL2",
      py_modules=['yaro'],
      packages = [],
      install_requires="wsgiref",
      keywords="wsgi web http request webapps",
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Utilities'])

