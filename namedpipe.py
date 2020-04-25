# Copyright (c) Anand Krishnamoorthi
# Licensed under the MIT License

from os import (close, getpid, mkfifo, open, read, write, unlink,
                O_RDONLY, O_RDWR)
from sys import exit
from threading import Thread

class NamedPipe:
    def __init__(self, name):
        self.path = name
        self.fd = None
        self.t = None
        try:
            mkfifo(self.path)
        except:
            pass

    def begin_reading(self, callback):
        def reader():
            self.fd = open(self.path, O_RDONLY)
            buffer = b''
            while True:
                try:                                        
                    p = buffer.find(b'\0')
                    if p >= 0:
                        chunk = buffer[0:p].decode('utf-8')
                        buffer = buffer[p+1:]
                        if chunk != '':                    
                            callback(chunk)
                        continue
                    buffer += read(self.fd, 4096)
                except:
                    pass
        if not self.fd:            
            self.t = Thread(target=reader)
            self.t.daemon = True
            self.t.start()

    def write(self, obj):
        if not self.fd:
            self.fd = open(self.path, O_RDWR)
        write(self.fd, str(obj).encode('utf-8'))
        write(self.fd, b'\0')

    def close(self):
        try:
            if self.fd:
                close(self.fd)
        except:
            pass
        try:
            unlink(self.path)
        except:
            pass
        
    def __del__(self):
        self.close()

