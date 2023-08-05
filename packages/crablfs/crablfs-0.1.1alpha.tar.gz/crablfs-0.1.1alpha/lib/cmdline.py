#!/usr/bin/python
# -*- encoding: utf-8 -*-

"""Author: 周鹏
Date: 2006-10-20
Email: chowroc.z@gmail.com

crablfs 的交互式命令解释器
主要在 userpack 的 install 时使用

需要一个变量赋值和读取功能(未实现)，如执行：
crablfs> cmd cp -Rv include/asm-$arch/* /usr/include/asm
比
crablfs> cmd cp -Rv include/asm-i386/* /usr/include/asm
要好

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
				# 使用 os.execvp() 将需要编写管道和重定向代码
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
	# *** 最好用 self.error_cmd_no 指向错误的命令数 ***
	# *** 如果这个命令没有被删除，则以失败退出？ ***

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
	# 只退出循环而不退出进程
	# 参见 cmd 源代码 cmdloop 和 postcmd 函数

# cli = cmdline()
# cli.cmdloop()
# print "after cmdloop"
# cli.do_command("ls")
