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

from zope import component
from zope.component.zcml import handler

from koboldfs.zope import KoboldFSClient
from koboldfs.zope.interfaces import IKoboldFSClient


def handle_koboldfs(name, domain, servers):
    """Register a koboldfs client utility"""
    client = KoboldFSClient(domain, servers)
    handler('registerUtility', client, IKoboldFSClient, name)


def koboldfs(_context, name, domain, servers):
    _context.action(
        discriminator=("koboldfs", name),
        callable=handle_koboldfs,
        args=(name, domain, servers),
    )
