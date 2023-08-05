#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Author: ����
# Date: 2006-10-20
# Email: chowroc.z@gmail.com

import os
import sys
import shutil

def find_list(filename, inew):
	try:
		if type(inew) is not str:
			strerr = "%s is not a valid LIST item string" % inew
			print >> sys.stderr, strerr
			raise "find_list_error"
		file = open(filename, 'r')
		for item in file.readlines():
			item = item.strip()
			if inew == item: return
		raise "find_list_error"
	except Exception, (errno, errstr):
		strerr = "find list faild: %d, %s" % (errno, errstr)
		print >> sys.stderr, strerr
		raise "find_list_error"

def push_list(filename, inew):
	"���һ����Ŀ�����б��ļ��У�������"
	try:
		if type(inew) is not str:
			strerr = "%s is not a valid LIST item string" % inew
			sys.stderr.write("%s\n" % strerr)
			return
		open(filename, 'a')  # touch $filename
		if os.path.isfile(filename): mode = 'r+'
		# else: mode = 'w'
		file = open(filename, mode)
		for item in file.readlines():
			item = item.strip()
			if inew == item: return
			# ����Ѿ�������ʲôҲ����
		file.write("%s\n" % inew)
		file.close()
	except Exception, (errno, errstr):
		strerr = "push list faild: %d, %s" % (errno, errstr)
		sys.stderr.write("%s\n" % strerr)

def pull_list(filename, inew):
	"���б��ļ���ɾ��һ����Ŀ"
	try:
		if type(inew) is not str:
			strerr = "%s is not a valid LIST item string" % inew
			sys.stderr.write("%s\n" % strerr)
			raise "pull_list_error"
		file = open(filename, 'r+')
		items = file.readlines()
		i = -1
		for item in items:
			itmp = item.strip()
			if inew == itmp:
				i = items.index(item)
				items.pop(i)
				break
		if i < 0:
			strerr = "LIST item: %s was not found" % inew
			sys.stderr.write("%s\n" % strerr)
			raise "pull_list_error"
		else:
			file.seek(0)
			file.truncate()
			file.writelines(items)
		file.close()
	except Exception, (errno, errstr):
		strerr = "pull list faild: %d, %s" % (errno, errstr)
		sys.stderr.write("%s\n" % strerr)
		raise "pull_list_error"

def rmtree(pathname):
	if os.path.isdir(pathname):
		shutil.rmtree(pathname)
	else:
		os.remove(pathname)

def copytree(pathname):
	if os.path.isdir(pathname):
		shutil.copytree(pathname)
	else:
		shutil.copy(pathname)
