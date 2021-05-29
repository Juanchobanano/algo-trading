# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 18:33:20 2019

@author: Juan Esteban

@description
Este script corresponde a una plantilla base para futuros algoritmos de trading
que corren directamente desde Python, los cuales pueden incorporar tanto análisis 
técnico, fundamental, modelos de inteligencia artifical para predicción de retornos, 
entre otros.

Para lograr el objetivo anterior, se incorporó la clase oandaClass, la cual cuenta
con una API que se conecta al broker Oanda directamente, y tiene una gran cantidad 
de funcionalidades.

Estos algoritmos de trading incorporarán de manera local toda la lógica de la 
estrategia, y se limitarán únicamente a guardar la información de los trades
en MySQL con un identificador de cada estrategia.

De esta manera, ICapital.py sólo se encargará de analizar y presentar información.
A futuro, se espera desarrollar un portal web en donde la información del fondo
se actualice cada vez que ocurra una operación, tanto en las estrategias que 
corren localmente en Python, como las estrategias que corren en MQL5.

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
