# Copyright (C) 2008 Stephan Peijnik
#
# This file is part of sptest.
#
#  sptest is free software: you can redistribute it and/or modify     
#  it under the terms of the GNU General Public License as published by      
#  the Free Software Foundation, either version 3 of the License, or         
#  (at your option) any later version.                                       
#                                                                              
#  sptest is distributed in the hope that it will be useful,          
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             
#  GNU General Public License for more details.                             
#                                                                              
#  You should have received a copy of the GNU General Public License       
#  along with sptest.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup
import glob


import sptest

setup(
    name="sptest",
    version=sptest.__version__,
    description='Python unittest extension',
    long_description='''sptest provides an easier way of customizing how
    Python unittest results are handled. It comes with two simple output
    handler classes: FancyCLIOutput (coloured output) and XMLOutput, which
    writes the results to an XML file.

    New output handlers can be implemented by extending the
    sptest.output.IOutput interface.
    ''',
    author='Stephan Peijnik',
    author_email='sp@sp.or.at',
    url='http://www.bitbucket.org/sp/sptest',
    license='GNU GPLv3+',
    packages = ['sptest'],
    classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Programming Language :: Python',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Testing',
    ]
    )
