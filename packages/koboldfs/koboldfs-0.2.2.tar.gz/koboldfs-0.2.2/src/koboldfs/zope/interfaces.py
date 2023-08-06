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

from zope.configuration.fields import Tokens
from zope.interface import Interface
from zope.schema import BytesLine


class IKoboldFSClientMeta(Interface):
    """A koboldfs client utility"""

    domain = BytesLine(
        title=u'Domain',
        description=u"The domain used by this client",
        required=True,
    )

    servers = Tokens(
        title=u'Servers',
        description=u"Servers defined as <hostname>:<port>",
        value_type=BytesLine(
            required=True,
            constraint=re.compile('^.*:[0-9]+$').match,
        ),
        required=True,
    )


class IKoboldFSClient(IKoboldFSClientMeta):

    def ping():
        """Ping the server"""

    def put(key, source):
        """Upload a file to the server"""

    def get(key, destination):
        """Get a file by key and write it to destination"""

    def get_url(key):
        """Get the URL of a file by key"""

    def delete(key):
        """Delete a file by key"""
