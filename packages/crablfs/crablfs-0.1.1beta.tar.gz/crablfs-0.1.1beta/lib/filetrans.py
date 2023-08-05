#!/usr/bin/python
# -*- encoding: UTF-8 -*-

"""Author: ÖÜÅô
Date: 2006-12-01
Email: chowroc.z@gmail.com

Ö§³Ö¶àÖÖÐ­ÒéµÄÎÄ¼þ´«ÊäÄ£¿é

filetrans $SRC $DST
Ä¿Ç° $DST ±ØÐë´æÔÚÇÒÊÇÄ¿Â¼
Ò²Ã»ÓÐÄ£Ê½Æ¥Åä¹¦ÄÜ

crablfs Copyright (c) 2006 ÖÜÅô(chowroc.z@gmail.com)

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

import os
import re
import sys
import time
import getopt
import shutil
import ftplib

USER = os.environ['USER']
HOME = os.environ['HOME']

class filetrans:
	def __init__(self, user=USER, passwd='', host='localhost', 
	remote='', locale='.'):
		self.user = user
		self.host = host
		self.passwd = passwd
		self.remote = os.path.normpath(remote)
		self.locale = os.path.normpath(locale)
	def getfile(self, remote='', locale='', timeout=600, force=False):
		if remote: self.remote = os.path.normpath(remote)
		if locale: self.locale = os.path.normpath(locale)
		if not self.remote:
			strerr = "%s: No remote file given" % program
			sys.stderr.write("%s\n" % strerr)
		if not os.path.isdir(self.locale):
			strerr = "%s: No local directory %s found" % (program, self.locale)
			print >> sys.stderr, strerr
			sys.exit(1)
		# *** self.locale: ÊÇÆÕÍ¨ÎÄ¼þ£¿ÊÇÄ¿Â¼£¿²»´æÔÚ£¿ ***
		# *** »ò£ºÊÇ´æÔÚÔòµ±×öÄ¿Â¼£¬»ò²»´æÔÚ ***
		# *** ²»´æÔÚ£ºself.rename ***
		# *** Èç¹ûÕâÑùÓ¦¸Ã·µ»ØÄ¿±ê´® ***
		
		fbname = os.path.basename(self.remote)
		destin = '%s/%s' % (self.locale, fbname)
		if os.path.exists(destin):
			if not force:
				strerr = "%s: Destination: %s exists" % (program, destin)
				print >> sys.stderr, strerr
				sys.exit(1)
			else:
				if os.path.isdir(destin):
					shutil.rmtree(destin)
				else:
					os.remove(destin)
		# scp ²»»á×÷³öÅÐ¶Ï£¬ËùÒÔÔÚÕâÀïÏÈÅÐ¶Ï
		self._getfile(timeout)
	def _getfile(self, timeout): pass

class filetransEx:
	def __init__(self, strerr):
		self.strerr = strerr
	def logerror(self):
		print self.strerr
		# sys.stderr.write("%s\n" % self.strerr)

class filetrans_copy(filetrans):
	def getfile(self, remote='', locale='', timeout=600, force=False):
		if remote: self.remote = os.path.normpath(remote)
		if locale: self.locale = os.path.normpath(locale)
		fbname = os.path.basename(self.remote)
		self.destin = os.path.join(self.locale, fbname)
		self.destin = os.path.abspath(self.destin)
		self.remote = os.path.abspath(self.remote)
		# Only the local coping can use 'abspath'!
		# if os.path.samefile(self.remote, self.destin):
		# 	return
		if self.remote == self.destin: # Èç¹ûÊÇÍ¬Ò»¸öÎÄ¼þ
			return
		else:
			filetrans.getfile(self, timeout=timeout, force=force)
			# self._getfile(self, timeout=timeout, force=force)
	def _getfile(self, timeout):
		### print "DEBUG: filetrans_copy._getfile"
		if os.path.isdir(self.remote):
			shutil.copytree(self.remote, self.destin)
		else:
			shutil.copy(self.remote, self.locale)
filetrans_file = filetrans_copy

class filetrans_ftp(filetrans):
	def __init__(self, user='anoymous', passwd='', host='localhost',
		remote='', locale='.'):
		filetrans.__init__(self, user, passwd, host, remote, locale)
	def _getfile(self, timeout):
		self.__ftp_get(self.remote, self.locale)
	def __ftp_get(self, rdir, ldir):
		ftp = ftplib.FTP(self.host, self.user, self.passwd)
		ftp.login()
		fbname = os.path.basename(rdir)
		for sub in ftp.nlst(rdir):
			if sub == rdir:
			# is regular file
				rfile = sub
				fbname = os.path.basename(sub)
				lfile_o = open('%s/%s' % (ldir, fbname), 'wb')
				ftp.retrbinary('RETR %s' % rfile, lfile_o.write)
				lfile_o.close()
			else:
			# is directory
				ldir = '%s/%s' % (ldir, fbname)
				os.mkdir(ldir)
				rdir = sub
				self.__ftp_get(rdir, ldir)

class filetrans_ssh_pexpect(filetrans):
	def _getfile(self, timeout):
		cmd = 'scp -rpC %s@%s:%s %s/' % (self.user, self.host, self.remote, self.locale)
		# *** Èç¹ûÎ´¿½±´µ½ÎÄ¼þ£¬ÈçÔ¶¶ËÎÄ¼þ¸ù±¾²»´æÔÚ£¬ÕâÀïÃ»ÓÐÅ×³öÒì³££¿ ***
		self.__pexpect(cmd, timeout)

	def __pexpect(self, cmd, timeout=600):
		import pexpect
		T = time.time()
		try:
			ssh = pexpect.spawn(cmd, timeout=timeout)
			index = -1
			while index < 2:
				index = ssh.expect([
					'continue connecting', 
					'password: ', 
					pexpect.EOF, 
					pexpect.TIMEOUT	])
				if index == 0:
					ssh.sendline('yes')
				elif index == 1:
					ssh.sendline(self.passwd)
		except pexpect.EOF:
			ssh.close()
			outstr = 'filetrans takes %d seconds' % int(time.time() - T)
			print outstr
		except pexpect.TIMEOUT:
		# *** ÎÞ·¨²¶×½µ½Õâ¸öÒì³££¿£¡ ***
			ssh.close()
			raise filetransEx('%s: pexpect TIMEOUT %d seconds' % (program, timeout))
		except ExceptionPexpect:
			raise filetransEx('filetrans_scp_pexpect failed, "%s"' % cmd)
		ssh.expect(pexpect.EOF)
		ssh.close()
		outstr =  'filetrans: [[32m%s[00m] takes %d seconds' % (cmd, int(time.time() - T))
		print outstr
filetrans_scp= filetrans_ssh_pexpect

def parse(remote):
	# pregexp = r"((?P<proto>\w+)://){0,1}(?P<host>(\w+\.{0,1})+){0,1}(?P<file>/.+){1}"
	pregexp = r"((?P<proto>\w+)://((?P<user>[\w\.]+)@'(?P<passwd>.+)':){0,1}){0,1}(?P<host>(\w+\.{0,1})+/){0,1}(?P<file>/{0,1}.*){1}"
	try:
		mo = re.match(pregexp, remote)
		proto = mo.group('proto')
		user = mo.group('user')
		passwd = mo.group('passwd')
		host = mo.group('host')
		fname = mo.group('file')
		return proto, user, passwd, host, fname
	except AttributeError:
		strerr = "%s: Not a valid file location: %s" % (program, remote)
		sys.stderr.write("%s\n" % strerr)
		sys.exit(1)

def build(user='', passwd='', remote='', locale='.'):
	proto, utmp, ptmp, host, remote = parse(remote)
	if utmp: user = utmp
	if ptmp: passwd = ptmp
	import filetrans
	try:
		ftclass = getattr(filetrans, 'filetrans_%s' % proto, filetrans_copy)
	except AttributeError:
		strerr = "%s: Not a valid protocol: %s" % (program, proto)
		sys.stderr.write("%s\n" % strerr)
		sys.exit(1)
	fto = ftclass(user, passwd, host, remote, locale)
	return fto

if __name__ == '__main__':
	program = os.path.basename(sys.argv[0])
	location = os.path.dirname(sys.argv[0])
	usage = """usage: filetrans [OPTIONS] $SOURCE $DESTINATION
	-u $user
	-p $password
	-t $timeout
	-f, force
	-G, GETFILE(default)
	-P, PUTFILE
	-h"""
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'u:p:t:fG:P:', 
			['user=', 'password=', 'timeout', 'force', 'get', 'put', 'help'])
		user = ''
		passwd = ''
		source = args[0]
		destin = args[1]
		timeout = 600
		action = 'getfile'
		remote = source
		locale = destin
		force = False
		for o, v in opts:
			if o in ['-u', '--user']:
				user = v
			elif o in ['-p', '--password']:
				passwd = v
			elif o in ['-t', '--timeout']:
				timeout = int(v)
			elif o in ['-f', '--force']:
				force = True
			elif o in ['-D', '--get']:
				action = 'getfile'
				remote = source
				locale = destin
			elif o in ['-U', '--put']:
				action = 'putfile'
				remote = destin
				locale = source
		fto = build(user, passwd, remote, locale)
		exec "fto.%s(timeout=%s, force=%s)" % (action, timeout, force)
	except getopt.GetoptError, (errno, errstr):
		strerr = "%s: getopt error: %s, %s" % (program, errno, errstr)
		sys.stderr.write("%s\n", strerr)
		print usage
		sys.exit(1)
	except IndexError, errstr:
		strerr = "%s: Lack of source or destination: %s" % (program, errstr)
		sys.stderr.write("%s\n" % strerr)
		print usage
		sys.exit(1)
	# except filetransEx, ftEx:
	#	ftEx.logerror()
else:
	program = __name__
