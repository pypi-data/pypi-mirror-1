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

from koboldfs import Client
from koboldfs.zope.interfaces import IKoboldFSClient

from zope.component import queryUtility
from zope.interface import Interface, implements
from zope.schema.fieldproperty import FieldProperty

from zope.thread import local

clients = local()


class KoboldFSClient(object):
    """KoboldFS client utility
    
    Verify if the class implements the interfaces:

        >>> from zope.interface.verify import verifyClass
        >>> verifyClass(IKoboldFSClient, KoboldFSClient)
        True

    Verify if the object provides the interfaces:

        >>> from zope.interface.verify import verifyObject
        >>> obj = KoboldFSClient(domain='test', servers=[])
        >>> verifyObject(IKoboldFSClient, obj)
        True

    """

    implements(IKoboldFSClient)

    domain = FieldProperty(IKoboldFSClient['domain'])
    servers = FieldProperty(IKoboldFSClient['servers'])

    def __init__(self, domain, servers):
        self.domain = domain
        if isinstance(self.domain, unicode):
            self.domain = self.domain.encode('utf-8')
        self.servers = servers

    @property
    def client(self):
        global clients
        client = getattr(clients, 'client', None)
        if client is None:
            client = Client(self.domain, servers=self.servers)
            clients.client = client
        return client

    def __health_check(self):
        if not self.client.ping():
            self.client.reset()

    def ping(self):
        return self.client.ping()

    def put(self, key, source):
        self.__health_check()
        return self.client.put(key, source)

    def get(self, key, destination):
        self.__health_check()
        return self.client.get(key, destination)

    def get_url(self, key):
        self.__health_check()
        return self.client.get_url(key)

    def delete(self, key):
        self.__health_check()
        return self.client.delete(key)
