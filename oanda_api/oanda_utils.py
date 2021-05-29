# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 15:50:40 2019

@author: Juan Esteban
"""

# Import Oanda Libraries.
import oandapyV20

import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.forexlabs as labs
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.instruments as instruments

import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.transactions as trans

import configparser
import json

# Read config file.
config = configparser.ConfigParser()
config.read("./oanda.cfg")

# AccountID & Token.
accountID = config["oanda"]["account_id"]
token = config["oanda"]["access_token"]
client = oandapyV20.API(access_token = token)

# Oanda class implementation.
class oandaAccount():
    
    # Init object
    def __init__(self, accountID):
        accountID = accountID
    
    # Get the list of tradable instruments for the given Account. 
    def getInstruments(self):
        r = accounts.AccountInstruments(accountID=accountID)
        rv = client.request(r)
        return json.dumps(rv, indent=2)
        
    # Get the full details for a single Account that a client has access to. 
    # Full pending Order, open Trade and open Position representations are provided.
    def getDetails(self):
        r = accounts.AccountDetails(accountID)
        client.request(r)
        return r.response
        
    # Get a summary for a single Account that a client has access to.
    def getSummary(self):
        r = accounts.AccountSummary(accountID)
        client.request(r)
        return r.response
        
    # Get a list of all Accounts authorized for the provided token.
    def getList(self):
        r = accounts.AccountList()
        client.request(r)
        return r.response
        
        
    # Endpoint used to poll an Account for its current state and changes since a specified TransactionID.
    def getChanges(self):
        r = accounts.AccountChanges(accountID, { "sinceTransactionID": 127 })
        client.request(r)
        return r.response

class oandaLabs():

    # Init object.
    def __init__(self, accountID):
        accountID = accountID        
        
    def getAutochartist(self, params):
        #params = {
        #    "instrument": "EUR_USD"
        #}
        r = labs.Autochartist(params = params)
        client.request(r)
        return r.response
        
    def getCalendar(self, params):
        #params = {
        #    "instrument": "EUR_USD", 
        #    "period": 86400
        #}
        r = labs.Calendar(params = params)
        client.request(r)
        return r.response
                
    def getSpread(self, params):
        #params = {
        #    "instrument": "EUR_USD",
        #    "period": 57600
        #}
        r = labs.Spreads(params=params)
        client.request(r)
        return r.response
        
class oandaInstruments():
    
    def getInstrumentCandles(self, instrument, params):
        #params = {
        #  "count": 5,
        #  "granularity": "M5"
        #}
        r = instruments.InstrumentsCandles(instrument = instrument, params = params)
        client.request(r)
        return r.response
    
    def getOrderBook(self, instrument, params):
        # params: {}
        r = instruments.InstrumentsOrderBook(instrument = instrument, params = params)
        client.request(r)
        return r.response
    
    def getPositionBook(self, instrument, params):
        # params: {}
        r = instruments.InstrumentsPositionBook(instrument = "EUR_USD", params = params)
        client.request(r)
        return r.response
    
class oandaOrders():
    
    def __init__(self, accountID):
        accountID = accountID
        
    def orderCancel(self, orderID):
        r = orders.OrderCancel(accountID = accountID, orderID = orderID)
        client.request(r)
        return r.response
    
    def orderClientExtensions(self, orderID, data):
        r = orders.OrderClientExtensions(accountID, orderID, data = data)
        client.request(r)
        return r.response
    
    def orderCreate(self, data):
        r = orders.OrderCreate(accountID, data = data)
        client.request(r)
        return r.response
    
    def orderDetails(self, orderID):
        r = orders.OrderDetails(accountID = accountID, orderID = orderID)
        client.request(r)
        return r.response
    
    def orderList(self):
        r = orders.OrderList(accountID)
        client.request(r)
        return r.response
    
    def orderReplace(self, orderID, data):
        
        """
        data =
        {
          "order": {
            "units": "-500000",
            "instrument": "EUR_USD",
            "price": "1.25000",
            "type": "LIMIT"
          }
        }
        """
        r = orders.OrderReplace(accountID = accountID, orderID = orderID, data = data)
        client.request(r)
        return r.response
    
    def ordersPending(self):
        r = orders.OrdersPending(accountID)
        client.request(r)
        return r.response
    
class oandaPositions():
      
    def __init__(self, accountID):
        accountID = accountID
        
    def openPositions(self):
        r = positions.OpenPositions(accountID = accountID)
        client.request(r)
        return r.response
    
    def positionClose(self, instrument, data):
        """
        instrument = "EUR_USD"
        data =
        {
          "longUnits": "ALL"
        }
        """
        r= positions.PositionClose(accountID = accountID, instrument = instrument, data = data)
        client.request(r)
        return r.response
    
    def positionDetails(self, instrument):
        r = positions.PositionDetails(accountID, instrument = instrument)
        client.request(r)
        return r.response
    
    def positionList(self):
        r = positions.PositionList(accountID = accountID)
        client.request(r)
        return r.response
    
class oandaPricing():
    
    def __init__(self, accountID):
        accountID = accountID
        
    def getPricingInfo(self, params):
        """
        params =
        {
          "instruments": "EUR_USD,EUR_JPY"
        }
        """
        r = pricing.PricingInfo(self, accountID = accountID, params = params)
        client.request(r)
        return r.response
    
    def getPricingStream(self, params):
        """
        params =
        {
          "instruments": "EUR_USD,EUR_JPY"
        }
        """
        r = pricing.PricingStream(accountID = accountID, params = params)
        client.request(r)
        maxrecs = 100
        for ticks in r: 
            print(json.dumps(R, indent = 4), ", ")
            if maxrecs == 0:
                r.terminate("maxrecs records received")
                
class oandaTrades():
    
    def __init__(self, accountID):
        accountID = accountID
        
    def getOpenTrades(self ):
        r = trades.OpenTrades(accountID = accountID)
        client.request(r)
        return r.response
    
    def tradeCRCDO(self, tradeID, data):
        """
            data =
            {
              "takeProfit": {
                "timeInForce": "GTC",
                "price": "1.05"
              },
              "stopLoss": {
                "timeInForce": "GTC",
                "price": "1.10"
              }
            }
        """
        r = trades.TradeCRCDO(accountID = accountID, tradeID = tradeID, data = data)
        client.request(r)
        return r.response
    
    def tradeClientExtensiones(self, tradeID, data):
        """
        data =
        {
          "clientExtensions": {
            "comment": "myComment",
            "id": "myID2315"
          }
        }
        """
        r = trades.TradeClientExtensiones(accountID = accountID, tradeID = tradeID, data = data)
        client.request(r)
        return r.response
    
    def tradeClose(self, data):
        """
        data =
        {
          "units": 100
        }
        """
        r = trades.TradeClose(accountID = accountID, data = data)
        client.request(r)
        return r.response
    
    def tradeDetails(self, tradeID):
        r = trades.TradeDetails(accountID = accountID, tradeID = tradeID)
        client.request(r)
        return r.response
    
    def tradeList(self, params):
        """
        params =
        {
          "instrument": "DE30_EUR,EUR_USD"
        }
        """
        r = trades.TradesList(accountID = accountID, params = params)
        client.request(r)
        return r.response
        
class oandaTransactions():
    
    def __init__(self, accountID):
        accountID = accountID
        
    def getTransactionDetails(transactionID):
        r = trans.TransactionDetails(accountID = accountID, transactionID = transactionID)
        client.request(r)
        return r.response
    
    def getTransactionIDRange(params):
        """
        {
          "to": 2306,
          "from": 2304
        }
        """
        r = trans.TransactionIDRange(accountID = accountID, params = params)
        client.request(r)
        return r.response
    
    def getTransactionList(params = {}):
        """
        {
          "pageSize": 200
        }
        """
        r = trans.TransactionList(accountID, params = params)
        client.request(r)
        return r.response
    
    def getTransactionsSinceID(params):
        """
        params = {
          "id": 2306
        }
        """
        r = trans.TransactionsSinceID(accountID = accountID, params = params)
        client.request(r)
        return r.response
    
    def getTransactionsStream():
        r = trans.TransactionsStream(accountID = accountID)
        client.request(r)
        maxrecs = 5
        try:
            for T in r.response:
                print(json.dumps(R, indent = 4), ",")
                maxrecs -= 1
                if maxrecs == 0:
                    r.terminate("Got them all")
        except StreamTerminated as e:
            print("Finished: {msg}".format(msg=e))
    
    
        
#lab = oandaLabs(accountID)
#assets = oandaInstruments()


#print(assets.getInstrumentCandles(instrument = "DE30_EUR", params = params))
#print(assets.getOrderBook(instrument = "EUR_USD", params = {}))
#print(assets.getPositionBook(instrument = "EUR_USD", params = {}))