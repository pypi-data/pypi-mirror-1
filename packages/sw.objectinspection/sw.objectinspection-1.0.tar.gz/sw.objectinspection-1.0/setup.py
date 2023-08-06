# Copyright (c) 2009 Sebastian Wehrmann
# See also LICENSE.txt
"""Setup for sw.objectinspection package"""

import sys
import os.path

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name = 'sw.objectinspection'

setup(
    name=name,
    version = '1.0',
    license='ZPL 2.1',
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Database'],
    description='Provides an API to access an objects references (children).',
    long_description = (read('src', 'sw', 'objectinspection', 'README.txt')
                        + '\n\n' +
                        read('CHANGES.txt')
    ),
    author='Sebastian Wehrmann',
    author_email='sw@gocept.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['sw',],
    include_package_data=True,
    install_requires=[
        'setuptools',
        'zope.component',
        'zope.interface',
    ],
    extras_require = dict(
        test=[
            'zope.testing',
            'zope.app.testing',
        ]),
    zip_safe=False,
    )
