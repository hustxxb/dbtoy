# -*- coding: utf-8 -*-

from setuptools import setup


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

pkg = 'dbtoy'

setup(
    name=pkg,
    version='0.0.1',
    description='Convenient wrapper and utilities for database operations',
    long_description=readme,
    author='Xiong Xiongbin',
    author_email='hustxxb@gmail.com',
    url='http://github.com/hustxxb/dbtoy',
    license=license,
    zip_safe=False,
    packages=[pkg]
)
