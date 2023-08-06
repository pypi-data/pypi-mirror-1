#!/usr/bin/env python

from setuptools import *

try:
	readme = open("README").read()
except StandardError:
	readme = "see README file"

setup(
	name='mandy',
	version='0.1.4',
	description='a terse command-line options parser',
	author='Tim Cuthbertson',
	author_email='tim3d.junk+mandy@gmail.com',
	url='http://pypi.python.org/pypi/mandy/',
	packages=find_packages(exclude=["test"]),
	
	long_description=readme,
	classifiers=[
		"License :: OSI Approved :: BSD License",
		"Programming Language :: Python",
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"Topic :: Software Development :: Libraries :: Python Modules",
	],
	keywords='optparse option parsing command commandline simple',
	license='BSD',
	install_requires=[
		'setuptools',
	],
)
