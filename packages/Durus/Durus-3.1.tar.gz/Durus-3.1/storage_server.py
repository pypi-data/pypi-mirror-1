"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/durus/storage_server.py $
$Id: storage_server.py 27080 2005-07-26 13:53:40Z dbinger $
"""
from datetime import datetime
from durus.logger import log, is_logging
from durus.serialize import extract_class_name
from durus.utils import p32, u32, u64
from sets import Set
import errno
import select
import socket


STATUS_OKAY = 'O'
STATUS_KEYERROR = 'K'
STATUS_INVALID = 'I'

TIMEOUT = 10
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 2972


def recv(s, n):
    """(s:socket, n:int) -> str
    Call the recv() method on the socket, repeating as required until n bytes
    are received.  
    """
    data = []
    while n > 0:
        hunk = s.recv(n)
        if not hunk:
            raise IOError, 'connection reset by peer'
        n -= len(hunk)
        data.append(hunk)
    return ''.join(data)

class _Client:

    def __init__(self, s, addr):
        self.s = s
        self.addr = addr
        self.invalid = Set()

class ClientError(Exception):
    pass

class StorageServer:

    def __init__(self, storage, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.storage = storage
        self.clients = []
        self.sockets = []
        self.packer = None
        self.host = host
        self.port = port

    def serve(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((self.host, self.port))
        except socket.error, exc:
            if exc.args[0] == errno.EADDRINUSE:
                raise RuntimeError(
                    "Port %s on %s is already in use by another process." %
                    (self.port, self.host))
        sock.listen(40)
        log(20, 'Ready with %s objects', self.storage.get_size())
        self.sockets.append(sock)
        while 1:
            if self.packer is not None:
                timeout = 0.0
            else:
                timeout = None
            r, w, e = select.select(self.sockets, [], [], timeout)
            for s in r:
                if s is sock:
                    # new connection
                    conn, addr = s.accept()
                    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    conn.settimeout(TIMEOUT)
                    self.clients.append(_Client(conn, addr))
                    self.sockets.append(conn)
                else:
                    # command from client
                    try:
                        self.handle(s)
                    except (ClientError, socket.error, socket.timeout), exc:
                        log(10, '%s', ''.join(map(str, exc.args)))
                        self.sockets.remove(s)
                        self.clients.remove(self._find_client(s))
            if self.packer is not None:
                try:
                    self.packer.next()
                except StopIteration:
                    log(20, 'Pack finished at %s' % datetime.now())
                    self.packer = None # done packing

    def handle(self, s):
        command_code = s.recv(1)
        if not command_code:
            raise ClientError('EOF from client')
        handler = getattr(self, 'handle_%s' % command_code)
        handler(s)

    def _find_client(self, s):
        for client in self.clients:
            if client.s is s:
                return client
        assert 0

    def handle_N(self, s):
        # new OID
        s.sendall(self.storage.new_oid())

    def handle_L(self, s):
        # load
        oid = recv(s, 8)
        if oid in self._find_client(s).invalid:
            s.sendall(STATUS_INVALID)
        else:
            try:
                record = self.storage.load(oid)
            except KeyError:
                log(10, 'KeyError %s', u64(oid))
                s.sendall(STATUS_KEYERROR)
            else:
                if is_logging(5):
                    log(5, 'Load %-7s %s', u64(oid), extract_class_name(record))
                s.sendall(STATUS_OKAY + p32(len(record)) + record)

    def handle_C(self, s):
        # commit
        client = self._find_client(s)
        s.sendall(p32(len(client.invalid)) + ''.join(client.invalid))
        client.invalid.clear()
        tlen = u32(recv(s, 4))
        if tlen == 0:
            return # client decided not to commit (e.g. conflict)
        tdata = recv(s, tlen)
        logging_debug = is_logging(10)
        logging_debug and log(10, 'Committing %s bytes', tlen)
        self.storage.begin()
        i = 0
        oids = []
        while i < len(tdata):
            rlen = u32(tdata[i:i+4])
            i += 4
            oid = tdata[i:i+8]
            record = tdata[i+8:i+rlen]
            i += rlen
            if logging_debug:
                class_name = extract_class_name(record)
                log(10, '  oid=%-6s rlen=%-6s %s', u64(oid), rlen, class_name)
            self.storage.store(oid, record)
            oids.append(oid)
        assert i == len(tdata)
        self.storage.end()
        log(20, 'Committed %3s objects %s bytes at %s',
            len(oids), tlen, datetime.now())
        s.sendall(STATUS_OKAY)
        for c in self.clients:
            if c is not client:
                c.invalid.update(oids)

    def handle_S(self, s):
        # sync
        client = self._find_client(s)
        log(8, 'Sync %s', len(client.invalid))
        invalid = self.storage.sync()
        assert not invalid # should have exclusive access
        s.sendall(p32(len(client.invalid)) + ''.join(client.invalid))
        client.invalid.clear()

    def handle_P(self, s):
        # pack
        log(20, 'Pack started at %s' % datetime.now())
        if self.packer is None:
            self.packer = self.storage.get_packer()
        s.sendall(STATUS_OKAY)

    def handle_Q(self, s):
        # graceful quit
        log(20, 'Quit')
        raise SystemExit


def wait_for_server(host, port, maxtries=30, sleeptime=2):
    # Wait for the server to bind to the port.
    import time
    for attempt in range(maxtries):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((host, port))
        except socket.error, e:
            if not e.args[0] == errno.ECONNREFUSED:
                raise
            time.sleep(sleeptime)
        else:
            break
    else:
        raise SystemExit('Timeout waiting for port.')
    sock.close()
