# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 15:22:45 2018

@author: Juan Esteban
"""


"""
MQL5 to Python Message Structure:

* INFO_TYPE. *

--------------------------------------

1) TRADE_INFO.
    
-MAGIC_NUM (EXPERT ID), 
-DATE TIME, 
-DEAL, 
-SYMBOL, 
-TYPE (BUY / SELL), 
-DIRECTION (IN / OUT)
-VOLUME, 
-PRICE (ENTRY / CLOSE), 
-TAKE_PROFIT, 
-STOP_LOSS,
-ORDER, 
-COMMISSION, 
-SWAP, 
-PROFIT, 
-BALANCE, 
-COMMENT

EXAMPLE:
"TRADE_INFO|4376|2018.01.02 00:45:00|1|EURUSD|BUY|IN|0.08|1.20169|1.24169|1.19169|1|0|0|0|MetaTrader-to-Python"

--------------------------------------

2) ACCOUNT_INFO.
    
- DATE TIME, 
- BALANCE,
- CREDIT,
- ACCOUNT PROFIT,
- EQUITY, 
- MARGIN, 
- MARGIN FREE, 
- MARGIN LEVEL, 
- MARGIN SO CALL, 
- MARGIN SO SO.

--------------------------------------
    
"""

# Import libraries.
#import pandas as pd
#import numpy as np
import MySQLdb as msql
from datetime import datetime
#from datetime import timedelta
import csv
import pymail as pymail
import client_socket as courier
#import socket

class interpreter(): 

    def __init__(self):
        
        print("Interpreter Initialized")
        
        # Create connection with local database.
        global db, c, api, tocsv, sendEmails
        
        tocsv = False
        sendEmails = False
        
        try:
            db = msql.connect(host="localhost", user="root", passwd="", db="forex_data") 
            c = db.cursor()
            print("MYSQL connection established!")

        except msql.Error:
            print("MYSQL connection failed !")
            db = None
            c = None
            
            
    def processMessage(self, message):
        
        print("Proccessing Message...")
        
        # Split the message.
        msg = message.split("|")
        print(msg)
        
        # Process message.
        if msg[0] == "TRADE_INFO":
            magic_num = message[1]
            self.saveTradeDB(msg, magic_num)
        elif msg[0] == "ACCOUNT_INFO":
            self.processAccountInfo(msg)
        elif msg[0] == "NEWS_INFO":
            self.processNewsInfo(msg)
        elif msg[0] == "ICAPITAL":
            self.processICapital(msg)
            
    def processICapital(self, msg):
        
        join_message = ""
        for i in range(1, len(msg), 1):
            if i != len(msg) - 1:
                join_message += msg[i] + "|"
            else:
                join_message += msg[i] 
        print("Command sent to MQL5!")
        courier.pythonMessenger(join_message)
        

       
    def processNewsInfo(self, message):

        current_date = datetime.strptime(message[1], '%Y.%m.%d %H:%M')
        next_new_date = datetime(2019, 10, 10, 0, 0, 0)
        diff = next_new_date - current_date
        print(diff)
        
        return False
    
    def processAccountInfo(self, message):
        print("Saving new account info")
        print(message[1:])
        
        save_data = message[1:]
        
        date_time = datetime.strptime(save_data[0], '%Y.%m.%d %H:%M:%S')
        balance = float(save_data[1])
        credit = float(save_data[2])
        account_profit = float(save_data[3])
        equity = float(save_data[4])
        margin = float(save_data[5])
        margin_free = float(save_data[6])
        margin_level = float(save_data[7])
        margin_so_call = float(save_data[8])
        margin_so_so = float(save_data[9])
        
        account_info = [date_time, balance, credit, account_profit, equity, margin, margin_free, margin_level, margin_so_call, margin_so_so];
    
    
        if db != None and c != None:
            try:
                query = "INSERT INTO account_info (date_time, balance, credit, account_profit, equity, margin, margin_free, margin_level, margin_so_call, margin_so_so) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = tuple(account_info)
                c.execute(query, values)
                db.commit()
                print(c.rowcount, " record inserted.")
                
            except c.Error as e: 
                print("ERROR: Database Error...", e)
                print("We will create a CSV file...")
                self.saveCSV("account_info_PYTHON.csv", account_info)
                
                if(sendEmails):
                    message = """\
                    Subject: Database Error.
                    
                    Database connection lost. Account info added to CSV. 
                    This message is sent from Python."""
                    pymail.sendEmailAll(message)
                    
        else:
            print("Not connected to DB...")
            print("We will create a CSV file...")
            self.saveCSV("trades_info_MQL5.csv", account_info)
            
            if(sendEmails):
                message = """\
                Subject: Database object does not exist.
                
                Database not exist. This message is sent from Python."""
                pymail.sendEmailAll(message)
                    
        print("")
            
    def saveTradeDB(self, message, table_name):
        
        print("Saving new trade in DB...")
        print(message)
        save_data = message[2:]
        
        # Get Trade Date and format it.
        date_time = datetime.strptime(save_data[0], '%Y.%m.%d %H:%M')       # DATE TIME
        deal = int(save_data[1])                                                     # DEAL
        symbol = save_data[2]                                                   # SYMBOL.
        order_type = save_data[3]                                               # TYPE (BUY/SELL)
        direction = save_data[4]                                                # DIRECTION (IN/OUT)
        volume = float(save_data[5])                                                   # VOLUME
        price = float(save_data[6])                                                  # PRICE
        take_profit = float(save_data[7])      # TAKE PROFIT
        stop_loss = float(save_data[8])        # STOP LOSS
        order_num = int(save_data[9])                                                   # ORDER NUMBER
        comission = float(save_data[10])       # COMISSION.
        swap = float(save_data[11])          # SWAP
        profit = float(save_data[12])         # PROFIT
        balance = float(save_data[13])         # BALANCE
        comment = save_data[14]          # COMMENT
        
        trades_info = [date_time, deal, symbol, order_type, direction, volume, price, take_profit, stop_loss, order_num, comission, swap, profit, balance, comment]

        if db != None and c != None:
            try:
                query = "INSERT INTO " + table_name + " (date_time, deal, symbol, order_type, direction, volume, price, take_profit, stop_loss, order_num, comission, swap, profit, balance, comment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = tuple(trades_info)
                c.execute(query, values)
                db.commit()
                print(c.rowcount, " record inserted.")           
            except c.Error as e: 
                print("ERROR: Database Error...", e)
                print("We will create a CSV file...")
                self.saveCSV("trades_info_MQL5.csv", trades_info)
                
                if(sendEmails):
                    message = """\
                    Subject: Database Error.
                    
                    Database connection lost. Trade info added to CSV. 
                    This message is sent from Python."""
                    pymail.sendEmailAll(message)
        else:
            print("Not connected to DB...")
            print("We will create a CSV file...")
            self.saveCSV("trades_info_MQL5.csv", trades_info)
            
            if(sendEmails):
                message = """\
                Subject: Database object does not exist.
                
                Database not exist. This message is sent from Python."""
                pymail.sendEmailAll(message)
                                
        print("")


    def saveCSV(self, filename, info):
        with open("./info/" + filename, "a") as file:
            file_writer = csv.writer(file, delimiter='|', quotechar='*', quoting=csv.QUOTE_MINIMAL)
            file_writer.writerow(info)
        return True
    
#inter = interpreter()
#inter.processMessage("TRADE_INFO|4376|2018.01.03 00:45|1|EURUSD|BUY|IN|0.08|1.20169|1.24169|1.19169|1|0|0|0|500000|HOLA MUNDO")    
#meng = messenger()



# ("TRADE|12345|OPEN|1|EURUSD|0|50|50|R-to-MetaTrader4|12345678"
"""
if data == bytes(" ", "utf-8"): 
                
                conn.sendall(bytes("HOLA...", "utf-8") + reply)
                f = open("save_message.txt", "a")
                f.write("Client message: " + reply.decode("utf-8") + "%d\r\n")  
                f.close()
            
                reply = bytes("", "utf-8")
                def processTrade(self, message):
    
        # Splice 1 to get trade info.
        trade_info = message[1: ]
        
        magic_num = trade_info[0]        # EXPERT ID
        date_time = trade_info[1]        # DATE TIME
        deal = trade_info[2]             # DEAL
        symbol = trade_info[3]           # SYMBOL.
        order_type = trade_info[4]       # TYPE (BUY/SELL)
        direction = trade_info[5]        # DIRECTION (IN/OUT)
        volume = trade_info[6]           # VOLUME
        price = trade_info[7]            # PRICE
        take_profit = trade_info[8]      # TAKE PROFIT
        stop_loss = trade_info[9]        # STOP LOSS
        order = trade_info[10]           # ORDER NUMBER
        comission = trade_info[11]       # COMISSION.
        swap = trade_info[12]            # SWAP
        profit = trade_info[13]          # PROFIT
        balance = trade_info[14]         # BALANCE
        comment = trade_info[15]         # COMMENT
                        
        new_entry = pd.DataFrame({
                    "Date_Time": [date_time], 
                    "Deal": [deal], 
                    "Symbol": [symbol], 
                    "Order_Type": [order_type], 
                    "Direction": [direction], 
                    "Volume": [volume], 
                    "Price": [price], 
                    "Take_Profit": [take_profit],
                    "Stop_Loss": [stop_loss],
                    "Order": [order], 
                    "Comission": [comission],
                    "Swap": [swap], 
                    "Profit": [profit], 
                    "Balance": [balance], 
                    "Comment": [comment]
                })
    
        # Create file path.
        filename = "expert_" + magic_num + ".csv"
        filepath = "experts_info/" + filename
        
        # Get historical information.
        try:
            historical_info = pd.read_csv(filepath)
 
            # Concatenate dataframes.
            frames = [historical_info, new_entry]
            result = pd.concat(frames)
        
        except ValueError:
            result = new_entry
        
        # Save Data.
        result.to_csv(filepath)
            
    def processRates(self, message):
        return ""
    
    def processData(self, message):
        return ""
        
               query = "INSERT INTO test_table (TEST_ID) VALUES (%s)"
        values = tuple([8])
        c.execute(query, values)
        db.commit()
        print(c.rowcount, " record inserted.")
        
    
"""

#print("Incoming message...", msg);
        #print("")
    
"""
# Check if there are several messages.
several_messages = list()
if len(msg) > 18:
    while(len(msg) > 0):
        several_messages.append(list(msg[0: 17]))
        msg = msg[19:]
    msg = list(several_messages)
    #print("Message formated...", msg)
else:
    msg = [msg[0: 17]]
    #print("Normal message...", msg)
    
# For every message in message.
for m in msg:    
    if m[0] == "TRADE_INFO":
        self.proccessTrade(m)
    elif m[0] == "PORTAFOLIO_INFO":
        self.processPortfolio(m)
    return ""
"""
"""
 # Initizalize IPFS.
     
        try:
            api = ipfs.connect('127.0.0.1', 5001)
            print("IPFS connection established!")
        except ConnectionError as c:
            print("IPFS connection failed!", c)
            api = None
      
"""