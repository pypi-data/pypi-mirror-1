"""setup - setuptools based installer for dbstore.

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
from setuptools import setup, find_packages

setup(name='dbstore',
      version='0.0.1',
      description='Database storage for flup session middleware.',
      long_description="""\
This distribution provides database backed storage using any PEP 249
compliant database package in conjuction with flup.middleware.session. 
A decorator for supplying WSGI apps with MySQLdb backed sessions is 
provided. 

@mysql_sessionizer(user='foo', passwd='bar', db='baz', host='localhost')
def some_wsgi_app(environ, start_response):
    ...

You will need a database with a sessions table:

CREATE TABLE sessions (
    id VARCHAR(32) NOT NULL, 
    touched  FLOAT, 
    pickle LONGTEXT, 
    primary key (id));

      """,
      author='Luke Arno',
      author_email='luke.arno@gmail.com',
      url='http://lukearno.com/projects/selector/',
      license="GPL2",
      py_modules=[],
      packages = find_packages(),
      keywords="wsgi database mysql sessions flup",
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Utilities'])

