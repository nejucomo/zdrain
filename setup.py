#!/usr/bin/env python

from setuptools import setup, find_packages


PACKAGE = 'zdrain'

setup(
    name=PACKAGE,
    description='Drain all funds from input addresses to output addresses.',
    version='0.1',
    author='Nathan Wilcox',
    author_email='nejucomo@gmail.com',
    license='GPLv3',
    url='https://github.com/nejucomo/{}'.format(PACKAGE),

    install_requires=[
        'simplejson >= 3.11.1',
    ],

    packages=find_packages(),

    entry_points={
        'console_scripts': [
            '{} = {}.main:main'.format(
                PACKAGE.replace('_', '-'),
                PACKAGE,
            )
        ],
    }
)
