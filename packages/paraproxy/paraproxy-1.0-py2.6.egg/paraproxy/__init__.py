# -*- encoding: utf-8
# Copyright (C) 2009  Rene Koecher <shirk87@gmail.com>
#
# This file is part of paraproxy.
#
# Paraproxy is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paraproxy is distrubuted in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with paraproxy; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.

import paramiko

import re
import os
import time
import socket
import thread
import fnmatch
import subprocess

from WrapSock import WrapSock

# for  debugging
__paramiko_SSHClient_connect_verbose = os.getenv('PARAMIKO_SSH_HOOK_VERBOSE', False)

# hook for original SSHClient.connect function
__paramiko_SSHClient_connect_hook = globals()['paramiko'].SSHClient.connect
# hook for original SSHClient.close function
__paramiko_SSHClient_close_hook = globals()['paramiko'].SSHClient.close

# liste with configured proxy-commands
__paramiko_SSHClient_proxy_list     = {}

# Import paramiko internals with prefix (__.*)
from paramiko.hostkeys import HostKeys as __HostKeys
from paramiko.resource import ResourceManager as __ResourceManager
from paramiko.transport import Transport as __Transport
from paramiko.ssh_exception import SSHException, BadHostKeyException

def __paramiko_SSHClient_debug(msg):
	if __paramiko_SSHClient_connect_verbose:
		print '[%s] %s' % (os.getpid(), msg)

def __paramiko_SSHClient_proxy_thread(self, ip, port, command):
	"""
	Proxy thread used to establish a connection using a ssh ProxyCommand.
	
	This will open a unix-domain-socket and listen for one incomming connection.
	After this it will spawn the proxy command an wrap the open socket to act
	as stdin and stdout for the new process.
	"""
	__paramiko_SSHClient_debug('proxy_thread(%s,%s)' % (ip, port))
	self._sock_name = os.path.join(os.path.sep,'tmp', '.paramiko_proxy_%s_%s_%s' % (ip, port, os.getpid()))
	
	try:
		os.unlink(self._sock_name)
	except OSError:
		pass
	
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	sock.bind(self._sock_name)
	sock.listen(1)
	__paramiko_SSHClient_debug('proxy: bound to `%s` and listening' % self._sock_name)
	
	(stmp, addr) = sock.accept()
	__paramiko_SSHClient_debug('proxy: incomming connection')
	
	wrap_sock = WrapSock(stmp)
	cmd_str = str(command) # copy
	proc = subprocess.Popen(cmd_str.replace('%h', str(ip)).replace('%p', str(port)),
							shell=True,
							stdin=wrap_sock,
							stdout=wrap_sock,
							close_fds=True)
	
	self._proc_id = proc.pid
	
	# warten auf Beendigung der Verbindung
	proc.wait()
		
	__paramiko_SSHClient_debug('proxy: ProxyCommand terminated, exit code: %s' % proc.returncode)
	wrap_sock.close()
	sock.close()
	
	del proc
	
	try:
		os.unlink(self._sock_name)
	except OSError:
		pass
	
	self._proc_id = None
	__paramiko_SSHClient_debug('proxy: ~proxy_thread()')


def __paramiko_SSHClient_connect(self, hostname, port=22, username=None,
				 password=None, pkey=None, key_filename=None,
				 timeout=None, allow_agent=True, look_for_keys=True):
	"""
	Hook function to enable Paramiko's SSHClient to work with ssh ProxyCommand.
	This will only hook into connections matching one of the ProxyRules.
	"""
	__paramiko_SSHClient_debug('__paramiko_SSHClient_connect(%s, %s)' % (hostname, port))
	
	command = None
	for pattern in __paramiko_SSHClient_proxy_list.keys():
		if fnmatch.fnmatch(hostname, pattern):
			command = __paramiko_SSHClient_proxy_list[pattern]
			break
	
	if not command:
		__paramiko_SSHClient_debug('direct connection.')
		return __paramiko_SSHClient_connect_hook(self, hostname, port, username, password, pkey,
							 key_filename, timeout, allow_agent, look_for_keys)

	__paramiko_SSHClient_debug('using ProxyCommand `%s`' % command)
	
	self._sock_name = None
	thread.start_new(__paramiko_SSHClient_proxy_thread, (self, hostname, port, command))
	time.sleep(1)
	
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	if timeout is not None:
		try:
			sock.settimeout(timeout)
		except:
			pass
	
	sock.connect(self._sock_name) # set by proxy_thread
	__paramiko_SSHClient_debug('connected to proxy thread on `%s`' % self._sock_name)
	
	t = self._transport = __Transport(sock)
	
	if self._log_channel is not None:
		t.set_log_channel(self._log_channel)
	t.start_client()
	__ResourceManager.register(self, t)
	
	server_key = t.get_remote_server_key()
	keytype = server_key.get_name()
	
	our_server_key = self._system_host_keys.get(hostname, {}).get(keytype, None)
	if our_server_key is None:
		our_server_key = self._host_keys.get(hostname, {}).get(keytype, None)
	if our_server_key is None:
		# will raise exception if the key is rejected; let that fall out
		self._policy.missing_host_key(self, hostname, server_key)
		# if the callback returns, assume the key is ok
		our_server_key = server_key
	
	if server_key != our_server_key:
		raise BadHostKeyException(hostname, server_key, our_server_key)
	
	if username is None:
		username = getpass.getuser()
	
	if key_filename is None:
		key_filenames = []
	elif isinstance(key_filename, (str, unicode)):
		key_filenames = [ key_filename ]
	else:
		key_filenames = key_filename
	self._auth(username, password, pkey, key_filenames, allow_agent, look_for_keys)
	__paramiko_SSHClient_debug('~__paramiko_SSHClient_connect()')

def __paramiko_SSHClient_close(self):
	__paramiko_SSHClient_close_hook(self)
	try:
		while self._proc_id:
			time.sleep(0.5)
		
	except AttributeError:
		pass
	
	try:
		os.unlink(self._sock_name)
	except OSError:
		pass
	except AttributeError:
		pass

# parse ssh_config
for conf_file in [os.path.join(os.path.sep, 'etc', 'ssh', 'ssh_config'),
			       os.path.join(os.getenv('HOME','/tmp'), '.ssh', 'config')]:
	try:
		config = open(conf_file)
		host_name = None
		for line in config.readlines():
			line = line.strip()
			match = re.match(r'[ \t]*Host[ \t]+([^ \t#]+)', line)
			if match:
				__paramiko_SSHClient_debug('New host `%s`' % match.groups()[0])
				host_name = match.groups()[0]
		
			match = re.match(r'[ \t]*ProxyCommand[ \t]+([^;#]+)', line)
			if match:
				__paramiko_SSHClient_debug('New command `%s`' % match.groups()[0])
				__paramiko_SSHClient_proxy_list[host_name] = match.groups()[0]

		config.close()
		del config
		del host_name
	
	except IOError,e:
		pass

# finally modify SSHClient to use our connect hook
globals()['paramiko'].SSHClient.connect = __paramiko_SSHClient_connect
globals()['paramiko'].SSHClient.close   = __paramiko_SSHClient_close

__paramiko_SSHClient_debug('Hookhookhook')
