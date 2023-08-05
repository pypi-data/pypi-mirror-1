#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Author: ÷‹≈Ù
# Date: 2006-10-02
# Email: chowroc.z@gmail.com

from distutils.core import setup

setup(
	name = 'crablfs',
	version = '0.1.1alpha',
	author = '÷‹≈Ù(chowroc)',
	author_email = 'chowroc.z@gmail.com',
	description = 'User Based Package Management System',
	# classifier = [
	#	'Environment :: Console',
	#	'Operating System :: POSIX',
	#	'Programming Language :: Python',
	#	'Topic :: Communications :: Email',
	# ],
	py_modules = ['userpack'],
	package_dir = {'crablfs' : 'lib'},
	packages = ['crablfs'],
	scripts = ['userpack', 'crablfs'],
	data_files = [('/etc', ['userpack.dirs'])],
)
