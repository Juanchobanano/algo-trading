# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 17:46:29 2019

@author: Juan Esteban
@description

Este script está destinado a emplear las funcionalidades de ForexLabs de la libreria
de Oanda para volver a descargar los datos de las noticias macroeconmicas.
Lo anterior, tiene el objetivo de tener una base de datos con una mejor calidad de datos, 
y más actualizada. Así, realizando un análisis de los datos con ICapital.py, se busca
implementar un algoritmo que haga trades sobre las noticias.

"""

# Import oanda class.
import configparser
import oandaClass

# Read config file.
config = configparser.ConfigParser()
config.read("./oanda.cfg")

# AccountID & Token.
accountID = config["oanda"]["account_id"]
token = config["oanda"]["access_token"]

labs = oandaClass.oandaLabs(accountID)
params = {
 "instrument": "EUR_USD", 
  "period": 86400
}    
print(labs.getCalendar(params))

# Download news and upload to MySQL.