#!/usr/bin/env python

from distutils.core import setup

setup(name='Fossil',
	version='0.1',
	description='A basic revision control system.',
	author='David Koenig',
	author_email='karhu@u.washington.edu',
	py_modules=['fossil'],
	scripts=['fsl']
	)
