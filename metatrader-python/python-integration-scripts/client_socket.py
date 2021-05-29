# -*- coding: utf-8 -*-
"""
Created on Tue Jan  1 11:12:07 2019

@author: Juan Esteban
"""

"""
2) EXECUTE_ACTION.
    
1) ON_ORDER

- EXPERT_ID
- TICKET_ID (IF EXISTS)
- ACTION (BUY/SELL/MODIFY)
- PRICE
- TAKE_PROFIT
- STOP_LOSS
- COMMENT

"56532|MODIFY|1.2659|1.2784|1.2568|Python-to-MetaTrader"

2) ON_EXPERT
    
- EXPERT_ID    
- ACTION (ACTIVATE / DEACTIVATE)
- CLOSE_POSITION (TRUE / FALSE)
- COMMENT

"4376|ACTIVATE|Python-to-MetaTrader"


# TYPES OF MESSAGES.

#pythonMessenger("ALLOCATION|4562:0.02")
#pythonMessenger("ON_ORDER|4562|TRADE_ACTION_PENDING|19|0|1.2685|1.1246|Hello from Python")
#pythonMessenger("ON_EXPERT|4562|TRUE|TRUE|Hello from Python")
#pythonMessenger("ON_TIME|4562|FALSE|TRUE|TRUE|TRUE|TRUE|0|24|0|60")

"""

import socket 

# Process Errors and Success from python messenger object.      
def processMQLResponse(data):
    
    
    print(data)
    
    return ""      
        
def pythonMessenger(message, HOST = "127.0.0.1", PORT = 23456):
    
    print(" ")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Client socket initialized!")
    
    s.connect((HOST, PORT))
    print("Socket client connected to port!")
    
    data = s.recv(1024)
    print("Received: ", repr(data))
        
    print("Sending message...")
    s.sendall(bytes(message, "utf-8"))
            
    print("Waiting for answer...")
    answer = s.recv(1024)
    processMQLResponse(repr(answer))
    print("Answer: ", repr(answer))
    
    print("Closing socket...")
    s.close()
    
    print(" ")
    
    return answer.decode("utf-8")

pythonMessenger("ALLOCATION|4562:0.02")