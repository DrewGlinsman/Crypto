import websockets
import asyncio
import threading
import ast
import pytz
import requests
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import datetime
from Generics import priceSymbols

style.use("ggplot")


class volumeThread(threading.Thread):
    def __init__(self, symbol, timestamp):
        threading.Thread.__init__(self)
        self.symbol = symbol
        self.timestamp = timestamp

    def run(self):
        asyncio.new_event_loop().run_until_complete(getData(self.symbol, self.timestamp))


async def getData(symbol, timestamp):
    """
        :param symbol the currency we want the depth for:

        :return:

        payload return structure

        {
        "e": "depthUpdate", // Event type
        "E": 123456789,     // Event time
        "s": "BNBBTC",      // Symbol
        "U": 157,           // First update ID in event
        "u": 160,           // Final update ID in event
        "b": [              // Bids to be updated
            [
            "0.0024",       // price level to be updated
            "10",
            []              // ignore
            ]
        ],
        "a": [              // Asks to be updated
            [
            "0.0026",       // price level to be updated
            "100",          // quantity
            []              // ignore
            ]
        ]
        }
        """
    base = 'wss://stream.binance.com:9443/ws/'
    getPriceURL = 'https://api.binance.com/api/v3/ticker/price'
    symbol = symbol
    symbolPath = str(symbol) + "@depth"
    depthNum = 0
    buyVolume = 0
    sellVolume = 0
    wsURL = os.path.join(base, symbolPath)

    async with websockets.connect(wsURL) as websocket:
        while(depthNum <= 12):
            # set a variable equal to the payload received from the websocket
            depth = await websocket.recv()

            # recv() returns a string represnetaiton of a dictionary but we need a dictionary so this line changes a string to a dictionary
            depth = ast.literal_eval(depth)

            # building the param string to get the price of the crypto in bitcoin need to uppercase the symbol cuz binance sucks
            param = symbol.upper()
            parameter = {'symbol': param}
            cryptoPrice = requests.get(getPriceURL, params=parameter).json()
            if ('price' in cryptoPrice.keys()):
                cryptoPrice = cryptoPrice['price']

            # get the bitcoin price to scale the crypto price to dollars
            bitcoinPrice = requests.get(getPriceURL, params={'symbol': 'BTCUSDT'}).json()
            if ('price' in bitcoinPrice.keys()):
                bitcoinPrice = bitcoinPrice['price']

            # if the symbol were looking at isnt bitcoin to USDT we need to scale it to dollars using the BTCUSDT price
            if (symbol != 'btcusdt'):
                dollarPrice = float(cryptoPrice) * float(bitcoinPrice)
            else:
                dollarPrice = float(cryptoPrice)

            # this means that there is either a bid or an ask
            if (depth["u"] - depth["U"] > 0):
                for value in depth['b']:
                    if value is not None:
                        buyVolume += dollarPrice * float(value[1])

                for value in depth['a']:
                    if value is not None:
                        sellVolume += dollarPrice * float(value[1])

        # setting up file path to write to
        dirname = os.path.dirname(__file__)

        # converting the timestamp to just days, hours, minutes, seconds
        timestamp = datetime.datetime.fromtimestamp(timestamp / 1000.0)
        timestamp = int(timestamp.strftime("%D%H%M%S"))

        # separate paths for how much volume we can buy and sell
        buyDataPath = "DistributionData/" + symbol + "/" + timestamp + "/Buy"
        buyDataPath = os.path.join(dirname, buyDataPath)

        sellDataPath = "DistributionData/" + symbol + "/" + timestamp + "/Sell"
        sellDataPath = os.path.join(dirname, sellDataPath)

        buyDataFile = open(buyDataPath, "a+")
        sellDataFile = open(sellDataPath, "a+")

        buyDataFile.write("{},".format(buyVolume))
        sellDataFile.write("{},".format(sellVolume))

# start of the main code


# compare current time against 4 pm to see if its within a ten minute interval
baseTS = datetime.datetime(2018, 5, 25, 16, 0, 0)
baseTS = baseTS.astimezone(pytz.timezone('US/Eastern'))

print(baseTS)
x = 0

while(x > 20):
    # get the date current time and set it to US Eastern time
    timestamp = datetime.datetime.now(tz=pytz.UTC)
    timestamp = timestamp.astimezone(pytz.timezone('US/Eastern'))
    print(timestamp)

    timedelta = timestamp.minute - baseTS.minute
    x += 1
    print(timedelta)

# while()
# for key, value in priceSymbols.items():
# asyncio.get_event_loop().run_until_complete(getDepth(value, timestamp)
