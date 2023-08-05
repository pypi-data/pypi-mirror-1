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
      version='0.1',
      description=\
        'A simple but non-restrictive abstraction of WSGI for end users.',
      long_description="""\
This distribution provides Yet Another Request Object (for WSGI)
in a way that is intended to be simple and useful for end users
(by which I simply mean web developers who don't want to have to know
a lot about WSGI to get the job done). The Yaro class can be used as a 
decorator if you are using Python 2.4, which is nice.""",
      author='Luke Arno',
      author_email='luke.arno@gmail.com',
      url='http://lukearno.com/projects/static/',
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

