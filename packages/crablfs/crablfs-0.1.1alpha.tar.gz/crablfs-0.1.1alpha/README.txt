crablfs: �����û��İ�����ϵͳ -- �û������ֲ�
crablfs: User Based Package Management System -- User's Concise Manual

Author: ����(Chowroc)
dATE: 2006-10-20
Email: chowroc.z@gmail.com

(1) ����
crablfs �ǻ����û��İ�����ϵͳ�������ԭ���ǣ�ϵͳ�е�ÿһ�����������Ӧһ���������û�������װһ����ʱ��������û�����ݽ��в����������ð���ϵͳ�����ɵ������ļ����û�����Ȩ�޶��Ǹ��û���ͬʱ���еİ��û�����һ�� install ���У�������ϵͳ�е�һЩ�ؼ�Ŀ¼�� /usr/local, /usr/local/bin ��ӵ�� g+s,o+t Ȩ�ޣ������� install �飬�����ڲ�ͬ�İ��û�����ЩĿ¼�д������������Լ����ļ���Ŀ¼��

���ַ��������ĺô���������ԭ��ľ�����������μ� LFS hints��
More Control and Package Management using Package Users (v1.2)
http://www.linuxfromscratch.org/hints/downloads/files/more_control_and_pkg_man.txt

��������ԭ���������� userpack ��һ�������нӿڣ���ӵ���� rpm, paco �����İ����������Ƶ������нӿڣ��Ա���ɰ�����������������ɲ�������ֻ��һ�������а�װ��ж�ء���ѯ�Ȳ��������ѯĳ���ļ��İ����������г�ϵͳ��ǰ���еİ�(rpm -qa)����װ�İ����ֺͰ汾��Ϣ�����ָ�����б��ļ���

ͬʱ��ÿһ���������������Լ��� HOME Ŀ¼��Ĭ�Ϸ����� /usr/src �¡��� HOME Ŀ¼�н�����������Դ����鵵�������еĲ���(����һЩ�������ļ����������� patch)�Լ���ص�"��װ������Ϣ�ļ�"�����а���������Ϣ�����û�/�������汾�š�Դ����鵵�������в����Ͱ�װʱִ�е������Լ�����ϵͳ�н�����ʱ�䡣

crablfs �ű���һ����������ű�������˵��һ�� ALFS ��ʵ�֡�������ʹ���������б��ļ���Ȼ��ָ������Դ����鵵��"��װ������Ϣ�ļ�"���ڵ�Ŀ¼����ʵ���Զ����Ĵ���Ҳ����ָ��һ����ԭϵͳ�� HOME ǰ׺Ŀ¼(/usr/src)��ͬ��Ŀ¼�����Ӷ����Ժܷ����ʵ����ϵͳ����ϵͳ��Ǩ�� -- ����ζ����������κ�����ºܿ�ݵĽ������Լ���ĸ��Ի�ϵͳ��

Linux һ�����а汾����һ�����а汾�ĸ������𣬾����ڰ�����ʽ�Ĳ�ͬ��LFS ��Ϊһ�����а汾��ʵ����ȴ��û�к����Ƶİ�����ϵͳ����Ȼ��Ҳ�� LFS ��������������ģ�����Ϊ�ճ�ʹ�ã�һ�����ƶ��򵥵İ�����ϵͳ�Ǳ�Ҫ�ġ�BLFS �ĵ��н���ʹ�õľ��� User Based Management����ֻ�� LFS hints ������˻���ԭ�����ԭ���д��⣬�������ṩ�Ľű������Ǻ����ƣ���û���γ�һ����Ǣ��ϵͳ���������²�ϧ�ֳ�������һ����ϣ������ש��������á�

(2) ��װ crablfs
Ϊ�˱�֤ crablfs ����Ҳ���ڰ��������֮�£�����ʹ�����·������а�װ��
# export PYTHONPATH=/opt/lib/python2.4/site-packages
// sys.path ���� PYTHONPATH ��Ӱ��
# tar xfz pexpect-2.1.tar.gz
# cd pexpect-2.1
# python setup.py install --prefix=/opt
# cd ..

# tar xfz crablfs-0.1.tar.gz
# cd crablfs-0.1
# vi userpack.dirs
// �������еĹؼ�Ŀ¼
// ��ЩĿ¼������ install �飬��ӵ�� g+s,o+t Ȩ��
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
// ������Լ�����Ҫ����
# python setup.py install --prefix=/opt
# cd ..

# /opt/bin/userpack init
# /opt/bin/userpack install -f /tmp/crablfs-0.1.tar.gz crablfs-0.1
crablfs> cmd tar xfz crablfs-0.1.tar.gz
crablfs> cmd cd crablfs-0.1
crablfs> cmd python setup.py install --install-scripts=/usr/local/bin
// ����û�и����� /usr/bin ���г�ʼ������������ָ��
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

(3) ������
����������userpack

a. ��װһ������
# userpack install $pkgname-$version
��
# userpack install rxvt-2.7.10
�����ʹ���Լ��ķ��ࣺ
# userpack install meida.mplayer-1.0pre8
��Ϊϵͳ�û�֧�� "."

******
ע�⣺
* �� LFS ϵͳ�в�����ˣ�LFS ϵͳʹ�õ� shadow ��ֻ֧��[-a-z0-9_]��Щ�ַ���������ʹ�����Լ���д�� shadow ģ��ֱ��д /etc/passwd, /etc/group, /etc/shadow �� /etc/gshadow ��Щ�ļ���

* Ŀǰ����Ĺ��ܻ���ǿ��û�о����ϸ�Ĳ��ԡ�
******

�����������£���ִ��Ĭ�ϵĶ���������ΪԴ����İ��Ͳ����Ѿ��� HOME Ŀ¼���ˣ��� /usr/src/$pkgname������Ӧ���ڲ�����ָ����
# userpack install -f /mnt/file/packages/rxvt-2.7.10.tar.gz rxvt-2.7.10
�Խ���Ӧ�İ������� HOME Ŀ¼�¡�

�������һ������ʽ�������н��棬��������бȽϼ򵥣�ֻ��Ϊ������ļ������ʵ�����е�������һ�� shell��������ִ�а�װʱ����Ҫ���������Էǳ������ݲ�ͬ�����ʹ����Ӧ������ɡ�ֻ��������֮ǰҪ����"cmd"��ʶ�����������������¼��Ӧ�İ�װ����� HOME Ŀ¼�µ� .config(��װ������Ϣ�ļ�)�С�
crablfs> cmd tar xfz rxvt-2.7.10.tar.gz
crablfs> cmd cd rxvt-2.7.10
crablfs> cmd ./configure
crablfs> cmd make
crablfs> cmd make install
crablfs> cmd cd ..
crablfs> cmd rm -rf rxvt-2.7.10
crablfs> commit
��Ҫ˵�����ǣ���ʱ����ĵ�ǰ�û���������û�������Ŀ¼��������û�����Ŀ¼�����Ի���Ȩ������(��Ҳ���ǰ��û�ϵͳ��Ŀ������)��

���ô�����ʱ��������� list �鿴�������������
crablfs> list
0, tar xfz rxvt-2.7.10.tar.gz
1, cd rxvt-2.7.10
2, ./configure
3, make
4, make install

ʹ�� rollback ����������е�������ֻ����ɾ��ĳ��������������ʹ�� del N ���ɡ�

������ commit���������е�������¼�� .config �У�������� $pkgname-$version Ҳ���¼���б��ļ���(Ĭ�� /usr/src/packages.list)���Ա������������װ�ˡ������������ʧ�ܶ������޷���װ����������ų��������� quit �˳���������Ӧ�����ݲ��ᱻ��¼����ͨ���鵵�������Ȼᱻ���Ƶ� HOME �С�

����������������ļ��ȣ�
# userpack install -f /mnt/file/packages/MPlayer-1.0per8.tar.bz2 \
	-p /mnt/file/packages/all-20060611.tar.bz2 \
	-p /mnt/file/packages/Blue-1.6.tar.bz2 \
	mplayer-1.0pre8
// all �� mplayer �� codecs��Blue �� GUI Skin��

����Ѿ�ӵ����ǰ��װ��ʱ������������Ϣ�ļ���������� -a|--auto ִ���Զ���װ��
# userpack install -a rxvt-2.7.10
��ʱ��ζ�� $HOME/.config �Ѿ����ڣ�����ָ��֮(-c|--profile)��
# userpack install -ac /mnt/packages/confiles/rxvt-2.7.10 rxvt-2.7.10

������Ѿ��� /usr/src ��¼���˹����ϵ� sources Ŀ¼����Ҳ����ִ�����µ��Զ���װ��
# userpack install -as /mnt/dvdrom/sources rxvt-2.7.10

���⣬��װԴ�����������ϣ��� ftp �� ssh:
ssh://localhost/sources/mlterm-2.9.3.tar.gz
scp://localhost/sources/mlterm-2.9.3.tar.gz
����������һ����˼
ftp://localhost/pub/sources/mlterm-2.9.3.tar.gz
����
# userpack install -f ftp://192.168.0.1/pub/sources/mlterm-2.9.3.tar.gz mlterm-2.9.3

******
���û��ָ�� $pkgname-$version������ԴӰ���(mlterm-2.9.3.tar.gz)����������
******

���һ����ѹ���������⣬��Ϊ��װʱ���Զ������� HOME������һ�ΰ����������ȼ�� HOME ���Ƿ��д�ѹ����������Ѵ�����Ĭ�ϲ��´���µģ�������Ҫ����ָ��ǿ�ƿ���(-C|--copy-force)��
# userpack install -Caf libesmtp-1.0.3r1.tar.bz2

�����û����� ID�������������Լ����趨��Χ��Ĭ��ֵ�Ǵ� 1000 �� 20000�������� /etc/login.defs �ж��壺
PACK_UID_MIN	10000
PACK_UID_MAX	25000
PACK_GID_MIN	10000
PACK_GID_MAX	25000

b. ж�أ�
# userpack remove rxvt-2.7.10

c. �г������ܰ������������Ƶİ���
# userpack packs
rxvt-2.7.10
mplayer-1.0pre8
crablfs-0.1
pexpect-2.1
mlterm-2.9.3

d. ��ѯһ���ļ������Ǹ�����
# userpack owner /usr/local/bin/mlterm
mlterm-2.9.3

e. �г�һ����ӵ����Щ�ļ���
# userpack files pexpect-2.1
/usr/lib/python2.4/site-packages/fdpexpect.py
/usr/lib/python2.4/site-packages/pxssh.py
/usr/lib/python2.4/site-packages/pexpect.py
/usr/lib/python2.4/site-packages/pxssh.pyc
/usr/lib/python2.4/site-packages/pexpect.pyc
/usr/lib/python2.4/site-packages/fdpexpect.pyc

(4) ���ڰ�����汾������Լ��
�����ݸ����������Ĳ�������ʽΪ $pkgname-$version���� python re ��ģʽƥ��Ϊ��
'^(?P<pkgname>(\w+-{0,1})+)(-(?P<version>(\d[\w]*[-\.])*\d[\w]*))'

�� $pkgname ����Ϊ part1[-part2][-part3][...]��ÿ�� part ������[-a-zA-Z0-9_]���Կ�ͷ��ĸû�����ƣ�������ʹ����ĸ��ͷ�������� -[0-9][a-zA-Z0-9_]\. ������ģʽʱ(-�����һ�����ֿ�ͷ�Ĵ����ڴ������һ��'.'�ŵ����)��������Ϊ $version ���֣�$version ����Ҳ���԰�������'-'�ţ����������������ֿ�ͷ�Ĳ���ʱ����� $version ���֣���������ݺ��ԡ�

(5) ALFS
ǰ���Ѿ����������е�������¼��ÿ���� HOME �µ� .config �У����ҿ���������Щ��������Զ���װ���������п���ʹ��һ����������ű��������ڰ�װʱ���ɵ� packages.list һ���԰�װ���еİ�������������ϣ����ǿ��Խ���һ�� ALFS ��ʵ�֡�

��� ALFS ��ʵ���봫ͳ�� nALFS �� jhalfs ��Ŀ��������չ��������������Ի���ϵͳ�����磺��������һ̨������ʹ�� step by step �ķ���������һ�� LFS ϵͳ����ô��һ���ҿ�������������ɵ����а�װ������Ϣ�ļ��Զ���������Ҫ�������������ԭ����ϵͳ����һ�£�����ζ���ҿ���ʵ�ֶ�ε�Ǩ�ƣ�ͬʱ����Ҳ���������ҵİ�װ������Ϣ�ļ�Ϊ�����������Լ��ĸ��Ի�ϵͳ�����յ�Ŀ�굱Ȼ��Ҫʵ�ֿ�ƽ̨�Ĳ�����

�����������Ľű����� crablfs �ˡ�

******
Ŀǰֻ�� LFS �Ѿ�����������£���ʹ�� crablfs ���� BLFS ����������˲��ԣ���˻����ܽ� LFS ����ϵͳ�����а����ڰ�����ϵͳ����֮�¡�
******

������Ҫͨ���������� python �� crablfs �����ڱ��������֮�£�
# cd /blfs-sources
# tar xfj python-2.4.1.tar.bz2
# cd python-2.4.1
# patch -Np1 -i ../python-2.4.1-gdbm-1.patch
# ./configure --prefix=/opt --enable-shared
# make && make install
# cd ..
# rm -rf python-2.4.1
// ���ɾ����������ܻ�������

# export PYTHONPATH=/opt/lib/python2.4/site-packages
# tar xfz pexpect-2.1.tar.gz
# cd pexpect-2.1
# /opt/bin/python setup.py install --prefix=/opt
# cd ..
# rm -rf pexpect-2.1

# tar xfz crablfs-0.1.tar.gz
# cd crablfs-0.1
# cp userpack.dirs.blfs userpack.dirs
// �����ϵͳ��������������Ŀ¼�б�
// ����Ժ�����Ŀ¼Ȩ�޵����⣬ֻ��Ҫ���� /etc/userpack.dirs
// Ȼ������ userpack init ����
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

������ͬ�ķ�����ʹ�� userpack �ְ�װ�����ɰ���
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
// �ڵ�ǰĿ¼������һ�� profiles Ŀ¼������������� /usr/src
// �°�װ������Ϣ�ļ��Ŀ���
// ��� shell �ű����ᰲװ�������ڰ���ѹ�������ҵ�
# mv profiles /blfs-sources
# crablfs -t alfs \
	-C /blfs-sources/profiles/ \
	-F /blfs-sources/ \
	/blfs-sources/packages.list

���⣬�����֮ǰ��װ��һ��ϵͳ�����ҽ� /usr/src ȫ������������ -- �����¼���� DVD-R �ϣ���Ҳ������������
# crablfs -t crablfs[/default] \
	-s /mnt/dvdrom/sources/ \
	/mnt/dvdrom/sources/packages.list

crablfs ���¼��ǰ�ɹ���װ�İ������ֵ� /var/log/crablfs/.mark �С���Ϊ������֮�䳣����ǰ��������ϵ���������ĳһ�������� crablfs ���̻���ֹ�����������ᰲװ�����ų��������������ԭ�����������ԴӶϵ㿪ʼִ�С�

������� .mark ָ�� packages.list �е����һ�������� crablfs ʲô������������ע������������

���⣬crablfs ����У�� packages.list �ļ���������а����Ƿ��İ����Ȼ�ʹ crablfs ��ֹ���������κΰ�װ��������� .mark �еİ������� packages.list �У���õ� "x not in list" ���������������Ӧ�ĵ�����ͨ��ɾ�� .mark ���ɡ�

��Ŀǰ�����������û������̫��Ȩ�����⣬�Ҷ�����ͨ��������װʱ�Ĳ��������⡣������Ҫ�� chown, chmod, chgrp, install ��Щ�����д����������Ŀǰ��û�п�������֮��������ٿ��Ժ���Ե���������ɡ�

(6) ��һ���ļƻ�
* BLFS �� crablfs �����������ű�(shell script)
* ���� upgrade ����
* ���� gettext ���ʻ�֧��
* ÿ����������������Ϣ
* PyUnit ��Ԫ����
* cmdline ���� do ���ִ�е�����¼
* ��ǿ cmdline �����ȫ����
* ���� cmdline ��ȡ .config ��ʷ������޸�ָ������Ĺ���
* �� cmdline ����ִ�� root ����(���ý��̼�ͨ�Ż����� sudo)��
* cmdline �Ķ���ģʽ���� cat > file <<"EOF"��
* �����һ������༭��
* �� packages.list �����ļ���
* �� .config ��Ϊ $pkgname-$version ��ʽ
* �� LFS ����ϵͳʵ�ֿ���
* ��ǿ��ƽ̨֧�֣�
	���ӻ��������� cmdline ����֧������Ӧ��ͬ�� $ARCH �� $LOCALE
* ���ӶԶ����װԴ��֧��
* ��ǿ���������
* ����������У��
* ��ǿ���ý���: Plain Tree & XML
* ���������Լ������, reinstall ���⣿
* �����Ƶ��ĵ����ڲ��ĵ�������ĵ����ֲ�
* ʹ userpack.dir ֧��ָ����ȵĵݹ飬�� /usr/share/locale/ -r2
* userpack init �Զ�ɾ�� userpack.dirs �б�ɾ������ĿĿ¼

**************************************************************************
�����ҵ�һ�η����Լ�����Ʒ������ˮƽ���ޣ����л�����಻������֮�����һ����Ժ�Ŭ���ĸĽ������ƣ�ͬʱϣ����Ҳ��ߴͽ̣������ܸ����ҷ����������Ը�⣬��Ҳ������ GPL 2.0 Э�鼰������汾������Ľ����롣

ϣ���������Դ�����ã�Ҳϣ���ɴ˿�������һ������ͨ���͵ġ������ LFS ���а档

лл��
**************************************************************************

crablfs Copyright (c) 2006, ����(chowroc.z@gmail.com)

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
