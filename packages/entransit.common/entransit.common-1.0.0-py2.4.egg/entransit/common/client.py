##############################################################################
#
# Enfold Enterprise Deployment - Remote Deployment of Content
# Copyright (C) 2005 Enfold Systems
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
##############################################################################
"""
$Id: __init__.py 732 2005-01-21 19:43:40Z sidnei $
"""

import os
import sys
import socket
import types

from entransit.common.logger import log, DEBUG
from ZEO.zrpc.client import ConnectionManager
from ZEO.Exceptions import ClientDisconnected

CHUNKSIZE = 1 << 16

class DisconnectedServerStub(object):
    """Internal helper class used as a faux RPC stub when disconnected.

    This raises ClientDisconnected on all attribute accesses.

    This is a singleton class -- there should be only one instance,
    the global disconnected_stub, os it can be tested by identity.
    """

    def __init__(self, addr):
        self.addr = addr

    def __getattr__(self, attr):
        if attr in ('addr',):
            return object.__getattribute__(self, attr)
        raise ClientDisconnected(self.addr)

class ServerStub:
    """An RPC stub class for the interface exported by Client.

    This is the interface presented by the Server to the
    Client; i.e. the Client calls these methods and they
    are executed in the Server.

    See the Server module for documentation on these methods.
    """

    def __init__(self, rpc):
        """Constructor.

        The argument is a connection: an instance of the
        zrpc.connection.Connection class.
        """
        self.rpc = rpc
        # Wait until we know what version the other side is using.
        while rpc.peer_protocol_version is None:
            rpc.pending()

    def deploy(self, archivefilename, keep=False):
        self.rpc.call('startDeploy')
        archive = open(archivefilename, 'rb')
        try:
            chunk = archive.read(CHUNKSIZE)
            while chunk:
                self.rpc.call('receiveArchiveChunk', chunk)
                chunk = archive.read(CHUNKSIZE)
        finally:
            archive.close()
        if not keep:
            os.remove(archivefilename)
        self.rpc.call('finishDeploy')

    def ping(self):
        self.rpc.call('ping')

    def close(self):
        self.rpc.close()

class Client(object):

    ConnectionManagerClass = ConnectionManager
    ServerStubClass = ServerStub

    def __init__(self, addr,
                 min_disconnect_poll=5,
                 max_disconnect_poll=300):

        self._rpc_mgr = self.ConnectionManagerClass(addr, self,
                                                    tmin=min_disconnect_poll,
                                                    tmax=max_disconnect_poll)

        self._disconnected = self._server = DisconnectedServerStub(addr)

        if not self._rpc_mgr.attempt_connect():
            self._rpc_mgr.connect()

    def notifyConnected(self, conn):
        """Internal: start using the given connection.

        This is called by ConnectionManager after it has decided which
        connection should be used.
        """
        self.set_server_addr(conn.get_addr())
        stub = self.ServerStubClass(conn)
        self._server = stub

    def set_server_addr(self, addr):
        # Normalize server address and convert to string
        if isinstance(addr, types.StringType):
            self._server_addr = addr
        else:
            assert isinstance(addr, types.TupleType)
            # If the server is on a remote host, we need to guarantee
            # that all clients used the same name for the server.  If
            # they don't, the sortKey() may be different for each client.
            # The best solution seems to be the official name reported
            # by gethostbyaddr().
            host = addr[0]
            try:
                canonical, aliases, addrs = socket.gethostbyaddr(host)
            except socket.error, err:
                log("Error resolving host: %s (%s)" % (host, err), level=DEBUG)
                canonical = host
            self._server_addr = str((canonical, addr[1]))

    def notifyDisconnected(self):
        """Internal: notify that the server connection was terminated.

        This is called by ConnectionManager when the connection is
        closed or when certain problems with the connection occur.
        """
        log("Disconnected from storage: %s" % repr(self._server_addr))

        self._server = self._disconnected

    def testConnection(self, conn):
        return True

    def deploy(self, fpath, keep=False):
        return self._server.deploy(fpath, keep=keep)

    def close(self):
        self._rpc_mgr.close()

    def ping(self):
        self._server.ping()

if __name__ == '__main__':
    from time import time, sleep
    now = time()
    if len(sys.argv) > 2:
        addr = (sys.argv[1], int(sys.argv[2]))
    else:
        addr = ('127.0.0.1', 9101)
    handler = Client(addr)

    try:
        try:
            handler.deploy(sys.argv[1], keep=True)
#             handler.deploy((
#                 ('tarek', 'add',
#                  {'title':u'Tarek Ziad\xc3\xa9',
#                   'portal_type':'Document',
#                   'object_id': 'tarek',
#                   'uid': '101',
#                   'description':u'Tarek Ziad\xc3\xa9',
#                   'body':'<a href="resolveuid/%s" />' % 101,
#                   }),
#                 ))

#             sleep(1)

#             handler.deploy((
#                 ('erico', 'add',
#                  {'title':'\xc3\x83\xc2\x89rico',
#                   'portal_type':'Document',
#                   'object_id': 'erico',
#                   'uid': '102',
#                   'description':'\xc3\x83\xc2\x89rico',
#                   'body':'<a href="resolveuid/%s" />' % 102,
#                   }),
#                 ))

#             sleep(1)

#             handler.deploy((
#                 ('ref1', 'add',
#                  {'title':'This is a test ref1',
#                   'object_id': 'ref1',
#                   'portal_type':'Document',
#                   'uid': '333',
#                   'description':'Test ref1 description',
#                   'body':'<a href="resolveuid/%s" />' % 333,
#                   'references':{'subject':'98023948928938942980',
#                                 'predicates':
#                                 {'related':('287997274882394787247',
#                                             '289234273478277782384',
#                                             '239842747278439787384')
#                                  }
#                                 }
#                   }),
#                 ))

#             sleep(1)

#             handler.deploy((
#                 ('ref2', 'add',
#                  {'title':'This is a test ref2',
#                   'portal_type':'Document',
#                   'object_id': 'ref2',
#                   'uid': '444',
#                   'description':'Test ref2 description',
#                   'body':'<a href="resolveuid/%s" />' % 444,
#                   'references':{'subject':'287997274882394787247',
#                                 'predicates':
#                                 {'related':('98023948928938942980',
#                                             '289234273478277782384',
#                                             '239842747278439787384')
#                                  }
#                                 }
#                   }),
#                 ))

#             sleep(1)

#             handler.deploy((
#                 ('ref3', 'add',
#                  {'title':'This is a test ref3',
#                   'portal_type':'Document',
#                   'object_id': 'ref3',
#                   'uid': '5',
#                   'description':'Test ref3 description',
#                   'references':{'subject':'289234273478277782384',
#                                 'predicates':
#                                 {'related':('98023948928938942980',
#                                             '239842747278439787384')
#                                  }
#                                 }
#                   }),
#                 ))

#             sleep(1)

#             handler.deploy((
#                 ('ref3', 'remove', {}),
#                 ))

#             sleep(1)

#             handler.deploy([(str(i), 'add',
#                              {'title':'This is a test',
#                               'portal_type':'Document',
#                               'object_id': str(i),
#                               'uid': str(i),
#                               'description':'Test Description',
#                               'body':'<a href=\'resolveuid/%s\' />' % i})
#                             for i in xrange(0, 5)])

#             sleep(1)

#             handler.deploy([(str(i), 'remove', {})
#                             for i in xrange(3, 4)])

#             sleep(1)

#             handler.deploy([(str(i), 'update',
#                              {'title':'This is a test, v2',
#                               'portal_type':'Document',
#                               'uid': str(i),
#                               'description':'Test New Description',
#                               'body':'<a href="resolveuid/%s" />' % i})
#                             for i in xrange(0, 3)])

#             sleep(1)

#             handler.deploy((
#                 ('folder1/file1', 'add',
#                  {'title':'This is a test document',
#                   'portal_type':'Document',
#                   'object_id': 'file1',
#                   'uid': '222',
#                   'description':'Test folder description',
#                   'body':'<a href="resolveuid/%s" />' % 0}),
#                 ))

#             sleep(1)

#             handler.deploy((
#                 ('folder1/file1', 'update',
#                  {'title':'This is a test document',
#                   'portal_type':'Document',
#                   'object_id': 'file1',
#                   'uid': '2',
#                   'description':'Test folder description'}),
#                 ))

#             sleep(1)

#             handler.deploy((
#                 ('folder1/file2', 'add',
#                  {'title':'This is a test document',
#                   'portal_type':'Document',
#                   'object_id': 'file2',
#                   'uid': '2',
#                   'description':'Test folder description',
#                   'body':'<a href="resolveuid/%s" />' % 2,
#                   'blob':'xxxyyyzzz'}),
#                 ))

#             sleep(1)

#             # Deploy a sub-item before folder to trigger a bug in Add.
#             handler.deploy((
#                 ('folder3/file3', 'add',
#                  {'title':'This is a test document',
#                   'portal_type':'Document',
#                   'object_id': 'file3',
#                   'uid': '3',
#                   'description':'Test file description',
#                   'body':'<a href="resolveuid/%s" />' % 3,
#                   'folderish': False}),
#                 ))

#             sleep(1)

#             handler.deploy((
#                 ('folder3', 'add',
#                  {'title':'This is a test folder',
#                   'portal_type':'Folder',
#                   'object_id': 'folder3',
#                   'uid': '4',
#                   'description':'Test folder description',
#                   'body':'<a href="resolveuid/%s" />' % 4,
#                   'folderish': True,
#                   'children': ('file3',),
#                   'children_info':({'id':'file3',
#                                     'folderish': False,
#                                     'title':'This is a test file'},),
#                   }),
#                 ))

#             sleep(1)

#             handler.deploy((
#                 ('folder1/file2', 'remove', {}),
#                 ))

#             sleep(1)

#             handler.deploy((
#                 ('folder1/file1', 'remove', {}),
#                 ))

#             sleep(1)

#             handler.deploy((
#                 ('folder1', 'remove', {}),
#                 ))

#             sleep(1)

#             handler.deploy((
#                 ('blob1', 'add',
#                  {'title':'This is a test file',
#                   'portal_type':'File',
#                   'object_id': 'blob1',
#                   'uid': '777',
#                   'description':'Test folder description',
#                   'blob':'xxxyyyzzz'}),
#                 ))

#             sleep(1)

#             handler.deploy((
#                 ('blob1', 'remove', {}),
#                 ))

#             sleep(1)

#             handler.deploy((
#                 ('blob2', 'add',
#                  {'title':'This is a test file',
#                   'portal_type':'File',
#                   'object_id': 'blob2',
#                   'uid': '888',
#                   'description':'Test folder description',
#                   'body':'<a href="http://localhost/resolveuid/%s" />' % 1,
#                   'blob':'xxxyyyzzz'}),
#                 ))

#             sleep(1)
        except:
            import traceback
            traceback.print_exc()
            raw_input('Press a key to continue...')
    finally:
        handler.close()
