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

import re
import os
import sys
import md5
import pwd
import time
import shutil
import struct
import string
import socket
import signal
import random
import asyncore
import optparse
import operator
import tempfile
import threading

import logging
import logging.handlers

from koboldfs import protocol, Client


STATE_WAITING = 0
STATE_COMMAND = 1
STATE_ARGUMENT_SIZE = 2
STATE_ARGUMENT_VALUE = 3
STATE_EXECUTE = 4
STATE_RECEIVE_FILE_SIZE = 5
STATE_RECEIVE_FILE_CONTENT = 6
STATE_RECEIVE_FILE_CHECKSUM = 7


class ServerChannel(asyncore.dispatcher):
    """Channel dispatcher"""

    def __init__(self, channel, options, database, logger):
        self.__options = options
        self.__database = database
        self.__logger = logger
        self.__connection = database.get()
        self.__cursor = self.__connection.cursor()
        self.__buffer = ''
        self.__ibuffer = ''
        self.__reset(commit=False)
        asyncore.dispatcher.__init__(self, channel)

    def __reset(self, commit=True):
        # commit the transaction (if needed)
        success = True
        if commit:
            try:
                self.__connection.commit()
            except psycopg2.Error:
                self.__connection.rollback()
                success = False
            # remove the temporary file
            if self.__output_filename is not None and \
               os.path.isfile(self.__output_filename):
                os.unlink(self.__output_filename)
        # reset the status
        self.__status = STATE_WAITING
        self.__command = None
        self.__arguments = []
        self.__arguments_number = None
        self.__arguments_position = None
        self.__size = None
        self.__output = None
        self.__output_domain = None
        self.__output_key = None
        self.__output_filename = None
        self.__output_size = None
        self.__output_md5 = None
        return success

    def log_info(self, message, type='info'):
        if type in ('error', 'warning'):
            self.__logger.error('(%s:%s) - %s ' % \
                (self.addr[0], self.addr[1], message))
        else:
            self.__logger.debug('(%s:%s) - %s ' % \
                (self.addr[0], self.addr[1], message))

    def handle_error(self):
        nil, t, v, tbinfo = asyncore.compact_traceback()
        self_repr = repr(self)
        self.log_info('Python exception, closing channel %s (%s:%s %s)' % \
            (self_repr, t, v, tbinfo), 'error')
        self.handle_close()

    def writable(self):
        return len(self.__buffer) > 0

    def db_close(self):
        self.__cursor.close()
        self.__database.put(self.__connection)

    def handle_close(self):
        self.connected = False
        self.db_close()
        self.close()
        self.log_info('Closed connection.')

    def handle_write(self):
        sent = self.send(self.__buffer)
        self.__buffer = self.__buffer[sent:]

    def handle_read(self):
        data = self.__ibuffer
        # read from the socket
        try:
            data += self.recv(protocol.BLOCKSIZE)
        except socket.error, exception:
            self.handle_error()
            return
        # if the socket is not connected, skip the data
        if not self.connected:
            return
        # receiving a file (size)
        elif self.__status == STATE_RECEIVE_FILE_SIZE and len(data) >= 4:
            self.__size = struct.unpack('I', data[:4])[0]
            self.__status = STATE_RECEIVE_FILE_CONTENT
            data = data[4:]
        # receiving a file (content)
        if self.__status == STATE_RECEIVE_FILE_CONTENT and len(data) >= 1:
            remaining = self.__size - self.__output_size
            content = data[:remaining]
            self.__output.write(content)
            self.__output_size += len(content)
            self.__output_md5.update(content)
            data = data[remaining:]
            if self.__output_size == self.__size:
                self.__status = STATE_RECEIVE_FILE_CHECKSUM
        # receiving a file (checksum)
        if self.__status == STATE_RECEIVE_FILE_CHECKSUM and len(data) >= 32:
            checksum = data[:32]
            data = data[32:]
            self.handle_cmd_put_completed(checksum)
        # command
        if self.__status == STATE_WAITING and len(data) >= 1:
            self.__command = data[0]
            self.__status = STATE_COMMAND
            data = data[1:]
        # number of parameters
        if self.__status == STATE_COMMAND and len(data) >= 1:
            self.__arguments_number = struct.unpack('B', data[0])[0]
            self.__arguments_position = 0
            self.__status = STATE_ARGUMENT_SIZE
            data = data[1:]
        # loop on the parameters
        while self.__status in (STATE_ARGUMENT_SIZE, STATE_ARGUMENT_VALUE) and \
              len(self.__arguments) < self.__arguments_number:
            # argument size
            if self.__status == STATE_ARGUMENT_SIZE and len(data) >= 4:
                self.__size = struct.unpack('I', data[:4])[0]
                self.__status = STATE_ARGUMENT_VALUE
                data = data[4:]
            # argument value
            elif self.__status == STATE_ARGUMENT_VALUE and len(data) >= self.__size:
                self.__arguments.append(data[:self.__size])
                self.__status = len(self.__arguments) < self.__arguments_number and \
                    STATE_ARGUMENT_SIZE or STATE_EXECUTE
                data = data[self.__size:]
            # not enough data to continue
            else:
                break
        # update the input buffer
        self.__ibuffer = data
        # not enough data to continue
        if self.__status in (STATE_ARGUMENT_SIZE, STATE_ARGUMENT_VALUE) and \
           len(self.__arguments) == self.__arguments_number:
            self.__status = STATE_EXECUTE
        # execute the commands
        if self.__status == STATE_EXECUTE and \
           self.__command == protocol.CMD_PING:
            self.handle_cmd_ping(self.__arguments)
        elif self.__status == STATE_EXECUTE and \
           self.__command == protocol.CMD_PUT:
            self.handle_cmd_put(self.__arguments)
        elif self.__status == STATE_EXECUTE and \
           self.__command == protocol.CMD_GET:
            self.handle_cmd_get(self.__arguments)
        elif self.__status == STATE_EXECUTE and \
           self.__command == protocol.CMD_GET_URL:
            self.handle_cmd_get_url(self.__arguments)
        elif self.__status == STATE_EXECUTE and \
           self.__command == protocol.CMD_DELETE:
            self.handle_cmd_delete(self.__arguments)
        elif self.__status == STATE_EXECUTE:
            self.__buffer += protocol.RES_ERR_COMMAND
            self.__reset()

    def handle_cmd_ping(self, arguments):
        # log the request
        self.log_info('PING')
        # reply to the ping request
        if self.__reset(commit=False):
            self.__buffer += protocol.RES_OK
        else:
            self.__buffer += protocol.RES_ERR_RESET

    def handle_cmd_put(self, arguments):
        # log the request
        self.log_info('PUT (%s, %s)' % (arguments[0], arguments[1]))
        # retrieve the domain id, and return if it does not exist
        domain, key = arguments[0], arguments[1]
        domain = self.__options.domains.get(domain)
        if domain is None:
            self.__buffer += protocol.RES_ERR_DOMAIN
            self.__reset()
            return
        # prepare the system to receive the file from the client
        self.__status = STATE_RECEIVE_FILE_SIZE
        self.__output_domain = domain
        self.__output_key = key
        self.__output_filename = tempfile.mktemp(
            prefix='koboldfs-', dir=self.__options.repository_tmp)
        self.__output = open(self.__output_filename, 'w')
        self.__output_size = 0
        self.__output_md5 = md5.new()
        self.__buffer += protocol.RES_WAITING

    def __filename(self, domain, key, checksum, url=False):
        parts = not url and [self.__options.repository, domain[2]] or []
        parts.extend((
            checksum[0:2],
            checksum[2:4],
            checksum[4:6],
            checksum[6:8],
            checksum[8:12],
            checksum[12:16],
            checksum[16:24],
            checksum[24:32],
        ))
        parts.append(key)
        return not url and os.path.join(*parts) or '/'.join(parts)

    def handle_cmd_put_completed(self, checksum):
        # log the request
        self.log_info('PUT_COMPLETED (%s, %s)' % \
            (self.__output_domain[1], self.__output_key))
        # database connection and cursor: look-up the file by file id
        c = self.__cursor
        # the upload is successful
        if checksum == self.__output_md5.hexdigest():
            filename = self.__filename(self.__output_domain,
                self.__output_key, checksum)
            # database connection and cursor: look-up the file by key
            c = self.__cursor
            c.execute("SELECT id, checksum FROM files WHERE domain_id = %(d)s "
                "AND key = %(k)s AND status = 'R';",
                {'d': self.__output_domain[0], 'k': self.__output_key})
            file = c.fetchone()
           # if a different file with the same key already exists, delete it
            if file is not None and file[1] != checksum:
                c.execute("UPDATE files SET status = 'D', deleted_on = NOW() "
                    "WHERE id = %(id)s;", {'id': file[0]})
            # move the file and register it into the database
            if file is None or file[1] != checksum:
                c.execute("INSERT INTO files (domain_id, key, status, bytes, "
                    "checksum) VALUES (%(d)s, %(k)s, 'R', %(b)s, %(c)s);",
                    {'d': self.__output_domain[0], 'k': self.__output_key,
                     'b': self.__output_size, 'c': checksum})
                c.execute("INSERT INTO replicas (file_id, server_id) "
                    "VALUES (CURRVAL('files_id_seq'), %(s)s);",
                    {'s': self.__options.server_id})
                # move the file to the right position
                directory = os.path.split(filename)[0]
                if not os.path.isdir(directory):
                    os.makedirs(directory)
                shutil.move(self.__output_filename, filename)
            if self.__reset():
                self.__buffer += protocol.RES_OK
            else:
                self.__buffer += protocol.RES_RESET
        # the upload is NOT successful
        else:
            if self.__reset():
                self.__buffer += protocol.RES_OK
            else:
                self.__buffer += protocol.RES_RESET

    def handle_cmd_get(self, arguments):
        # log the request
        self.log_info('GET (%s, %s)' % (arguments[0], arguments[1]))
        # retrieve the domain id, and return if it does not exist
        domain, key = arguments[0], arguments[1]
        domain = self.__options.domains.get(domain)
        if domain is None:
            self.__buffer += protocol.RES_ERR_DOMAIN
            self.__reset()
            return
        # database connection and cursor: look-up the file by key
        c = self.__cursor
        c.execute("SELECT id, key, checksum FROM files WHERE domain_id = %(d)s "
            "AND key = %(k)s AND status = 'R';", {'d': domain[0], 'k': key})
        file = c.fetchone()
        # if the file does not exist, return error
        if file is None:
            self.__buffer += protocol.RES_ERR_NOTFOUND
            self.__reset()
            return
        # if we don't have the file on the file system, get it from the network
        filename = self.__filename(domain, file[1], file[2])
        if not os.path.isfile(filename):
            # get the list of servers we can find the file on
            c.execute("SELECT s.host FROM servers AS s "
                "JOIN replicas AS r ON (r.server_id = s.id) "
                "WHERE r.file_id = %(f)s;", {'f': file[0]})
            servers = map(operator.itemgetter(0), c.fetchall())
            # if we do not have servers to take the file from, return
            if not servers:
                self.__buffer += protocol.RES_ERR_NOTFOUND
            # send the redirect command reset the status
            else:
                random.shuffle(servers)
                self.log_info('REDIRECT (%s)' % (servers[0]))
                self.__buffer += (protocol.RES_REDIRECT + \
                    struct.pack('I', len(servers[0])) + servers[0])
            self.__reset()
        # send the file content to the client
        else:
            source = open(filename)
            source.seek(0, 2)
            size = source.tell()
            source.seek(0)
            self.__buffer += (protocol.RES_TRANSFER + struct.pack('I', size))
            while True:
                data = source.read(protocol.BLOCKSIZE)
                if not data:
                    break
                self.__buffer += data
            # send the file checksum and reset the status
            self.__buffer += file[2]
            self.__reset()

    def handle_cmd_get_url(self, arguments):
        # log the request
        self.log_info('GET_URL (%s, %s)' % (arguments[0], arguments[1]))
        # retrieve the domain id, and return if it does not exist
        domain, key = arguments[0], arguments[1]
        domain = self.__options.domains.get(domain)
        if domain is None:
            self.__buffer += protocol.RES_ERR_DOMAIN
            self.__reset()
            return
        # database connection and cursor: look-up the file by key
        c = self.__cursor
        c.execute("SELECT f.key, f.checksum, s.name FROM files AS f "
            "JOIN replicas AS r ON (f.id = r.file_id) "
            "JOIN servers AS s ON (s.id = r.server_id) "
            "WHERE f.domain_id = %(d)s AND f.key = %(k)s AND "
            "f.status = 'R' AND s.status = 'Y';", {'d': domain[0], 'k': key})
        options = c.fetchall()
        # if the file does not exist, return error
        if not options:
            self.__buffer += protocol.RES_ERR_NOTFOUND
            self.__reset()
            return
        # choose a random replica, and return the URL
        replica = random.choice(options)
        filename = self.__filename(domain, replica[0], replica[1], url=True)
        url = domain[3] % {
            'filename': filename, 'domain': domain[1], 'server': replica[2],
        }
        # reset the status
        self.__buffer += protocol.RES_TRANSFER + \
            struct.pack('I', len(url)) + url
        self.__reset()

    def handle_cmd_delete(self, arguments):
        # log the request
        self.log_info('DELETE (%s, %s)' % (arguments[0], arguments[1]))
        # retrieve the domain id, and return if it does not exist
        domain, key = arguments[0], arguments[1]
        domain = self.__options.domains.get(domain)
        if domain is None:
            self.__buffer += protocol.RES_ERR_DOMAIN
            self.__reset()
            return
        # database connection and cursor: look-up the file by key
        c = self.__cursor
        c.execute("SELECT id, key, checksum FROM files WHERE domain_id = %(d)s "
            "AND key = %(k)s AND status = 'R';", {'d': domain[0], 'k': key})
        file = c.fetchone()
        # if the file does not exist, return an error
        if file is None:
            self.__buffer += protocol.RES_ERR_NOTFOUND
            self.__reset()
            return
        # remove the file
        c.execute("UPDATE files SET status = 'D', deleted_on = NOW() "
            "WHERE id = %(f)s;", {'f': file[0]})
        # reset the status
        if self.__reset():
            self.__buffer += protocol.RES_OK
        else:
            self.__buffer += protocol.RES_RESET


class ServerDispatcher(asyncore.dispatcher):
    """Server network dispatcher"""

    def __init__(self, options, logger, database):
        asyncore.dispatcher.__init__(self)
        self.__options = options
        self.__logger = logger
        self.__database = database

    def handle_accept(self):
        channel, addr = self.accept()
        c = ServerChannel(channel, self.__options, self.__database, self.__logger)
        c.log_info('New connection ...')

    def sigterm_handler(self, signum, frame):
        self.__logger.info("Caught SIGTERM, shutting down the server.")
        asyncore.socket_map.clear()

    def run(self):
        signal.signal(signal.SIGTERM, self.sigterm_handler)
        host, port = self.__options.listen.split(':', 1)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, int(port)))
        self.listen(5)
        self.__logger.info("The server is ready to accept connections:")
        self.__logger.info('+ Server name: %s' % self.__options.server)
        self.__logger.info('+ Enabled domains: %s' % \
            ','.join(self.__options.domains.keys()))
        try:
            asyncore.loop()
        except KeyboardInterrupt:
            self.__logger.info("Caught KeyboardInterrupt, shutting down the server.")
            for x in asyncore.socket_map.values():
                x.socket.close()
                if hasattr(x, 'db_close'):
                    x.db_close()


class DataManager(threading.Thread):
    """Generic data manager"""

    def __init__(self, options, logger, database, server):
        super(DataManager, self).__init__()
        self.__options = options
        self.__database = database
        self.__logger = logger
        self.__server = server
        self.__interval = int(options.data_manager_interval)

    def __filename(self, domain, key, checksum, url=False):
        parts = not url and [self.__options.repository, domain[2]] or []
        parts.extend((
            checksum[0:2],
            checksum[2:4],
            checksum[4:6],
            checksum[6:8],
            checksum[8:12],
            checksum[12:16],
            checksum[16:24],
            checksum[24:32],
        ))
        parts.append(key)
        return not url and os.path.join(*parts) or '/'.join(parts)

    def run(self):
        timer = time.time()
        while self.__server.running:
            if time.time() - timer >= self.__interval:
                connection = self.__database.get()
                self.handler_purge(connection)
                self.handler_sync(connection)
                self.__database.put(connection)
                timer = time.time()
            time.sleep(1)

    def commit(self, db):
        # commit on the database
        try:
            db.commit()
        except pyscopg2.Error:
            self.__logger.error('(d-m) - Error while committing to the database, rollback.')
            db.rollback()
            return

    def handler_purge(self, db):
        # select all the files which are marked for removal
        c = db.cursor()
        d = db.cursor()
        c.execute("SELECT r.id, d.name, f.key, f.checksum FROM files AS f "
            "JOIN domains AS d ON (d.id = f.domain_id) "
            "JOIN replicas AS r ON (f.id = r.file_id) "
            "WHERE f.replicas > 0 AND f.status = 'D' AND r.server_id = %(s)s "
            "ORDER BY f.deleted_on LIMIT 100;",
            {'s': self.__options.server_id})
        # loop on the results, delete the row from `replicas'
        to_be_removed = []
        r = c.fetchone()
        while r:
            filename = self.__filename(self.__options.domains[r[1]], r[2], r[3])
            to_be_removed.append(filename)
            d.execute("DELETE FROM replicas WHERE id = %(id)s;", {'id': r[0]})
            r = c.fetchone()
        # commit on the database
        c.close()
        self.commit(db)
        # remove the files from the file system
        for filename in to_be_removed:
            if not os.path.isfile(filename):
                self.__logger.error("(d-m) - No such file `%s'" % filename)
                continue
            os.unlink(filename)
            head, tail = os.path.split(filename)
            while head and tail:
                try:
                    os.rmdir(head)
                except os.error:
                    break
                head, tail = os.path.split(head)
                if head == self.__options.repository:
                    break
        # log the result
        n = len(to_be_removed)
        if n > 0:
            self.__logger.info('(d-m) - Purged %d files from the file system' % n)

    def handler_sync(self, db):
        # select all the files which we do not have locally
        c = db.cursor()
        domains = ','.join(map(str, self.__options.rdomains.keys()))
        c.execute("SELECT f.id, f.domain_id, f.key, f.checksum "
            "FROM files AS f LEFT JOIN replicas AS r "
            "ON (f.id = r.file_id AND r.server_id = %(s)s) "
            "WHERE f.replicas < f.class AND f.status = 'R' AND "
            "f.domain_id IN (" + domains + ") AND r.id IS NULL "
            "ORDER BY f.created_on;",
            {'s': self.__options.server_id})
        # loop on the results, sync files we don't have locally
        r, n = c.fetchone(), 0
        while r:
            self.__sync(db, r[0], self.__options.rdomains[r[1]], r[2], r[3])
            r, n = c.fetchone(), n + 1
            # sync only 100 records, to avoid too long locks on the tables
            if n >= 100:
                break
        # commit on the database
        c.close()
        self.commit(db)
        # log the result
        if n > 0:
            self.__logger.info('(d-m) - Synchronized %d files from the network' % n)

    def __sync(self, db, fid, domain, key, checksum):
        # get the list of servers we can find the file on
        c = db.cursor()
        c.execute("SELECT s.host FROM servers AS s "
            "JOIN replicas AS r ON (r.server_id = s.id) "
            "WHERE r.file_id = %(f)s;", {'f': fid})
        servers = map(operator.itemgetter(0), c.fetchall())
        # if we do not have servers, return
        if not servers:
            return False
        # connect to the servers, and download the file
        random.shuffle(servers)
        client = Client(domain[1], servers=servers, timeout=10.0)
        tmpfile = tempfile.mktemp(prefix='koboldfs-',
            dir=self.__options.repository_tmp)
        output = open(tmpfile, 'w')
        success = client.get(key, output)
        output.close()
        # move the file to the right position and register the replica
        if success:
            filename = self.__filename(domain, key, checksum)
            directory = os.path.split(filename)[0]
            if not os.path.isdir(directory):
                os.makedirs(directory)
            shutil.move(tmpfile, filename)
            c.execute("INSERT INTO replicas (file_id, server_id) "
                "VALUES (%(f)s, %(s)s);", {'f': fid, 's': domain[4]})
        # error while trasferring the file: abort and remove the temporary file
        else:
            self.__logger.error("(d-m) - Unable to sync (`%s', `%s') from the network" % (domain[1], key))
            os.unlink(tmpfile)


class Server(object):
    """Server for the koboldfs distributed filesystem"""

    def __init__(self):
        self.running = True

    def parse_arguments(self):
        """Parse command line arguments"""
        parser = optparse.OptionParser(version="%prog " + protocol.VERSION)
        parser.add_option("-c", "--config", action="store", dest="config",
            default="/etc/koboldfsd.conf", help="configuration file path")
        parser.add_option("-d", "--debug", action="store_true", dest="debug",
            default=False, help="run in debug mode, do not detach from the console")
        (options, args) = parser.parse_args()
        if not os.path.isfile(options.config):
            print "Unable to read the configuration file `%s'!" % options.config
            sys.exit(1)
        for k, v in [map(string.strip, r.split("=", 1)) for r in file(options.config) \
            if "=" in r and not r.strip().startswith("#")]:
            setattr(options, k.lower(), v)
        if not os.path.isdir(options.repository):
            print "Repository directory `%s' does not exist!" % options.repository
            sys.exit(1)
        elif not os.path.isdir(options.repository_tmp):
            print "Repository temporary directory `%s' does not exist!" % options.repository_tmp
            sys.exit(1)
        return (parser, options, args)

    def start_logging(self, options):
        """Start logging infrastructure"""
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        handler = options.debug and \
            logging.StreamHandler(sys.stdout) or \
            logging.handlers.TimedRotatingFileHandler(
                os.path.join(options.logging_directory, 'koboldfsd.log'),
                'D', 1, options.logging_backups)
        handler.setFormatter(formatter)
        handler.setLevel(options.debug and logging.DEBUG or logging.INFO)
        logger = logging.getLogger()
        logger.setLevel(options.debug and logging.DEBUG or logging.INFO)
        logger.addHandler(handler)
        return logger

    def database_connection(self, options):
        # connection to the database server
        if options.db_type == 'postgresql':
            from koboldfs.databases import PostgreSQL
            database = PostgreSQL(options)
        else:
            raise ValueError, 'Unknown database type: %s' % options.db_type
        # get the list of domains
        db = database.get()
        c = db.cursor()
        c.execute("SELECT d.id, d.name, d.folder, d.url, s.id, s.name "
            "FROM domains AS d "
            "JOIN servers_domains AS sd ON (sd.domain_id = d.id) "
            "JOIN servers AS s ON (sd.server_id = s.id) "
            "WHERE s.name = %(n)s;", {'n': options.server})
        options.domains = {}
        options.rdomains = {}
        r = c.fetchone()
        while r is not None:
            options.server_id = r[4]
            options.domains[r[1]] = tuple(r)
            options.rdomains[r[0]] = tuple(r)
            r = c.fetchone()
        database.put(db)
        # return the database object
        return database

    def main(self):
        (parser, options, args) = self.parse_arguments()
        # fork, if it is needed
        if not options.debug:
            try:
                pid = os.fork()
                if pid > 0:
                    sys.exit(0)
            except OSError, e:
                print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)
                sys.exit(1)
            os.chdir("/")
            os.setsid()
            os.umask(2)
            si = file('/dev/null', 'r')
            so = file('/dev/null', 'a+')
            se = file('/dev/null', 'a+', 0)
            sys.stdout.flush()
            sys.stderr.flush()
            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())
            os.dup2(se.fileno(), sys.stderr.fileno())
            try:
                pid = os.fork()
                if pid > 0:
                    sys.exit(0)
            except OSError, e:
                print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
                sys.exit(1)
            try:
                pwnam = pwd.getpwnam(options.user)
                os.setgid(pwnam[3])
                os.setuid(pwnam[2])
            except KeyError:
                sys.exit(2)
            except OSError:
                sys.exit(3)
            # write the current PID into the pid_file
            open(options.pid_file, 'w').write(str(os.getpid()) + '\n')
        # start the server
        logger = self.start_logging(options)
        database = self.database_connection(options)
        threads = []
        threads.append(DataManager(options, logger, database, self))
        for t in threads:
            t.start()
        try:
            ServerDispatcher(options, logger, database).run()
        except socket.error, e:
            logger.error(str(e))
        # shutdown the server
        self.running = False
        for t in threads:
            t.join()
        database.close()
        # remove the pid file, if it exists
        if os.path.isfile(options.pid_file):
            os.unlink(options.pid_file)


def main(argv=sys.argv):
    """Run the koboldfs server"""
    Server().main()
