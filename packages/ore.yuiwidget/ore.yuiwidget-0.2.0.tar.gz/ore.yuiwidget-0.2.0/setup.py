##############################################################################
#
# Copyright (c) 2008 Kapil Thangavelu <kapil.foss@gmail.com>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os, setuptools

def read(*rnames):
    file_path = os.path.join(os.path.dirname(__file__), *rnames)
    return open( file_path ).read()

setuptools.setup(
    name = 'ore.yuiwidget',
    version = "0.2.0",
    author='Kapil Thangavelu',
    author_email='kapil.foss@gmail.com',    
    description = "Zope3 Widgets From YUI",
    long_description=( read('ore','yuiwidget','README.txt')
                       + '\n\n' 
                       ),
    url='http://pypi.python.org/pypi/ore.yui',
    license='ZPL',
    packages = ['ore', 'ore.yuiwidget'],
    include_package_data = True,
    namespace_packages = ['ore'],
    install_requires = [
        'setuptools',
        'ore.yui',
        'zope.app.form',
        ],
    zip_safe=False,
    classifiers=['Programming Language :: Python',
                 'Environment :: Web Environment',
                 'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                 'Framework :: Zope3',
                 ],    
    )
