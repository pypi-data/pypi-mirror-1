# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: setup.py 5447 2007-11-27 15:25:45Z sweh $
"""Setup for gocept.fixedpoint package"""

from setuptools import setup, find_packages

name = 'gocept.fixedpoint'

setup(
    name=name,
    version='0.1',
    url='http://www.python.org/pypi/'+name,
    license='ZPL 2.1',
    description='Fixedpoint datatype in python. Original code by Tim Peters.',
    author='Sebastian Wehrmann',
    author_email='sw@gocept.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['gocept',],
    include_package_data=True,
    install_requires=[
        'setuptools',
    ],
    zip_safe=False,
    )
