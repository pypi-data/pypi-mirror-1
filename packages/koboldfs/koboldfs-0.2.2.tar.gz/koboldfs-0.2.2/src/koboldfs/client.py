# koboldfs
# Copyright (C) 2008-2009 Fabio Tranchitella <fabio@tranchitella.it>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import md5
import time
import errno
import socket
import select
import struct
import StringIO

from koboldfs import protocol


class Client(object):
    """Client for the koboldfs distributed filesystem"""

    FLAG_NOSIGNAL = 0x4000
    
    def __init__(self, domain, servers, timeout=2.0):
        self.__domain = domain
        self.__servers = servers
        self.__dead_servers = {}
        self.__socket_cache = None
        self.__timeout = timeout

    @property
    def domain(self):
        return self.__domain

    def __socket(self, timeout=None, servers=None):
        if servers is None and \
           self.__socket_cache is not None:
            return self.__socket_cache
        now, dead_servers = time.time(), self.__dead_servers
        if servers is None:
            _servers = self.__servers
        else:
            _servers = servers
        if timeout is None:
            timeout = self.__timeout
        for s in _servers:
            dead = dead_servers.get(s)
            if dead is not None:
                if now - dead < 10:
                    continue
                else:
                    del dead_servers[s]
            host, port = s.split(':', 1)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(0)
            r = sock.connect_ex((host, int(port)))
            if not r:
                if servers is None:
                    self.__socket_cache = sock
                sock.settimeout(timeout)
                return sock
            if r == errno.EINPROGRESS:
                if select.select([], [sock], [], 3)[1:]:
                    r = sock.connect_ex((host, int(port)))
                    if not r or r == errno.EISCONN:
                        if servers is None:
                            self.__socket_cache = sock
                        sock.settimeout(timeout)
                        return sock
            dead_servers[s] = now
        return None

    def __read(self, sock, count):
        output = ""
        while len(output) < count:
            try:
                data = sock.recv(count - len(output))
            except socket.timeout:
                self.reset()
                return None
            if not data:
                return None
            output += data
        return output

    def __write(self, sock, data):
        try:
            sock.sendall(data, self.FLAG_NOSIGNAL)
        except socket.error, e:
            if e[0] == errno.EPIPE:
                return False
            raise
        else:
            return True

    def __request(self, command, args=[]):
        parts = [command, struct.pack('B', len(args))]
        for arg in args:
            parts.extend((struct.pack('I', len(arg)), arg))
        return ''.join(parts)

    def ping(self):
        sock = self.__socket()
        if sock is None:
            return False
        request = self.__request(protocol.CMD_PING)
        if not self.__write(sock, request):
            return False
        return self.__read(sock, 1) == protocol.RES_OK

    def put(self, key, source):
        close = False
        if not hasattr(source, 'read'):
            source = open(source)
            close = True
        source.seek(0, 2)
        size = source.tell()
        source.seek(0)
        sock = self.__socket()
        if sock is None:
            return False
        request = self.__request(protocol.CMD_PUT, args=(self.__domain, key,))
        if not self.__write(sock, request):
            return False
        if self.__read(sock, 1) != protocol.RES_WAITING:
            return False
        if not self.__write(sock, struct.pack('I', size)):
            return False
        digest = md5.new()
        while True:
            data = source.read(protocol.BLOCKSIZE)
            if not data:
                break
            if not self.__write(sock, data):
                return False
            digest.update(data)
        if close:
            source.close()
        if not self.__write(sock, digest.hexdigest()):
            return False
        return self.__read(sock, 1) == protocol.RES_OK

    def get(self, key, destination, sock=None):
        if sock is None:
            sock = self.__socket()
        if sock is None:
            return False
        request = self.__request(protocol.CMD_GET, args=(self.__domain, key))
        if not self.__write(sock, request):
            return False
        ret = self.__read(sock, 1)
        if ret == protocol.RES_REDIRECT:
            size = struct.unpack('I',  self.__read(sock, 4))[0]
            server = self.__read(sock, size)
            sock = self.__socket(servers=[server])
            if sock is None:
                return False
            return self.get(key, destination, sock)
        elif ret != protocol.RES_TRANSFER:
            return False
        position = 0
        size = struct.unpack('I',  self.__read(sock, 4))[0]
        digest = md5.new()
        while position < size:
            remaining = size - position
            data = self.__read(sock, min(protocol.BLOCKSIZE, remaining))
            if not data:
                break
            destination.write(data)
            digest.update(data)
            position += len(data)
        checksum = self.__read(sock, 32)
        if checksum != digest.hexdigest():
            return False
        return True

    def get_url(self, key):
        sock = self.__socket()
        if sock is None:
            return None
        request = self.__request(protocol.CMD_GET_URL, args=(self.__domain, key))
        if not self.__write(sock, request):
            return None
        if self.__read(sock, 1) != protocol.RES_TRANSFER:
            return None
        size = struct.unpack('I',  self.__read(sock, 4))[0]
        return self.__read(sock, size)

    def delete(self, key):
        sock = self.__socket()
        if sock is None:
            return False
        request = self.__request(protocol.CMD_DELETE, args=(self.__domain, key))
        if not self.__write(sock, request):
            return False
        return self.__read(sock, 1) == protocol.RES_OK

    def reset(self, servers=None):
        if self.__socket_cache is not None:
            self.__socket_cache.close()
            self.__socket_cache = None
        if servers is not None:
            self.__servers = servers
