# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: setup.py 5847 2008-05-26 15:55:23Z sweh $
"""Setup for gocept.fixedpoint package"""

import os.path

from setuptools import setup, find_packages

name = 'gocept.fixedpoint'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name=name,
    version='0.2',
    url='http://www.python.org/pypi/'+name,
    license='ZPL 2.1',
    description='Fixedpoint datatype in python.',
    long_description = (read('README.txt')
                         + '\n\n' +
                         read('src', 'gocept', 'fixedpoint',
                             'README.txt')
                         + '\n\n' +
                         read('CHANGES.txt')
    ),
    author='Sebastian Wehrmann',
    author_email='sw@gocept.com',
    keywords='fixedpoint decimal datatype',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['gocept',],
    include_package_data=True,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP'],
    install_requires=[
        'setuptools',
    ],
    zip_safe=False,
    )
