#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Author: ÷‹≈Ù
# Date: 2006-10-02
# Email: chowroc.z@gmail.com

from distutils.core import setup

setup(
	name = 'crablfs',
	version = '0.1.1beta',
	author = 'Zhou Peng(chowroc)',
	author_email = 'chowroc.z@gmail.com',
	description = "User Based Package Management System",
	platforms = 'platform independent',
	license = 'GPL version 2',
	# classifier = [
	#	'Environment :: Console',
	#	'Operating System :: POSIX',
	#	'Programming Language :: Python',
	#	'Topic :: Communications :: Email',
	# ],
	py_modules = ['userpack'],
	package_dir = {'crablfs' : 'lib'},
	packages = ['crablfs'],
	scripts = ['userpack', 'crablfs', 'scripts/copy-profiles'],
	data_files = [('/etc', ['userpack.dirs'])],
)

# from distutils import file_util
# file_util.copy_file('userpack', 'upm', link='sym')
