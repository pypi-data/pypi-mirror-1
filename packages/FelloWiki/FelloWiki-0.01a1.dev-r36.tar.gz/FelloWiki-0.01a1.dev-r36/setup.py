# Copyright (c) 2006 Jan Niklas Fingerle
#
# This source code file is based on a TurboGears "quickstarted" project.
# The TurboGears framework is copyrighted (c) 2005, 2006 by Kevin Dangoor 
# and contributors.
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os

# Release information about FelloWiki

setup(
    name="FelloWiki",
    version="0.01a1",
    
    description='Yet another wiki engine',
    long_description='Yet another wiki engine - still heavily in alpha',
    author="Jan Niklas Fingerle",
    author_email='fingerle@users.berlios.de',
    url='http://developer.berlios.de/projects/fellowiki/',
    download_url='http://developer.berlios.de/project/showfiles.php?group_id=6220',
    license='MIT-style',
    
    install_requires = [
        "TurboGears >= 1.0b1",
    ],
    scripts = ["fellowiki.py"],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='fellowiki',
                                     package='fellowiki'),
    keywords = ['turbogears.app'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        # if this is an application that you'll distribute through
        # the Cheeseshop, uncomment the next line
        'Framework :: TurboGears :: Applications',
        
        # if this is a package that includes widgets that you'll distribute
        # through the Cheeseshop, uncomment the next line
        # 'Framework :: TurboGears :: Widgets',
    ],
    test_suite = 'nose.collector',
    )
    
