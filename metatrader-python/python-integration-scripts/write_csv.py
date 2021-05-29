# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 17:52:13 2018

@author: Juan Esteban
"""

import csv
import os.path as p

#from time import sleep
#import random

# w => write
# a => append


# while True:
#    with open("forex_data.csv", "a", newline = "") as f:
        
#        thewriter = csv.writer(f)
#        thewriter.writerow(["rand1", "rand2", "rand3"])
    
#        for i in range(1, 100):
#            rnum = random.randint(1, 101)
#            thewriter.writerow([rnum, rnum*2, rnum*3])
#            print("New row added")
#            sleep(10)
            
def write_prices(filename, type_access, lista):
    with open(filename, type_access, newline = "") as file:
        handle = csv.writer(file)
        
        # Check if csv exists.        
        if(not p.isfile("./"+filename)):
            handle.writerow(["PRICE"])
            print("Creating a new file...OK")
        else:
            handle.writerow(lista)
            print("New price added to the csv file.")

def write_csv(filename, type_access, lista):
    with open(filename, type_access, newline = "") as file:
        handle = csv.writer(file)
        
        # Check if csv exists.        
        if(not p.isfile("./"+filename)):
            handle.writerow(("TIMEFRAME ID TYPE SYMBOL SIZE PRICE COMMISSION SWAP TP SL COMMENT").split())
            print("Creating a new file...OK")
        else:
            handle.writerow(lista)
            print("New info trade added to the csv file.")
    
    # TIMECURRENT|ID|TYPE(BUY OR SELL|SYMBOL|SIZE|PRICE|COMMISSION|SWAP|TP|SL|COMMENT
    
         #   try:
      #      with open("price_data.csv", "a", newline = "") as file:
      #          handle = csv.writer(file)
                
      #          safe_list = list()
      #          safe_list.append(prices[-1])
                
      #          handle.writerow(safe_list)
      #          print("New price added to the csv file.")
                
      #  except IOError as err:
      #      print("File couldnt be safed ", err.errno," : ",  err.strerror)

    
