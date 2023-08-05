"""setup - setuptools based setup for skel

Copyright (C) 2006 Luke Arno - http://lukearno.com/

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to 
the Free Software Foundation, Inc., 51 Franklin Street, 
Fifth Floor, Boston, MA  02110-1301  USA

Luke Arno can be found at http://lukearno.com/

"""
from setuptools import setup

setup(name='skel',
      version='0.3.1',
      description='Template-based filesystem manipulation '
                  '(for project skeletons and such).',
      long_description="""\
Produce a set of files and directories based on a "template"
set of files and directories and a some data (usually a dict of 
"vars". Replace variables in file and directory names as well as 
file contents. Comes with a nice (I think) command line interface
but is also a utility for building frameworks and such. Supports
pluggable "filters" so you could use Kid or Cheetah or probably
any other templating language that you need.
""",
      author='Luke Arno',
      author_email='luke.arno@gmail.com',
      url='http://lukearno.com/projects/skel/',
      license="LGPL2",
      py_modules=['skel'],
      packages = [],
      keywords="directory filesystem project skel "
               "skeleton template command frameworks",
      entry_points={'console_scripts':['skelcmd = skel:command']},
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: '
                    'GNU Library or Lesser General Public License (LGPL)',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Utilities'])

