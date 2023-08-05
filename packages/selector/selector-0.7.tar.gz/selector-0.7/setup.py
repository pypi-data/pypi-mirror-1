"""setup - setuptools based setup for selector

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
from setuptools import setup

setup(name='selector',
      version='0.7',
      description='WSGI delegation based on URL path and method.',
      long_description="""\
This distribution provides WSGI middleware
for "RESTful" mapping of URL paths to WSGI applications.
Selector now also comes with components for environ based
dispatch and on-the-fly middleware composition.
There is a very simple optional mini-language for
path expressions. Alternately we can easily use
regular expressions directly or even create our own
mini-language. There are no architecture specific features
(to MVC or whatever). Neither are there any framework
specific features. Best of all, selector is the simplest
thing that will work well (IMHO).""",
      author='Luke Arno',
      author_email='luke.arno@gmail.com',
      url='http://lukearno.com/projects/selector/',
      license="GPL2",
      py_modules=['selector'],
      packages = [],
      keywords="wsgi delegation web http rest webapps",
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Utilities'])

