#!/usr/bin/python
# -*- encoding: utf-8 -*-

"""Author: 周鹏(chowroc)
Date: 2006-12-01
Email: chowroc.z@gmail.com

LFS useradd/groupadd only support lowercase,
and I need the '.' in the username for package classification

order:
groupadd --> useradd --> [_join(group, user)]
   |            |             |
/etc/group   /etc/passwd  /etc/group

If user/group exists, return the uid/gid


crablfs Copyright (c) 2006 周鹏(chowroc.z@gmail.com)

This file is part of crablfs.

crablfs is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

crablfs is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA"""

import re
import os
import pwd
import grp
import time
from crablfs import filetools

legal = '[^-\w\.]'
UID_MIN = 1000
UID_MAX = 20000
# 19999 < 20000, follows as the same
GID_MIN = 1000
GID_MAX = 20000
# for var in ['UID_MIN', 'UID_MAX', 'GID_MIN', 'GID_MAX']:
#	cmd = "grep 'PACK_%s' /etc/login.defs | sed -n '1p'" % var
#	tmp = os.popen(cmd).read().strip()
#	try:
#		n = int(re.split('[\t\s]+', tmp)[1])
#		exec "%s = %s" % (var, n)
#	except IndexError:
#		exec "%s = %s" % (var, var)
ADM_MIN = 950
ADM_MAX = 1000

def __user_compare(user1, user2):
	if user1[2] < user2[2]: return -1
	elif user1[2] > user2[2]: return 1
	else: return 0

def groupadd(group, type='normal'):
	if type == 'sysadm':
		gid_min = ADM_MIN
		gid_max = ADM_MAX
	else:
		gid_min = GID_MIN
		gid_max = GID_MAX
	if not group:
		raise "groupadd: Empty group name"
	mo = re.search(legal, group)
	if mo:
		raise "groupadd: Invalid group name '%s'" % group
	try:
		gid = grp.getgrnam(group)[2]
		if gid < gid_min:
			raise "groupadd: '%s' is not a package group" % group
		return gid
	except KeyError:
		pass
	# 如果组已存在，则直接返回 GID
	groups = grp.getgrall()
	groups.sort(__user_compare, reverse=True)
	# 按 GID 降序排列
	for i in range(len(groups)):
		if groups[i][2] < gid_max:
			max = groups[i][2]
			break
	if max < gid_min: gid = gid_min
	elif max + 1 == gid_max: raise "package groups' stack full."
	else: gid = max + 1
	file = open('/etc/group', 'a')
	file.write("%s:x:%s:\n" % (group, gid))
	file.close()
	gshadow(group)
	return gid

def useradd(user, group='', groups=[], home='', shell='/bin/bash'):
	if not user:
		raise "useradd: Empty user name"
	if type(groups) is not list:
		raise "useradd: Invalid groups '%s'" % groups
	if not home: home = '/home/%s' % user
	mo = re.search(legal, user)
	if mo:
		raise "useradd: Invalid user name '%s'" % user
	if not group: group = user
	gid = groupadd(group)
	try:
		uid = pwd.getpwnam(user)[2]
		if uid < UID_MIN:
			raise "useradd: '%s' is not a package user" % user
		### Need a _join() checking ! ###
		for G in groups: _join(G, user)
		return uid, gid
	except KeyError:
		users = pwd.getpwall()
		users.sort(__user_compare, reverse=True)
		for i in range(len(users)):
			if users[i][2] < UID_MAX:
				max = users[i][2]
				break
		if max < UID_MIN: uid = UID_MIN
		elif max + 1 == UID_MAX: raise "package users' stack full."
		else: uid = max + 1
		file = open('/etc/passwd', 'a')
		file.write("%s:x:%s:%s::%s:%s\n" % (user, uid, gid, home, shell))
		file.close()
		shadow(user)
		if not os.path.exists(home): os.mkdir(home)
		if os.path.isdir(home):
			os.chown(home, uid, gid)
		else:
			raise "useradd: HOME '%s' exists but not a directory" % home
		for G in groups: _join(G, user)
		return uid, gid

def _join(group, user):
	"Add user to a group"
	try:
		notex = 'group: %s' % group
		record = grp.getgrnam(group)
		notex = 'user: %s' % user
		pwd.getpwnam(user)
	except KeyError:
		raise "useradd: Can't join '%s' to '%s', '%s' not exists" % (user, group, notex)
	record = list(record)
	if user in record[3]: return
	# Have joined!
	oline = ','.join(record[3])
	users = oline
	record[3] = oline
	record[2] = str(record[2])
	oline = ':'.join(record)
	if users:
		rline = oline + ',' + user
	else:
		rline = oline + user
		# No ',' is needed for the first time, otherwise raise problems the next time
	# filetools.pull_list('/etc/group', oline)
	# filetools.push_list('/etc/group', rline)
	file = open('/etc/group', 'r+')
	L = file.readlines()
	i = L.index(oline + '\n')
	L[i] = rline + '\n'
	file.seek(0)
	file.truncate()
	file.writelines(L)
	file.close()

def shadow(user):
	days = int(time.time() / 86400)
	file = open('/etc/shadow', 'a')
	file.write("%s:!!:%s:0:99999:7:::\n" % (user, days))
	file.close()

def gshadow(group):
	file = open('/etc/gshadow', 'a')
	file.write("%s:!::" % group)
	file.close()
