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

import datetime, tqdm
import pandas as pd

# parameters
N = [1, 250]
PRINCIPLE = 1000 # USDT
FEE = 0.001 # 0.1%
STARTING_DATE = '2022-01-01'

btcRAW = pd.read_csv('https://www.cryptodatadownload.com/cdd/Binance_BTCUSDT_d.csv', header = 1)
ethRAW = pd.read_csv('https://www.cryptodatadownload.com/cdd/Binance_ETHUSDT_d.csv', header = 1)

Ns = []

for n in tqdm.tqdm(range(N[0], N[1]+1)):
    # Convert to Pandas DataFrame
    btc = pd.DataFrame(btcRAW)
    eth = pd.DataFrame(ethRAW)

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
    btc['Change'] = btc['Close'].pct_change(n)
    eth['Change'] = eth['Close'].pct_change(n)

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
                # print(date, " | ", "Sell all and hold USDT. Value:", inventory['USDT']+inventory['BTC']*btc.loc[date]['Close']+inventory['ETH']*eth.loc[date]['Close'])
        # Elif change in BTC > change in ETH
        elif btc_change > eth_change:
            # Hold/Buy BTC
            if inventory['BTC'] == 0:
                inventory['BTC'] = inventory['USDT'] / btc.loc[date]['Close'] * (1 - FEE)
                inventory['USDT'] = 0
                # print(date, " | ", "Buy BTC. Value:", inventory['USDT']+inventory['BTC']*btc.loc[date]['Close']+inventory['ETH']*eth.loc[date]['Close'])
            else:
                pass
                # print(date, " | ", "Hold BTC. Value:", inventory['USDT']+inventory['BTC']*btc.loc[date]['Close']+inventory['ETH']*eth.loc[date]['Close'])
        # Elif change in ETH > change in BTC
        elif eth_change > btc_change:
            # Hold/Buy ETH
            if inventory['ETH'] == 0:
                inventory['ETH'] = inventory['USDT'] / eth.loc[date]['Close'] * (1 - FEE)
                inventory['USDT'] = 0
                # print(date, " | ", "Buy ETH. Value:", inventory['USDT']+inventory['BTC']*btc.loc[date]['Close']+inventory['ETH']*eth.loc[date]['Close'])
            else:
                # print(date, " | ", "Hold ETH. Value:", inventory['USDT']+inventory['BTC']*btc.loc[date]['Close']+inventory['ETH']*eth.loc[date]['Close'])
                pass
        # Else
        else:
            # print(date, " | ", "Do nothing. Value:", inventory['USDT']+inventory['BTC']*btc.loc[date]['Close']+inventory['ETH']*eth.loc[date]['Close'])
            pass

    # Save N
    Ns.append([n, inventory['USDT']+inventory['BTC']*btc.loc[date]['Close']+inventory['ETH']*eth.loc[date]['Close']])

# Print Best value
print("=====================================")
print(Ns)
print("=====================================")
print("STARTING DATE:", STARTING_DATE)
print("PRINCIPLE:", PRINCIPLE)
print("Best value:", max(Ns, key=lambda x: x[1]))
print("=====================================")
customN = 7
print("(2019) n = ", customN,  "\t\t| Value:", Ns[customN-1][1])
customN = 13
print("(OLD) n = ", customN,  "\t\t| Value:", Ns[customN-1][1])
customN = 247
print("(2020) n = ", customN,  "\t| Value:", Ns[customN-1][1])
customN = 186
print("(2021) n = ", customN,  "\t| Value:", Ns[customN-1][1])
customN = 109
print("(2022) n = ", customN,  "\t| Value:", Ns[customN-1][1])
customN = 47
print("(2023) n = ", customN,  "\t\t| Value:", Ns[customN-1][1])
print("=====================================")