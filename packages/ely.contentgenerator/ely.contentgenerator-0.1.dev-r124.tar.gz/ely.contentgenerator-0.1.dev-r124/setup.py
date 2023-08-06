from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='ely.contentgenerator',
    version=version,
    description=("Product for creating content in Zope"),
    long_description=open("README.txt").read(),
    author='Matt Halstead',
    author_email='matt@elyt.com',
    license='new BSD',
    url='http://ely.googlecode.com/svn/ely.contentgenerator/trunk',
    package_dir={'': 'src'},
    packages=['ely', 'ely.contentgenerator'],
    namespace_packages=['ely'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'setuptools',
      'ely.contentgenerator',
    ],
    )
