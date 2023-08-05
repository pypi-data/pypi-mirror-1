import os, sys
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

base = os.path.abspath(os.path.join(os.curdir,
                       os.path.dirname(__file__),
                       'src'))

sys.path.insert(0, base)

from memojito import version

setup(
    name = 'memojito',
    version = version.v_short,
    url='http://svn.plone.org/svn/collective/plonents/components/memojito/tags/%s' %version.v_short,
    license='MIT',
    description='simple library of memoizing decorators for object methods',
    author='Whit Morriss',
    author_email='whit@openplans.org',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    tests_require = ['zope.testing'],
    include_package_data = True,
    zip_safe = True)
