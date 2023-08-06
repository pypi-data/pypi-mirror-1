# -*- encoding: utf-8 -*-

import ez_setup
ez_setup.use_setuptools(version='0.6c9')

from setuptools import setup, Distribution
import os
import sys

from multiblend import __revision__

setup(
    name='multiblend', 
    version=__revision__, 
    author='Sybren A. Stuvel',
    author_email='sybren@stuvel.eu', 
    maintainer='Sybren A. Stuvel',
    maintainer_email='sybren@stuvel.eu',
    description='Distributed rendering with Blender', 
    long_description='Utility that can distribute rendering of '
        'frames with Blender over multiple nodes.',
    packages=['multiblend'],
    url='http://www.stuvel.eu/multiblend',
    data_files=[],
    license='GPL',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Natural Language :: English',
    ],
    entry_points={
        'console_scripts': [
            'multiblend = multiblend:main',
            'cachesync = multiblend:distrib_cache',
        ]
    }
)
