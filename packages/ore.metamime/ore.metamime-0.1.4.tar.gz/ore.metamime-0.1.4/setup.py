##############################################################################
#
# Copyright (c) 2008 Kapil Thangavelu
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
import setuptools

def read( name ):
    return open( name ).read()

setuptools.setup(
    name = 'ore.metamime',
    version = "0.1.4",
    author='Kapil Thangavelu',
    author_email='kapil.foss@gmail.com',    
    description = "Mime Identification and Property Extraction",
    long_description="Zope3 Utility Wrapper Around Hachoir",
    url='http://pypi.python.org/pypi/ore.metamime',
    packages = setuptools.find_packages('src'),
    package_dir = {'':'src'},
    include_package_data = True,
    namespace_packages = ['ore'],
    install_requires = [
        'setuptools',
        'zope.component',
        'zope.filerepresentation',
        'hachoir-core',
        'hachoir-parser',
        'hachoir-metadata',
        ],
    zip_safe=False,
    classifiers=['Programming Language :: Python',
                 'Environment :: Web Environment',
                 'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                 'Framework :: Zope3',
                 ],    
    )
