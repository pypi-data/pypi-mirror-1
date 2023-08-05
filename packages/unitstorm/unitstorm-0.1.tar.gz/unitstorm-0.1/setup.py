#!/usr/bin/env python
# vim:ts=4:sw=4:et

from setuptools import setup
from os import path

setup(
    name='unitstorm',
    version='0.1',
    description="Unit testing microframework for Storm ORM models",
    long_description=open(path.join(path.dirname(__file__), 'README.txt')).read(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Natural Language :: Russian",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Database",
        "Topic :: Software Development :: Testing"
    ],
    keywords='unit test testing unittest unitesting storm orm db dbms rdbms sql fixture fixtures postgres postgresql mysql sqlite',
    author='Vsevolod Balashov',
    author_email='vsevolod@balashov.name',
    url='http://pypi.python.org/pypi/unitstorm',
    download_url="http://vsevolod.balashov.name/download/unitstorm/",
    license='LGPL 2.1',
    py_modules=["unitstorm"],
    test_suite='nose.collector',
    zip_safe=True,
    install_requires=["storm>=0.10"]
)
