# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: setup.py 5739 2008-05-17 13:20:36Z ctheune $
"""Setup for gocept.munin package"""

from setuptools import setup, find_packages

name = 'gocept.munin'

setup(
    name=name,
    version='0.1',
    url='http://www.python.org/pypi/'+name,
    license='ZPL 2.1',
    description='Utilities for writing munin plugins.',
    long_description=open('README.txt', 'r').read(),
    author='Christian Theune',
    author_email='ct@gocept.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['gocept',],
    include_package_data=True,
    install_requires=[
        'setuptools',
    ],
    zip_safe=False,
    )
