# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 19:03:15 2019

@author: Juan Esteban
"""

import smtplib, ssl

def sendEmailTo(message, receiver_email = ""):

    port = 465
    password = """TR{-2C"6:UxB&Jef"""
    sender_email = "tradinginformant@gmail.com"
    
    # Create secure SSL context.
    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context = context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
        #server.quit()
        print("Email sent to ", receiver_email)
        
def sendEmailAll(message):
        
    port = 465
    password = """TR{-2C"6:UxB&Jef"""
    sender_email = "tradinginformant@gmail.com"
    receiver_list = ["juancepeda.gestion@gmail.com", "juancepeda.blockchain@gmail.com", "junes9710@gmail.com"]
    
    # Create secure SSL context.
    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context = context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_list, message)
        #server.quit()
        print("Email sent to ", receiver_list)