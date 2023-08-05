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
      version='0.01a',
      description='WSGI delegation based on uri path and method.',
      long_description=(
           "There are various other packages that do the same thing "
           + "in various but similar ways and they are "
           + "integrated into various frameworks to various "
           + "degrees. This is the particular way that "
           + "seems best to me at the time of this writing. "
           + "The goals are to support \"RESTful\" url mapping "
           + "as WSGI middleware for maximum interop,"
           + "without a custom mini-language (rather just regexes), "
           + "or being architecture specific (to MVC or whatever), "
           + "or being (even worse) framework specific. "
           + "The best thing about selector is how simple it is."),
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

