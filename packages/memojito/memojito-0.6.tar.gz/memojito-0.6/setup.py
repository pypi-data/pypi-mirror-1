import os, sys
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name = 'memojito',
    version = '0.6',
    url='http://svn.plone.org/svn/collective/plonents/components/memojito/trunk#egg=memojito',
    license='MIT',
    description='simple library of memoizing decorators',
    author='Whit Morriss',
    author_email='whit@openplans.org',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe = True)
