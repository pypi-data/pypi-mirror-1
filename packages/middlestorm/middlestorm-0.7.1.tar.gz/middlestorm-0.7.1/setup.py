#!/usr/bin/env python
# vim:ts=4:sw=4:et

from setuptools import setup
from os import path

setup(
    name='middlestorm',
    version='0.7.1',
    description="Middleware for use Storm ORM in WSGI applications",
    long_description=open(path.join(path.dirname(__file__), 'README.txt')).read(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Natural Language :: Russian",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Database :: Front-Ends",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
    ], 
    keywords='wsgi middleware decorator storm orm dbms db postgres mysql sqlite web webdev www',
    author='Vsevolod Balashov',
    author_email='vsevolod@balashov.name',
    url='http://pypi.python.org/pypi/middlestorm',
    download_url="http://vsevolod.balashov.name/download/python/middlestorm/",
    license='LGPL 2.1',
    py_modules=["middlestorm"],
    test_suite='nose.collector',
    zip_safe=True,
    install_requires=["storm>=0.10"],
    entry_points = """\
        [paste.filter_app_factory]
        middlestorm = middlestorm:make_middleware
        """,
)
