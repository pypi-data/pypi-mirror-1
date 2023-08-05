import time
import socket
import select
from errno import *


class Socket(object):
    """
    read from input_buffer to receive bytes
    append to output_buffer to send bytes
    override the on_recv_data, on_send_data, on_lost_connection and
    on_new_connection methods to be notified of socket events.
    """
    def on_lost_connection(self, socket_object): raise NotImplementedError
    def on_new_connection(self, socket_object): raise NotImplementedError
    def on_connected(self, socket_object): raise NotImplementedError

    def __init__(self, s, **kw):
        self.__dict__.update(kw)
        self.s = s
        self.output_buffer = ""
        self.input_buffer = ""
        self.dead = False



class Network(object):
    def __init__(self):
        self.readers = set()
        self.writers = set()
        self.errors = set()
        self.sockets = {}
        self.dead_sockets = set()

    def shutdown(self):
        for s in self.sockets:
            s.close()

    def socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(0)
        so = self.sockets[s] = Socket(s)
        return so

    def restart(self, so):
        so.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        so.s.setblocking(0)
        self.sockets[so.s] = so

    def close(self, so):
        try:
            so.s.shutdown(socket.SHUT_RDWR)
        except socket.error, e:
            errno, msg = e.args
            if errno == ENOTCONN:
                pass
            else:
                raise
        so.s.close()
        try:
            self.sockets.pop(so.s)
        except KeyError: pass
        try:
            self.readers.remove(so.s)
        except KeyError: pass
        try:
            self.writers.remove(so.s)
        except KeyError: pass
        try:
            self.errors.remove(so.s)
        except KeyError: pass

    def listen(self, so, address, protocol_class):
        so.address = address
        so.protocol_class = protocol_class
        so.s.bind(address)
        so.s.listen(5)
        self.readers.add(so.s)
        self.errors.add(so.s)
        so.on_readable = self.accept
    
    def accept(self, so):
        ns, address = so.s.accept()
        self.readers.add(ns)
        self.writers.add(ns)
        self.errors.add(ns)
        nso = self.sockets[ns] =  Socket(ns, on_readable=self.on_readable,on_writable=self.on_writable)
        nso.protocol = so.protocol_class(nso)
        nso.address = address
        nso.on_lost_connection = so.on_lost_connection
        so.on_new_connection(nso)

    def connect(self, so, address, protocol_class):
        so.protocol = protocol_class(so)
        so.address = address
        try:
            so.s.connect(address)
        except socket.error, e:
            errno, msg = e.args
            if errno in (EINPROGRESS, EWOULDBLOCK):
                pass
            else:
                raise
        self.writers.add(so.s)
        self.errors.add(so.s)
        so.on_writable = self.new_connection

    def new_connection(self, so):
        self.readers.add(so.s)
        so.on_writable = self.on_writable
        so.on_readable = self.on_readable
        so.on_connected(so)
    
    def on_exception(self, so):
        if so.dead: return
        self.dead_sockets.add(so)
        so.dead = True

    def on_readable(self, so):
        if so.dead: return
        try:
            data = so.s.recv(4096)
        except socket.error, e:
            errno, msg = e.args
            if errno in (ECONNRESET, ETIMEDOUT, ECONNREFUSED):
                self.on_exception(so)
            else:
                raise
        else:
            if len(data) > 0: 
                so.input_buffer += data
                so.protocol.on_recv_data(so)
            else:
                self.on_exception(so)
        
    def on_writable(self, so):
        if so.dead: return
        try:
            count = so.s.send(so.output_buffer)
        except socket.error, e:
            errno, msg = e.args
            if errno in (EPIPE, ECONNRESET):
                self.on_exception(so)
            else:
                raise
        else:
            so.output_buffer = so.output_buffer[count:]
            so.protocol.on_send_data(so)

    def tick(self, timeout=0):
        if not (self.readers or self.writers or self.errors): return
        r,w,e = select.select(self.readers, self.writers, self.errors,timeout)
        for s in r: 
            so = self.sockets[s]
            so.on_readable(so)
        for s in w:
            so = self.sockets[s]
            so.on_writable(so)
        for s in e:
            so = self.sockets[s]
            self.on_exception(so)
        for so in self.dead_sockets:
            ds = so.s
            so.on_lost_connection(so)
            self.sockets.pop(ds)
            try:
                self.readers.remove(ds)
            except KeyError: pass
            try:
                self.writers.remove(ds)
            except KeyError: pass
            try:
                self.errors.remove(ds)
            except KeyError: pass
        self.dead_sockets = set()

