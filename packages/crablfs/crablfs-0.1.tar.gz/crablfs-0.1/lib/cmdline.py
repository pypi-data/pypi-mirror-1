#!/usr/bin/python
# -*- encoding: utf-8 -*-

"""Author: ����
Date: 2006-10-20
Email: chowroc.z@gmail.com

crablfs �Ľ���ʽ���������
��Ҫ�� userpack �� install ʱʹ��

��Ҫһ��������ֵ�Ͷ�ȡ����(δʵ��)����ִ�У�
crablfs> cmd cp -Rv include/asm-$arch/* /usr/include/asm
��
crablfs> cmd cp -Rv include/asm-i386/* /usr/include/asm
Ҫ��

crablfs Copyright (c) 2006 ����(chowroc.z@gmail.com)

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

import cmd
from shlex import split
import os, sys

class cmdline(cmd.Cmd):
	def __init__(self, stdin=sys.stdin, stdout=sys.stdout):
		cmd.Cmd.__init__(self, 'tab', stdin, stdout)
		self.prompt = 'crablfs> '
		self.commands = []
		self.builtins = ['cd']
		self.stop = 0
		self.success = 0

	def do_shell(self, args): pass

	def build(self, command, argv):
		strerr = ""
		try:
			if command == 'cd':
				os.chdir(argv[1])
			else:
				strerr = "Invalid builtin command"
		except IndexError:
			strerr = "Invalid arguments for builtin command: %s" % command
		except OSError, (errno, errstr):
			strerr = "cmdline: %d, %s" % (errno, errstr)
		if strerr:
			sys.stderr.write("%s\n" % strerr)
			return 0
		return 1

	def do_command(self, args):
		success = 1
		try:
			argv = split(args)
			command = argv[0]
			if command in self.builtins:
				success = self.build(command, argv)
			else:
				# pid = os.fork()
				# if pid == 0:
				#	os.execvp(command, argv)
				#	success = 0
				# else: os.wait()
				success = (not os.system(args))
				# ʹ�� os.execvp() ����Ҫ��д�ܵ����ض������
		except IndexError:
			strerr = "No command given"
			sys.stderr.write("%s\n" % strerr)
		if success:
			self.commands.append(args)
		else:
			strerr = "Invalid command"
			sys.stderr.write("%s\n" % strerr)
		return success
	do_cmd = do_command
	# *** ����� self.error_cmd_no ָ������������ ***
	# *** ����������û�б�ɾ��������ʧ���˳��� ***

	def do_list(self, args):
		for i in range(len(self.commands)):
			print "%d, %s" % (i, self.commands[i])
	do_lst = do_list

	def do_delete(self, args):
		try:
			i = int(split(args)[0])
			print "delete: %d, %s" % (i, self.commands[i])
			self.commands.pop(i)
		except IndexError:
			strerr = "Index out of range, 'list' to show the commands"
			sys.stderr.write("%s\n" % strerr)
		except ValueError:
			strerr = "'list' to lookup the command's num that u want to del"
			sys.stderr.write("%s\n" % strerr)
	do_del = do_delete

	def do_commit(self, args): self.stop = 1; self.success = 1
	do_cmt = do_commit
	def do_rollback(self, args=""): self.commands = []
	def do_quit(self, args): self.do_rollback(); self.stop = 1
	def postcmd(self, stop, line): return self.stop
	# ֻ�˳�ѭ�������˳�����
	# �μ� cmd Դ���� cmdloop �� postcmd ����

# cli = cmdline()
# cli.cmdloop()
# print "after cmdloop"
# cli.do_command("ls")
