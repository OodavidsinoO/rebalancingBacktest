# Auto Balancing Strategy
# - Event: USDT, BTC, ETH
# - Condition: Past N days change in %
# - N Days: 13 Days
# - Timezone: UTC
# - If both change in % of BTC and ETH < 0
#     - Sell all and hold USDT
# - Elif change in BTC > change in ETH
#     - Hold/Buy BTC
# - Elif change in ETH > change in BTC
#     - Hold/Buy ETH

import datetime, sys
import pandas as pd

# Get sys parameters
redownload = False
if len(sys.argv) > 1:
    if sys.argv[1] == 'redownload':
        redownload = True

# parameters
N = 13
PRINCIPLE = 1000 # USDT
FEE = 0.001 # 0.1%
STARTING_DATE = '2020-01-01'

# Load Bitcoin and Ethereum data from online CSV
# Load from local CSV if BTCUSDT_d.csv and ETHUSDT_d.csv are in the folder
try:
    if redownload:
        raise Exception('Redownload')
    btc = pd.read_csv('BTCUSDT.csv', header = 1)
    eth = pd.read_csv('ETHUSDT.csv', header = 1)
except:
    btc = pd.read_csv('https://www.cryptodatadownload.com/cdd/Binance_BTCUSDT_d.csv', header = 1)
    eth = pd.read_csv('https://www.cryptodatadownload.com/cdd/Binance_ETHUSDT_d.csv', header = 1)

# Convert to Pandas DataFrame
btc = pd.DataFrame(btc)
eth = pd.DataFrame(eth)

# Convert to datetime
btc['Date'] = pd.to_datetime(btc['Date'])
eth['Date'] = pd.to_datetime(eth['Date'])

# Set Date as index
btc = btc.set_index('Date')
eth = eth.set_index('Date')

# Sort by Date
btc = btc.sort_index()
eth = eth.sort_index()

# Calculate change in % of BTC and ETH
btc['Change'] = btc['Close'].pct_change(N)
eth['Change'] = eth['Close'].pct_change(N)

# Save to CSV
btc.to_csv('BTCUSDT.csv')
eth.to_csv('ETHUSDT.csv')

# Start Backtesting
inventory = {'USDT': PRINCIPLE, 'BTC': 0, 'ETH': 0}

for date in btc.index:
    # Skip starting date
    if date < datetime.datetime.strptime(STARTING_DATE, '%Y-%m-%d'):
        continue
    # Get change in % of BTC and ETH
    btc_change = btc.loc[date]['Change']
    eth_change = eth.loc[date]['Change']
    # If both change in % of BTC and ETH < 0
    if btc_change < 0 and eth_change < 0:
        # Sell all and hold USDT
        if inventory['BTC'] > 0 or inventory['ETH'] > 0:
            inventory['USDT'] += inventory['BTC'] * btc.loc[date]['Close'] * (1 - FEE)
            inventory['USDT'] += inventory['ETH'] * eth.loc[date]['Close'] * (1 - FEE)
            inventory['BTC'] = 0
            inventory['ETH'] = 0
            print(date, " | ", "Sell all and hold USDT. Value:", inventory['USDT']+inventory['BTC']*btc.loc[date]['Close']+inventory['ETH']*eth.loc[date]['Close'])
    # Elif change in BTC > change in ETH
    elif btc_change > eth_change:
        # Hold/Buy BTC
        if inventory['BTC'] == 0:
            inventory['BTC'] = inventory['USDT'] / btc.loc[date]['Close'] * (1 - FEE)
            inventory['USDT'] = 0
            print(date, " | ", "Buy BTC. Value:", inventory['USDT']+inventory['BTC']*btc.loc[date]['Close']+inventory['ETH']*eth.loc[date]['Close'])
        else:
            print(date, " | ", "Hold BTC. Value:", inventory['USDT']+inventory['BTC']*btc.loc[date]['Close']+inventory['ETH']*eth.loc[date]['Close'])
    # Elif change in ETH > change in BTC
    elif eth_change > btc_change:
        # Hold/Buy ETH
        if inventory['ETH'] == 0:
            inventory['ETH'] = inventory['USDT'] / eth.loc[date]['Close'] * (1 - FEE)
            inventory['USDT'] = 0
            print(date, " | ", "Buy ETH. Value:", inventory['USDT']+inventory['BTC']*btc.loc[date]['Close']+inventory['ETH']*eth.loc[date]['Close'])
        else:
            print(date, " | ", "Hold ETH. Value:", inventory['USDT']+inventory['BTC']*btc.loc[date]['Close']+inventory['ETH']*eth.loc[date]['Close'])
    # Else
    else:
        print(date, " | ", "Do nothing. Value:", inventory['USDT']+inventory['BTC']*btc.loc[date]['Close']+inventory['ETH']*eth.loc[date]['Close'])


# Print final value
print("=====================================")
print("Final Value:", inventory['USDT']+inventory['BTC']*btc.loc[date]['Close']+inventory['ETH']*eth.loc[date]['Close'])
print("Final BTC:", inventory['BTC'])
print("Final ETH:", inventory['ETH'])
print("Final USDT:", inventory['USDT'])
print("Profit:", inventory['USDT']+inventory['BTC']*btc.loc[date]['Close']+inventory['ETH']*eth.loc[date]['Close']-PRINCIPLE)
print("Profit %:", (inventory['USDT']+inventory['BTC']*btc.loc[date]['Close']+inventory['ETH']*eth.loc[date]['Close']-PRINCIPLE)/PRINCIPLE*100)