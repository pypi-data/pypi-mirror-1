#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='pyprof2html',
    version='0.1.2',
    description="Python cProfile and hotshot profile's data to HTML Converter",
    license='New BSD License',
    author='Hideo Hattori',
    author_email='syobosyobo@gmail.com',
    url='http://www.hexacosa.net/project/pyprof2html/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    keywords="profile visualize html",
    py_modules=['pyprof2html'],
    install_requires=['jinja2'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'pyprof2html = pyprof2html:main',
        ],
    }
)

