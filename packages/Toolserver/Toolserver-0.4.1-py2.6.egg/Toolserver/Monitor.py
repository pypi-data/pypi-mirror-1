# Toolserver Framework for Python - Monitor client
#
#     Copyright (c) 2004, Georg Bauer <gb@rfc1437.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
# the Software, and to permit persons to whom the Software is furnished to do so, 
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import hashlib
import sys
import string
import asyncore
import asynchat
import socket

from Toolserver.Config import config

def hex_digest (s):
    m = hashlib.md5()
    m.update (s)
    return string.joinfields (
            map (lambda x: hex (ord (x))[2:], map (None, m.digest())),
            '',
            )

class stdin_channel (asyncore.file_dispatcher):
    def handle_read (self):
        data = self.recv(512)
        if not data:
            print '\nclosed.'
            self.sock_channel.close()
            try:
                self.close()
            except:
                pass

        data = string.replace(data, '\n', '\r\n')
        self.sock_channel.push (data)

    def writable (self):
        return 0

    def log (self, *ignore):
        pass

class monitor_client (asynchat.async_chat):
    def __init__ (self, password, addr=('',8023), socket_type=socket.AF_INET):
        asynchat.async_chat.__init__ (self)
        self.create_socket (socket_type, socket.SOCK_STREAM)
        self.terminator = '\r\n'
        self.connect (addr)
        self.sent_auth = 0
        self.timestamp = ''
        self.password = password

    def collect_incoming_data (self, data):
        if not self.sent_auth:
            self.timestamp = self.timestamp + data
        else:
            sys.stdout.write (data)
            sys.stdout.flush()

    def found_terminator (self):
        if not self.sent_auth:
            self.push (hex_digest (self.timestamp + self.password) + '\r\n')
            self.sent_auth = 1
        else:
            print

    def handle_close (self):
        # close all the channels, which will make the standard main
        # loop exit.
        map (lambda x: x.close(), asyncore.socket_map.values())

    def log (self, *ignore):
        pass

class encrypted_monitor_client (monitor_client):
    "Wrap push() and recv() with a stream cipher"

    def init_cipher (self, cipher, key):
        self.outgoing = cipher.new (key)
        self.incoming = cipher.new (key)

    def push (self, data):
        # push the encrypted data instead
        return monitor_client.push (self, self.outgoing.encrypt (data))

    def recv (self, block_size):
        data = monitor_client.recv (self, block_size)
        if data:
            return self.incoming.decrypt (data)
        else:
            return data

def startMonitorClient():
	if config.monitorport and config.monitorpassword:
		stdin = stdin_channel (0)
		client = monitor_client (config.monitorpassword, ('127.0.0.1', config.monitorport))
		stdin.sock_channel = client
		asyncore.loop()
	else:
		print 'No monitor server is configured!'

