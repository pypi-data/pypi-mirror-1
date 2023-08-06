#!/usr/bin/env python

from setuptools import *

setup(
	name='mandy',
	version='0.1.3',
	description='a terse command-line options parser',
	author='Tim Cuthbertson',
	author_email='tim3d.junk+mandy@gmail.com',
	url='http://pypi.python.org/pypi/mandy/',
	packages=find_packages(exclude=["test"]),
	
	long_description=open("README").read(),
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
