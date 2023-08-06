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

import psycopg2

from psycopg2.pool import ThreadedConnectionPool


class PostgreSQL(object):
    """Connection object for PostgreSQL"""

    def __init__(self, options):
        dsn = []
        for k, v in (('db_host', 'host'), ('db_name', 'dbname'),
            ('db_user', 'user'), ('db_password', 'password')):
            value = getattr(options, k)
            if value:
                dsn.append('%s=%s' % (v, value))
        self.__database = ThreadedConnectionPool(
            int(options.db_pool_min),
            int(options.db_pool_max),
            ' '.join(dsn),
        )

    def get(self, isolation_level=2):
        connection = self.__database.getconn()
        connection.set_isolation_level(isolation_level)
        return connection

    def put(self, connection):
        self.__database.putconn(connection)

    def close(self):
        return self.__database.closeall()
