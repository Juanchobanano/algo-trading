# -*- coding: utf-8 -*-
"""
Created on Fri Dec 28 18:43:25 2018

@author: Juan Esteban
"""

import socket

HOST = "127.0.0.1" # Symbolic name, meaning all available interfaces.
PORT = 23456

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket & Translator created succesfully")

s.connect((HOST, PORT))
s.sendall(bytes('Hello, world', "utf-8"))
data = s.recv(1024)
print("Message sent!")
print('Received', repr(data))
s.close()
print("Client disconnected")


class messenger():
      def __init__(self):
          print("Messenger initalized!")
          
      def open_trade(self):
          return ""
      
      def close_trade(self):
          return ""
      
      def modify_trade(self):
          return ""
      
      def activate_expert(self):
          return ""
      
      def deactivate_expert(self):
          return ""
          
      def response(self):
          return ""
          
    