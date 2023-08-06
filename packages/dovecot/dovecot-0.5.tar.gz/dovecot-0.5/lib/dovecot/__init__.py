# Copyright 2008-2009 Thomas Arnett
# Licensed under the Open Software License, version 3.0

'''Dovecot Authentication Protocol client and master
http://wiki.dovecot.org/Authentication_Protocol'''

import os
from socket import socket, AF_UNIX

VERSION = (1, 0)
LINE_LEN = 2**13

CONN = 0

def conn():
	'''Generate a connection identifier'''
	global CONN
	CONN += 1
	return str(CONN)

class _Socket(socket):
	def __init__(self, path):
		socket.__init__(self, AF_UNIX)
		self.buf = ''
		self.connect(path)
		self.put('VERSION', *VERSION)
	
	def put(self, *tokens):
		'''Format and send a command'''
		line = '\t'.join(map(str, tokens))
		if len(line) >= LINE_LEN:
			raise Exception('Not sending a very long line')
		self.sendall('%s\n' % line)
	
	def get(self):
		'''Receive and parse commands'''
		while True:
			self.buf += self.recv(LINE_LEN)
			
			# yield any complete lines
			while self.buf:
				line, sep, rest = self.buf.partition('\n')
				if not sep:
					self.buf = line
					break
				self.buf = rest
				yield line.split('\t')
			
			if not self.buf:
				break
			elif len(self.buf) >= LINE_LEN:
				raise Exception('Received a very long line')
	
	def check(self, tokens, expected_cmd):
		'''Send a command and check server reply'''
		self.put(*tokens)
		reply = next(self.get())
		expected = expected_cmd, str(tokens[1])
		return all(a == b for a, b in zip(reply, expected))
		
	def check_version(self, version):
		'''Check protocol version'''
		if int(version) != VERSION[0]:
			raise Exception('Protocol version mismatch')

class Client(_Socket):
	def __init__(self, path='/var/run/dovecot/auth-client'):
		_Socket.__init__(self, path)
		self.put('CPID', os.getpid())
		mechs = set()
		
		try:
			while True:
				for line in self.get():
					cmd = line[0]
					if cmd == 'DONE':
						raise StopIteration
					
					param = line[1]
					if cmd == 'VERSION':
						self.check_version(param)
					elif cmd == 'SPID':
						self.SPID = int(param)
					elif cmd == 'MECH':
						mechs.add(param)
		except StopIteration:
			pass
		
		if 'PLAIN' not in mechs:
			raise Exception('Server does not support PLAIN authentication')
	
	def auth(self, username, password, service):
		resp = '\0'.join(('', username, password)).encode('base64').rstrip('\n')
		tokens = ('AUTH', conn(), 'PLAIN', 'service=' + service, 'resp=' + resp)
		return self.check(tokens, 'OK')

class Master(_Socket):
	def __init__(self, client, path='/var/run/dovecot/auth-master'):
		_Socket.__init__(self, path)
		for line in self.get():
			cmd = line[0]
			if not cmd:
				continue
			
			param = line[1]
			if cmd == 'VERSION':
				self.check_version(param)
			if cmd == 'SPID' and int(param) != client.SPID:
				raise Exception('Server PID mismatch')
	
	def user(self, username, service):
		tokens = ('USER', conn(), username, 'service=' + service)
		return self.check(tokens, 'USER')
