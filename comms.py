import os
import sys
import socket

class Fifo_Comms(object):
    def __init__(self, read_file, write_file, read_block_size=50):
        self.read_block_size = read_block_size
	self.read_fifo = os.open(read_file, os.O_RDONLY | os.O_NONBLOCK)
        self.write_fifo = os.open(write_file, os.O_WRONLY | os.O_NONBLOCK)
    
    def __enter__(self):
        return self
    
    def __exit__(self ,type, value, traceback):
        os.close(self.read_fifo)
        os.close(self.write_fifo)

    def write(self, data):
        os.write(self.write_fifo, data)

    def read(self):
        bytes = []
        while True:
            try:
                bytes.append(os.read(self.read_fifo,read_block_size))
            except OSERROR as exc:
                if exc.errno == errno.EAGAIN:
                    return bytes

class Socket_Comms(object):
    def __init__(self, socket_path, block_size=64):
        self.socket_path = socket_path
        self.socket_blocking = False
        self.block_size = block_size

    def __enter__(self):
        try:
            print("Opening Socket")
            # Create UDS Socket
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.connect(self.socket_path)
            self.socket.setblocking(0)
            print("Socket Open")
        except socket.error as err:
            raise err
        return self

    def __exit__(self ,type, value, traceback):
        print("Closing socket")
        self.socket.close()
   
    def write(self, data):
        self.socket.sendall(data)

    def read(self):
        data = []
        try:
            while True:
                data.append(self.socket.recv(self.block_size))
        except socket.error as err:
            raise err
        return data
