#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='pyprof2html',
    version='0.1.1',
    description="Python cProfile and hotshot profile's data to HTML Converter",
    license='New BSD License',
    author='Hideo Hattori',
    author_email='syobosyobo@gmail.com',
    url='http://www.hexacosa.net/project/pyprof2html/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    py_modules=['pyprof2html'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'pyprof2html = pyprof2html:main',
        ],
    }
)

