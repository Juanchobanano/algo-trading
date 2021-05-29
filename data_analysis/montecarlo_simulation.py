# -*- coding: utf-8 -*-
"""
Created on Sat Dec 29 10:40:18 2018

@author: Juan Esteban
"""

import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib 
import matplotlib.pyplot as plt

data = pd.read_csv("forex_data.csv", index_col = 0)
data['date_time'] = pd.to_datetime(data['date_time'])

# MonteCarlo simulation.
mont_data = data["balance"]

# Set variables.
last_balance = mont_data.iloc[-1]
num_simulations = 100
num_days = 252
simulation_df = pd.DataFrame()

for x in range(num_simulations):
    count = 0
    profit_vol = mont_data.std()
    price_series = []
    price = last_balance + (1 + np.random.normal(0, profit_vol))
    price_series.append(price)
    
    for y in range(num_days):
        if count == 252:
            break
        price = price_series[count] + (1 + np.random.normal(0, profit_vol))
        price_series.append(price)
        count += 1
        
    simulation_df[x] = price_series
    
fig = plt.figure()
fig.suptitle("Monte Carlo Simulation: Expert 4726")
plt.plot(simulation_df)
plt.axhline(y = last_balance, color = "r", linestyle = "-")
plt.xlabel("Day")
plt.ylabel("Balance")
plt.show()