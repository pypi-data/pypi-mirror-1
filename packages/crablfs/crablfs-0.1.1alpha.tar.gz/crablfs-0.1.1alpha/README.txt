crablfs: 基于用户的包管理系统 -- 用户简明手册
crablfs: User Based Package Management System -- User's Concise Manual

Author: 周鹏(Chowroc)
dATE: 2006-10-20
Email: chowroc.z@gmail.com

(1) 概述
crablfs 是基于用户的包管理系统，其基本原理是：系统中的每一个软件包都对应一个单独的用户，当安装一个包时便以这个用户的身份进行操作，这样该包在系统中生成的所有文件和用户的组权限都是该用户；同时所有的包用户都在一个 install 组中，并且令系统中的一些关键目录如 /usr/local, /usr/local/bin 等拥有 g+s,o+t 权限，并属于 install 组，以利于不同的包用户在这些目录中创建属于它们自己的文件和目录。

这种方法有诸多的好处。关于其原理的具体描述，请参见 LFS hints：
More Control and Package Management using Package Users (v1.2)
http://www.linuxfromscratch.org/hints/downloads/files/more_control_and_pkg_man.txt

基于这种原理，包管理器 userpack 是一个命令行接口，它拥有与 rpm, paco 这样的包管理器相似的命令行接口，以便完成包管理器所必须的若干操作。它只对一个包进行安装、卸载、查询等操作，或查询某个文件的包属主，或列出系统当前所有的包(rpm -qa)。安装的包名字和版本信息会加入指定的列表文件。

同时，每一个包属主都会有自己的 HOME 目录，默认放置在 /usr/src 下。在 HOME 目录中将存放这个包的源代码归档，和所有的补丁(包括一些其它的文件，不仅仅是 patch)以及相关的"安装配置信息文件"，其中包括包的信息，如用户/组名、版本号、源代码归档名、所有补丁和安装时执行的命令以及包在系统中建立的时间。

crablfs 脚本是一个批量处理脚本，可以说是一种 ALFS 的实现。它可以使用上述的列表文件，然后指定所有源代码归档和"安装配置信息文件"所在的目录，以实现自动化的处理；也可以指定一个与原系统的 HOME 前缀目录(/usr/src)相同的目录树，从而可以很方便的实现老系统到新系统的迁移 -- 这意味这你可以在任何情况下很快捷的建立你自己熟的个性化系统。

Linux 一个发行版本与另一个发行版本的根本区别，就在于包管理方式的不同。LFS 作为一个发行版本，实际上却并没有很完善的包管理系统，当然这也是 LFS 的灵活性所决定的，但作为日常使用，一个完善而简单的包管理系统是必要的。BLFS 文档中建议使用的就是 User Based Management，但只在 LFS hints 中提出了基本原理，这个原理极有创意，但作者提供的脚本并不是很完善，并没有形成一个自洽的系统，所以在下不惜现丑，先作出一个，希望起到抛砖引玉的作用。

(2) 安装 crablfs
为了保证 crablfs 自身也置于包管理控制之下，可以使用如下方法进行安装：
# export PYTHONPATH=/opt/lib/python2.4/site-packages
// sys.path 不受 PYTHONPATH 的影响
# tar xfz pexpect-2.1.tar.gz
# cd pexpect-2.1
# python setup.py install --prefix=/opt
# cd ..

# tar xfz crablfs-0.1.tar.gz
# cd crablfs-0.1
# vi userpack.dirs
// 定义所有的关键目录
// 这些目录将属于 install 组，并拥有 g+s,o+t 权限
/usr/local/
/usr/local/bin/
/usr/local/doc/
/usr/local/etc/
/usr/local/include/
/usr/local/info/
/usr/local/lib/
/usr/local/libexec/
/usr/local/man/
/usr/local/man/man1/
/usr/local/man/man2/
/usr/local/man/man3/
/usr/local/man/man4/
/usr/local/man/man5/
/usr/local/man/man6/
/usr/local/man/man7/
/usr/local/man/man8/
/usr/local/sbin/
/usr/local/share/
/usr/local/share/doc/
/usr/local/share/info/
/usr/local/share/locale/
/usr/local/share/man/
/usr/local/share/man/man1/
/usr/local/share/man/man2/
/usr/local/share/man/man3/
/usr/local/share/man/man4/
/usr/local/share/man/man5/
/usr/local/share/man/man6/
/usr/local/share/man/man7/
/usr/local/share/man/man8/
/usr/local/share/misc/
/usr/local/share/terminfo/
/usr/local/share/zoneinfo/
/usr/lib/python2.4/site-packages/
/usr/lib64/python2.4/site-packages/
// 请根据自己的需要调整
# python setup.py install --prefix=/opt
# cd ..

# /opt/bin/userpack init
# /opt/bin/userpack install -f /tmp/crablfs-0.1.tar.gz crablfs-0.1
crablfs> cmd tar xfz crablfs-0.1.tar.gz
crablfs> cmd cd crablfs-0.1
crablfs> cmd python setup.py install --install-scripts=/usr/local/bin
// 上面没有给出对 /usr/bin 进行初始化，所以重新指定
crablfs> cmd cd ..
crablfs> cmd rm -rf crablfs-0.1
crablfs> commit

# userpack install -f /tmp/pexpect-2.1.tar.gz pexpect-2.1
crablfs> cmd tar xfz pexpect-2.1.tar.gz
crablfs> cmd cd pexpect-2.1
crablfs> cmd python setup.py install
crablfs> cmd cd ..
crablfs> cmd rm -rf pexpect-2.1
crablfs> commit

# unset PYTHONPATH

(3) 包管理
包管理器：userpack

a. 安装一个包：
# userpack install $pkgname-$version
如
# userpack install rxvt-2.7.10
你可以使用自己的分类：
# userpack install meida.mplayer-1.0pre8
因为系统用户支持 "."

******
注意：
* 在 LFS 系统中并非如此，LFS 系统使用的 shadow 包只支持[-a-z0-9_]这些字符，所以我使用了自己编写的 shadow 模块直接写 /etc/passwd, /etc/group, /etc/shadow 和 /etc/gshadow 这些文件。

* 目前分类的功能还不强，没有经过严格的测试。
******

在上面的情况下，会执行默认的动作，即认为源代码的包和补丁已经在 HOME 目录中了，即 /usr/src/$pkgname，否则应该在参数中指定：
# userpack install -f /mnt/file/packages/rxvt-2.7.10.tar.gz rxvt-2.7.10
以将相应的包拷贝到 HOME 目录下。

这会启动一个交互式的命令行界面，这个命令行比较简单，只有为数不多的几个命令。实际上有点类似于一个 shell，在这里执行安装时所需要的命令，这可以非常灵活，根据不同的软件使用相应的命令即可。只是在命令之前要增加"cmd"标识，这样包管理器会记录相应的安装命令到其 HOME 目录下的 .config(安装配置信息文件)中。
crablfs> cmd tar xfz rxvt-2.7.10.tar.gz
crablfs> cmd cd rxvt-2.7.10
crablfs> cmd ./configure
crablfs> cmd make
crablfs> cmd make install
crablfs> cmd cd ..
crablfs> cmd rm -rf rxvt-2.7.10
crablfs> commit
需要说明的是，这时候你的当前用户是这个包用户，工作目录是这个包用户的主目录，所以会有权限限制(这也正是包用户系统的目的所在)。

在敲打命令时，你可以用 list 查看你键入的所有命令：
crablfs> list
0, tar xfz rxvt-2.7.10.tar.gz
1, cd rxvt-2.7.10
2, ./configure
3, make
4, make install

使用 rollback 可以清除所有的命令；如果只是想删除某个多余或错误的命令，使用 del N 即可。

最后必须 commit，这样所有的命令会记录到 .config 中，这个包的 $pkgname-$version 也会记录到列表文件中(默认 /usr/src/packages.list)，以表明这个包被安装了。如果运行命令失败而导致无法安装，如果不能排除错误，则以 quit 退出，这样相应的内容不会被记录。但通常归档、补丁等会被复制到 HOME 中。

如果带有其它补丁文件等：
# userpack install -f /mnt/file/packages/MPlayer-1.0per8.tar.bz2 \
	-p /mnt/file/packages/all-20060611.tar.bz2 \
	-p /mnt/file/packages/Blue-1.6.tar.bz2 \
	mplayer-1.0pre8
// all 是 mplayer 的 codecs，Blue 是 GUI Skin。

如果已经拥有以前安装包时遗留的配置信息文件，则可以用 -a|--auto 执行自动安装：
# userpack install -a rxvt-2.7.10
这时意味着 $HOME/.config 已经存在，否则指定之(-c|--profile)：
# userpack install -ac /mnt/packages/confiles/rxvt-2.7.10 rxvt-2.7.10

如果你已经将 /usr/src 刻录到了光盘上的 sources 目录，你也可以执行如下的自动安装：
# userpack install -as /mnt/dvdrom/sources rxvt-2.7.10

另外，安装源可以在网络上，如 ftp 或 ssh:
ssh://localhost/sources/mlterm-2.9.3.tar.gz
scp://localhost/sources/mlterm-2.9.3.tar.gz
上面两个是一个意思
ftp://localhost/pub/sources/mlterm-2.9.3.tar.gz
即：
# userpack install -f ftp://192.168.0.1/pub/sources/mlterm-2.9.3.tar.gz mlterm-2.9.3

******
如果没有指定 $pkgname-$version，则可以从包名(mlterm-2.9.3.tar.gz)解析出来。
******

如果一个包压缩档有问题，因为安装时会自动拷贝到 HOME，且下一次包管理器会先检查 HOME 中是否有此压缩包，如果已存在则默认不会拷贝新的，所以需要参数指定强制拷贝(-C|--copy-force)：
# userpack install -Caf libesmtp-1.0.3r1.tar.bz2

关于用户和组 ID，包管理器有自己的设定范围，默认值是从 1000 到 20000，可以在 /etc/login.defs 中定义：
PACK_UID_MIN	10000
PACK_UID_MAX	25000
PACK_GID_MIN	10000
PACK_GID_MAX	25000

b. 卸载：
# userpack remove rxvt-2.7.10

c. 列出所有受包报管理器控制的包：
# userpack packs
rxvt-2.7.10
mplayer-1.0pre8
crablfs-0.1
pexpect-2.1
mlterm-2.9.3

d. 查询一个文件属于那个包：
# userpack owner /usr/local/bin/mlterm
mlterm-2.9.3

e. 列出一个包拥有那些文件：
# userpack files pexpect-2.1
/usr/lib/python2.4/site-packages/fdpexpect.py
/usr/lib/python2.4/site-packages/pxssh.py
/usr/lib/python2.4/site-packages/pexpect.py
/usr/lib/python2.4/site-packages/pxssh.pyc
/usr/lib/python2.4/site-packages/pexpect.pyc
/usr/lib/python2.4/site-packages/fdpexpect.pyc

(4) 关于包及其版本的命名约定
即传递给包管理器的参数，形式为 $pkgname-$version，其 python re 的模式匹配为：
'^(?P<pkgname>(\w+-{0,1})+)(-(?P<version>(\d[\w]*[-\.])*\d[\w]*))'

即 $pkgname 部分为 part1[-part2][-part3][...]，每个 part 可以是[-a-zA-Z0-9_]，对开头字母没有限制，但建议使用字母开头；当遇到 -[0-9][a-zA-Z0-9_]\. 这样的模式时(-后跟这一个数字开头的串，在串后跟着一个'.'号的情况)，则将其作为 $version 部分，$version 部分也可以包含其他'-'号，但当有遇到非数字开头的部分时则结束 $version 部分，后面的内容忽略。

(5) ALFS
前面已经讲到，所有的命令都会记录到每个包 HOME 下的 .config 中，并且可以利用这些命令进行自动安装操作，所有可以使用一个批量处理脚本，根据在安装时生成的 packages.list 一次性安装所有的包。在这个设想上，我们可以建立一种 ALFS 的实现。

这个 ALFS 的实现与传统的 nALFS 和 jhalfs 的目标有所扩展，可以面向更个性化的系统，比如：我首先在一台主机上使用 step by step 的方法建立了一个 LFS 系统，那么下一次我可以利用这次生成的所有安装配置信息文件自动生成我需要的软件环境，与原来的系统保持一致；这意味着我可以实现多次的迁移，同时别人也可以利用我的安装配置信息文件为基础建立他自己的个性化系统。最终的目标当然还要实现跨平台的操作。

这个批量处理的脚本就是 crablfs 了。

******
目前只在 LFS 已经建立的情况下，对使用 crablfs 建立 BLFS 的情况进行了测试，因此还不能将 LFS 基本系统的所有包置于包管理系统控制之下。
******

首先需要通过工具链将 python 和 crablfs 都置于报管理控制之下：
# cd /blfs-sources
# tar xfj python-2.4.1.tar.bz2
# cd python-2.4.1
# patch -Np1 -i ../python-2.4.1-gdbm-1.patch
# ./configure --prefix=/opt --enable-shared
# make && make install
# cd ..
# rm -rf python-2.4.1
// 最好删除，否则可能会有问题

# export PYTHONPATH=/opt/lib/python2.4/site-packages
# tar xfz pexpect-2.1.tar.gz
# cd pexpect-2.1
# /opt/bin/python setup.py install --prefix=/opt
# cd ..
# rm -rf pexpect-2.1

# tar xfz crablfs-0.1.tar.gz
# cd crablfs-0.1
# cp userpack.dirs.blfs userpack.dirs
// 请根据系统具体情况调整你的目录列表
// 如果以后遇到目录权限的问题，只需要调整 /etc/userpack.dirs
// 然后运行 userpack init 即可
# /opt/bin/python setup.py install --prefix=/opt

# /opt/bin/userpack init
# /opt/bin/userpack install -f python-2.4.1.tar.bz2 -p
# python-2.4.1-gdbm-1.patch python-2.4.1
crablfs> cmd tar xfj python-2.4.1.tar.bz2
crablfs> cmd cd python-2.4.1
crablfs> cmd ./configure --prefix=/usr --enable-shared
crablfs> cmd make
crablfs> cmd make install
crablfs> cmd cd ..
crablfs> cmd rm -rf python-2.4.1
crablfs> commit

# /opt/bin/userpack install -f crablfs-0.1.tar.gz crablfs-0.1
crablfs> cmd tar xfz crablfs-0.1.tar.gz
crablfs> cmd cd crablfs-0.1
crablfs> cmd python setup.py install --install-scripts=/usr/local/bin
crablfs> cmd cd ..
crablfs> cmd rm -rf crablfs-0.1
crablfs> commit

# userpack install -f pexpect-2.1.tar.gz pexpect-2.1
crablfs> cmd tar xfz pexpect-2.1.tar.gz
crablfs> cmd cd pexpect-2.1
crablfs> cmd python setup.py install
crablfs> cmd cd ..
crablfs> cmd rm -rf pexpect-2.1
crablfs> commit

# unset PYTHONPATH
# userpack packs
python-2.4.1
crablfs-0.1
pexpect-2.1

按照相同的方法，使用 userpack 又安装了若干包：
# userpack packs
# cat /usr/src/packages.list
python-2.4.1
crablfs-0.1
pexpect-2.1
openssl-0.9.7g
cracklib-2.8.3
Linux-PAM-0.80
iptables-1.3.3
gnupg-1.4.1
pcre-6.1
libxml-1.8.17
libxml2-2.6.20
libxslt-1.1.14
gdbm-1.8.3
pkg-config-0.19
glib2-2.6.4
expat-1.95.8
libesmtp-1.0.3r1
lzo-2.01
libusb-0.1.10a
libjpeg-6b
libpng-1.2.8
which-2.16

# mv /usr/src/packages.list /blfs-sources/
# config.copy /usr/src
// 在当前目录下生成一个 profiles 目录，里面会有所有 /usr/src
// 下安装配置信息文件的拷贝
// 这个 shell 脚本不会安装，可以在包的压缩档中找到
# mv profiles /blfs-sources
# crablfs -t alfs \
	-C /blfs-sources/profiles/ \
	-F /blfs-sources/ \
	/blfs-sources/packages.list

另外，如果你之前安装过一个系统，并且将 /usr/src 全部拷贝下来了 -- 比如刻录到了 DVD-R 上，你也可以这样做：
# crablfs -t crablfs[/default] \
	-s /mnt/dvdrom/sources/ \
	/mnt/dvdrom/sources/packages.list

crablfs 会记录当前成功安装的包的名字到 /var/log/crablfs/.mark 中。因为各个包之间常常有前后依赖关系，所以如果某一步出错，则 crablfs 进程会终止，后续包不会安装。待排除错误后，重新运行原来的命令，则可以从断点开始执行。

所以如果 .mark 指向 packages.list 中的最后一个包，则 crablfs 什么都不会做。请注意作出调整。

另外，crablfs 会先校验 packages.list 文件，如果其中包含非法的包名等会使 crablfs 终止而不进行任何安装操作；如果 .mark 中的包名不在 packages.list 中，会得到 "x not in list" 报错，你可以作出相应的调整，通常删除 .mark 即可。

从目前的情况看，还没有遇到太多权限问题，且都可以通过调整安装时的参数来避免。可能需要对 chown, chmod, chgrp, install 这些程序编写包裹器，但目前还没有看到必须之处。这个再看以后测试的情况来定吧。

(6) 下一步的计划
* BLFS 中 crablfs 工具链建立脚本(shell script)
* 增加 upgrade 部分
* 增加 gettext 国际化支持
* 每个包完整的描述信息
* PyUnit 单元测试
* cmdline 增加 do 命令，执行但不记录
* 增强 cmdline 的命令补全功能
* 增加 cmdline 读取 .config 历史命令和修改指定命令的功能
* 令 cmdline 可以执行 root 命令(利用进程间通信或利用 sudo)？
* cmdline 的多行模式，如 cat > file <<"EOF"？
* 最好有一个命令编辑器
* 对 packages.list 增加文件锁
* 将 .config 改为 $pkgname-$version 形式
* 对 LFS 基本系统实现控制
* 增强跨平台支持：
	增加环境变量和 cmdline 变量支持以适应不同的 $ARCH 和 $LOCALE
* 增加对多个安装源的支持
* 增强包分类机制
* 增加完整性校验
* 增强配置解析: Plain Tree & XML
* 考虑依赖性检查问题, reinstall 问题？
* 更完善的文档：内部文档、设计文档和手册
* 使 userpack.dir 支持指定深度的递归，如 /usr/share/locale/ -r2
* userpack init 自动删除 userpack.dirs 中被删除的条目目录

**************************************************************************
这是我第一次发布自己的作品，由于水平有限，其中还有许多不尽人意之处，我会在以后努力的改进和完善，同时希望大家不吝赐教，尽可能给予我反馈意见。如愿意，您也可以在 GPL 2.0 协议及其后续版本下随意改进代码。

希望这个程序对大家有用，也希望由此可以做出一个真正通用型的、方便的 LFS 发行版。

谢谢！
**************************************************************************

crablfs Copyright (c) 2006, 周鹏(chowroc.z@gmail.com)

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
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
