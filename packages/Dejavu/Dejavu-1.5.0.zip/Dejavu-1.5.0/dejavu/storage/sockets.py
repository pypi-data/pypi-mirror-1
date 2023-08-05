try:
    import cPickle as pickle
except ImportError:
    import pickle

import socket
import select


def _define_fixedpoint_states():
    """Add methods to fixedpoint to support pickling."""
    import fixedpoint
    
    if not hasattr(fixedpoint.FixedPoint, "__getstate__"):
        def __getstate__(self):
            return (self.n, self.p)
        fixedpoint.FixedPoint.__getstate__ = __getstate__
        
        def __setstate__(self, v):
            self.n, self.p = v
        fixedpoint.FixedPoint.__setstate__ = __setstate__


def stream(unit):
    data = {}
    if isinstance(unit, dict):
        for key, value in unit.iteritems():
            if value.__class__.__name__ == "FixedPoint":
                _define_fixedpoint_states()
            data[key] = value
    else:
        # Assume it's a dejavu.Unit.
        for key in unit.properties:
            value = getattr(unit, key)
            if value.__class__.__name__ == "FixedPoint":
                _define_fixedpoint_states()
            data[key] = value
    return pickle.dumps(data)

def destream(unit, data):
    # data will be a pickled dictionary of properties for a unit.
    try:
        attrdict = pickle.loads(data)
        if not isinstance(attrdict, dict):
            raise TypeError(attrdict)
    except pickle.UnpicklingError:
        raise TypeError(data)
    for key in unit.properties:
        # Set the attribute directly to avoid __set__ overhead.
        unit._properties[key] = attrdict[key]

def dechunk(data):
    """Extract chunks from a stream of data."""
    chunks = []
    while data:
        size = (256 * int(ord(data[0]))) + int(ord(data[1]))
        chunks.append(data[2:size + 2])
        data = data[size + 2:]
    return chunks

def sendall(conn, msg):
    size = len(msg)
    if size > (256 * 256):
        raise ValueError("msg to send is too large (%s)." % size)
    conn.sendall(chr(size >> 8))
    conn.sendall(chr(size & 0xFF))
    conn.sendall(msg)


class SocketClient(object):
    """Client (dejavu) end of a socket for handling dejavu Units."""
    
    # For some reason, the default of '' for localhost doesn't work on Win2k.
    def __init__(self, host='127.0.0.1', port=51111, timeout=5):
        self.host = host
        self.port = port
        self.timeout = timeout
    
    def query(self, msg):
        """Send msg to the peer and return the response(s) in a list.
        
        Socket responses specify their length in the first two
        bytes (hi, lo). Then, the data follows. If the socket wishes to
        return another "object", it will follow the data with another
        length+data stream.
        """
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Not sure if we should have a timeout or not--
        # some users getting "Address already in use" errors..?
        conn.settimeout(self.timeout)
##        conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        conn.connect((self.host, self.port))
        sendall(conn, msg)
        conn.shutdown(1)
        
        # Receive reply.
        data = []
        while True:
            try:
                chunk = conn.recv(1024)
            except Exception, x:
                if x.args[0] != 10035:
                    raise x
            else:
                if chunk == '':
                    break
                data.append(chunk)
        
        conn.close()
        
        data = dechunk(''.join(data))
        if data and data[0] == 'ERROR':
            # The value in data[1] is a pickled Exception.
            raise pickle.loads(data[1])
        return data


class SocketServer(object):
    """Server end of a socket for handling dejavu Units.
    
    Use this class to build wrappers for non-standard databases or
    other sources of dejavu Units.
    """
    
    def open(self, host='127.0.0.1', port=51111, backlog=5):
        """open(host='127.0.0.1', port=51111, backlog=5)."""
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
##        self.conn.setblocking(0)
        self.conn.bind((host, port))
        self.conn.listen(backlog)
    
    def read(self):
        """read(). Read from the socket."""
        readables, writables, e = select.select([self.conn], [self.conn], [], 1)
        if self.conn in readables:
            (sockobj, address) = self.conn.accept()
            
            data = []
            while True:
                try:
                    chunk = sockobj.recv(1024)
                except Exception, x:
                    if x.args[0] != 10035:
                        raise x
                else:
                    if chunk == '':
                        break
                    data.append(chunk)
            return sockobj, dechunk(''.join(data))[0]
        else:
            return None, ''
    
    def close(self):
        self.conn.close()

