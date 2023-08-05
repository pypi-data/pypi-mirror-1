#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Author: 周鹏
# Date: 2006-12-01
# Email: chowroc.z@gmail.com

"""为 userpack 解析配置
在将来可用 coreea 的 plainconf 替换"""

import re
import sys

def getconf(confile, flag='norm', *keys):
	options = {}
	found = []
	if type(confile) is file:
		confile = confile
	elif type(confile) is str:
		confile = open(confile, 'r')
	for ostr in confile.readlines():
		try:
			mo = re.match(
				'^\s*(?P<key>\w+)\s*=\s*"(?P<value>.*)";\s*$', ostr)
			key = mo.group('key')
			if key not in keys: continue
			value = mo.group('value')
			if flag == 'seq':
				if not options.get(key): options[key] = [value]
				else: options[key].append(value)
			else:
				options[key] = value
			found.append(key)
		except AttributeError:
			strerr = 'plainconf: %s is not a valid option' % ostr
			print >> sys.stderr, strerr
	for key in keys:
		if key not in found:
			strerr = 'plainconf: key %s was not found' % key
			print >> sys.stderr, strerr
	return options

def setconf(confile, mode, **options):
	if type(confile) is file:
		confile = confile
	elif type(confile) is str:
		confile = open(confile, mode)
	for key, value in options.iteritems():
		confile.write('%s = "%s";\n' % (key, value))
	# confile.close()

# optmap = getconf('/usr/src/rxvt/.config', 'norm', 'user', 'notexists')
# print optmap['notexists']
