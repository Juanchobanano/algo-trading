# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 20:00:22 2018

@author: Juan Esteban
"""

import socket
import _thread
import MQL5_Interpreter

# Define host and port.
HOST = "127.0.0.1" # Symbolic name, meaning all available interfaces.
PORT = 9500

# Initialize socket and interpreter.
translator = MQL5_Interpreter.interpreter()
#messenger = MQL5_Interpreter.messenger()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket & Translator created succesfully")

# Bind socket to local host and port.
try: 
    s.bind((HOST, PORT))
    print("Socket bind completed")
    
    # Start listening on socket (5 clients).
    s.listen(5)
    print("Socket now listening!")

except socket.error as msg:
    print("Bind failed. Closing program...")
    exit


# Function for handling connections. 
def clientThread(conn):
    message = bytes("Welcome to the server!", "utf-8")
    conn.send(message)    

    # Client season.
    while True:         
        
        try:
        
            # Receiving data from client.
            data = conn.recv(32768)
            if data.decode("utf-8") == "":
                break
            
            #print("MQL5 Incomming data: ")
            #print(data.decode("utf-8"))
            
            
            #conn.send(bytes("hey!", "utf-8"))
            # Save Data.
            #conn.send(bytes("HOLA DESDE PYTHON", "utf-8"))

            translator.processMessage(data.decode("utf-8"))
            #response = messenger.response()
            
            # Reply message to client.
            #if response != "":
            #    conn.send(response)        
            
        except socket.error: 
            print("Client has disconnected...closing conn socket.")
            print(" ")
            conn.close()
            break
            
    # Came out of loop.
    conn.close()
    
    
# Now keep talking with the client.
while True: 
    print(" ")
    conn, addr = s.accept()
    print("Connected with " + addr[0] + ":" + str(addr[1]))
    _thread.start_new_thread(clientThread, (conn, ))
    #if input("Digite X para finalizar el programa: ") == "X":
    #    break
    #else: 
    #    continue

# Closing pending conn and server socket connections.
if conn:
    print("Conn closed")
    conn.close()
s.close()
print("Socket closed")


s.close()