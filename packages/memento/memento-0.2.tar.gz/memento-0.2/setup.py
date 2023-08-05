"""setup - setuptools based setup for memento

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

setup(name='memento',
      version='0.2',
      description=\
        'WSGI middleware for per request code reloading.',
      long_description="""\
This distribution provides code reloading middleware for use with  
your WSGI applications. Two implementations are included. One is 
inspired by the RollBackImporter used by Steve Purcell in PyUnit. 
(http://pyunit.sourceforge.net/notes/reloading.html).
The other reloads a list of packages you supply (minus a list
of exceptions).""",
      author='Luke Arno',
      author_email='luke.arno@gmail.com',
      url='http://lukearno.com/projects/memento/',
      license="GPL2",
      py_modules=['memento'],
      packages = [],
      install_requires="resolver",
      keywords="wsgi web http reloading middleware webapps",
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Utilities'])

