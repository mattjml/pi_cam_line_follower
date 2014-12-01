import os
import sys

Class Fifo_Comms():
    def __init__(self, read_file, write_file):
	self.read_fifo = open(read_file, "r")
        self.write_fifo = open(write_file, "w")
    
    def __enter__(self):
        return self
    
    def __exit__(self):
        self.read_fifo.close()
        self.write_fifo.close()

    def write(self, data):
        self.write_fifo.write(data)

    def read(self):
        return [line for line in fifo]
