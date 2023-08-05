#!/usr/bin/python
# -*- encoding: utf-8 -*-

"""Author: 周鹏(Chowroc)
Date: 2006-10-20
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

illegal = '[^-\w\.]'
UID_MIN = 1000
UID_MAX = 20000
GID_MIN = 1000
GID_MAX = 20000
for var in ['UID_MIN', 'UID_MAX', 'GID_MIN', 'GID_MAX']:
	cmd = "grep 'PACK_%s' /etc/login.defs | sed -n '1p'" % var
	tmp = os.popen(cmd).read().strip()
	try:
		n = int(re.split('[\t\s]+', tmp)[1])
		exec "%s = %s" % (var, n)
	except IndexError:
		exec "%s = %s" % (var, var)

def __user_compare(user1, user2):
	if user1[2] < user2[2]: return -1
	elif user1[2] > user2[2]: return 1
	else: return 0

def groupadd(group):
	if not group:
		raise "groupadd: Empty group name"
	mo = re.search(illegal, group)
	if mo:
		raise "groupadd: Invalid group name '%s'" % group
	try:
		gid = grp.getgrnam(group)[2]
		if gid < GID_MIN:
			raise "groupadd: '%s' is not a package group" % group
		return gid
	except KeyError: pass
	groups = grp.getgrall()
	groups.sort(__user_compare, reverse=True)
	for i in range(len(groups)):
		if groups[i][2] < GID_MAX:
			maxgid = groups[i][2]
			break
	if maxgid < GID_MIN: gid = GID_MIN
	else: gid = maxgid + 1
	file = open('/etc/group', 'a')
	file.write("%s:x:%s:\n" % (group, gid))
	file.close()
	gshadow(group)
	return gid

def useradd(user, group='', groups=[], home='', shell='/bin/bash'):
	if not user:
		raise "useradd: Empty user name"
	if not home: home = '/home/%s' % user
	mo = re.search(illegal, user)
	if mo:
		raise "useradd: Invalid user name '%s'" % user
	if not group: group = user
	gid = groupadd(group)
	try:
		uid = pwd.getpwnam(user)[2]
		if uid < UID_MIN:
			raise "useradd: '%s' is not a package user" % user
		return uid, gid
	except KeyError: pass
	if type(groups) is not list:
		raise "useradd: Invalid groups '%s'" % groups

	users = pwd.getpwall()
	users.sort(__user_compare, reverse=True)
	for i in range(len(users)):
		if users[i][2] < UID_MAX:
			maxuid = users[i][2]
			break
	if maxuid < UID_MIN: uid = UID_MIN
	else: uid = maxuid + 1
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
	try:
		notex = 'group: %s' % group
		record = grp.getgrnam(group)
		notex = 'user: %s' % user
		pwd.getpwnam(user)
	except KeyError:
		raise "useradd: Can't join '%s' to '%s', '%s' not exists" % (user, group, notex)
	record = list(record)
	oline = ','.join(record[3])
	record[3] = oline
	record[2] = str(record[2])
	oline = ':'.join(record)
	rline = oline + ',' + user
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
