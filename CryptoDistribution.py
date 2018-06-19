import websockets
import asyncio
import threading
import ast
import pytz
import pickle
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
    def __init__(self, symbol, timestamp, percentLoss):
        threading.Thread.__init__(self)
        self.symbol = symbol
        self.timestamp = timestamp
        self.percentLoss = percentLoss

    def run(self):
        asyncio.new_event_loop().run_until_complete(testMethod(self.symbol, self.timestamp, self.percentLoss))


async def testMethod(symbol, timestamp, percentLoss):
    base = 'wss://stream.binance.com:9443/ws/'
    # getPriceURL = 'https://api.binance.com/api/v3/ticker/price'
    symbol = symbol
    symbolPath = str(symbol) + "@depth"
    # buyVolume = 0
    # sellVolume = 0
    wsURL = os.path.join(base, symbolPath)
    maxPercentLoss = percentLoss
    # currBuyLoss = 0
    # currSellLoss = 0
    print(wsURL)
    async with websockets.connect(wsURL) as websocket:
        print("Getting Depth")
        depth = await websocket.recv()
        print(depth)


async def getData(symbol, timestamp, percentLoss):
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
    buyVolume = 0
    sellVolume = 0
    wsURL = os.path.join(base, symbolPath)
    maxPercentLoss = percentLoss
    currBuyLoss = 0
    currSellLoss = 0

    async with websockets.connect(wsURL) as websocket:

        while(currBuyLoss > maxPercentLoss):
            print("I'm gay")
            # set a variable equal to the payload received from the websocket
            depth = await websocket.recv()
            print(depth)
            # print("PACKAGE: " + depth)
            # recv() returns a string represnetaiton of a dictionary but we need a dictionary so this line changes a string to a dictionary
            depth = ast.literal_eval(depth)

            # building the param string to get the price of the crypto in bitcoin, need to uppercase the symbol cuz binance sucks
            param = symbol.upper()
            parameter = {'symbol': param}
            cryptoPrice = requests.get(getPriceURL, params=parameter).json()

            # check to make sure there was a price field returned
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

            print("Dollar Price " + str(dollarPrice))
            # this means that there is either a bid or an ask
            if (depth["u"] - depth["U"] > 0):
                # check the bid
                for value in depth['b']:
                    if value is not None:
                        # add the percent change between the price we were expecting to pay and the actualy price of the bid to the percent change for the crypto
                        currBuyLoss = calcPercentChange(cryptoPrice, value[0])
                        print({} + ": current buy loss: " + {}.format(symbol, currBuyLoss))
                        # multiply by the dollarPrice times the amount of coins you can buy
                        buyVolume += dollarPrice * float(value[1])
                        '''
        while(currSellLoss > maxPercentLoss):
            print("Inside the sell while loop websocket for " + symbol)
            # set a variable equal to the payload received from the websocket
            depth = await websocket.recv()

            # recv() returns a string represnetaiton of a dictionary but we need a dictionary so this line changes a string to a dictionary
            depth = ast.literal_eval(depth)

            # building the param string to get the price of the crypto in bitcoin, need to uppercase the symbol cuz binance sucks
            param = symbol.upper()
            parameter = {'symbol': param}
            cryptoPrice = requests.get(getPriceURL, params=parameter).json()

            # check to make sure there was a price field returned
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
                # check the ask
                for value in depth['a']:
                    if value is not None:
                        # add the percent change between the actual price we would get for an ask and the price we thought we would get at the beginning
                        currSellLoss = calcPercentChange(value[0], cryptoPrice)
                        # multiply by the dollarPrice times the amount of coins you can sell
                        sellVolume += dollarPrice * float(value[1])
        '''
        # creating two dictionaries to store the currency and how much we can buy and sell of it in $$$
        buyVolumeDict = {symbol: buyVolume}
        sellVolumeDict = {symbol: sellVolume}

        # setting up file path to write to
        dirname = os.path.dirname(__file__)

        # get integer representation of day 1 = monday, 7 = sunday
        day = timestamp.isoweekday()

        # dictionary switch statement to change integer representation of the day to a string
        weekday = {
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
            7: "Sunday"
        }[day]

        # converting the timestamp to just days, hours, minutes, seconds
        hourtimestamp = timestamp.strftime("%H%M")
        daytimestamp = timestamp.strftime("%D%H%M")

        # creating the picklefile paths for the dictionaries in the distribution folder, corresponding day of the week and then symbol.timestamp.buyVolume
        print("Pickling: " + str(buyVolumeDict))
        print("Picling: " + str(sellVolumeDict))
        buyPickleFile = "DistributionData/" + weekday + "/" + symbol + "-" + hourtimestamp + "-BuyVolume"
        sellPickleFile = "DistributionData/" + weekday + "/" + symbol + "-" + hourtimestamp + "-SellVolume"

        with open(buyPickleFile, "wb") as pickle_out:
            pickle.dump(buyVolumeDict, pickle_out)

        with open(sellPickleFile, "wb") as pickle_out:
            pickle.dump(sellVolumeDict, pickle_out)
        '''
        # separate paths for how much volume we can buy and sell
        buyDataPath = "DistributionData/" + symbol + "/" + timestamp + "/BuyVolume"
        buyDataPath = os.path.join(dirname, buyDataPath)

        sellDataPath = "DistributionData/" + symbol + "/" + timestamp + "/SellVolume"
        sellDataPath = os.path.join(dirname, sellDataPath)

        buyDataFile = open(buyDataPath, "a+")
        sellDataFile = open(sellDataPath, "a+")

        buyDataFile.write("{},".format(buyVolume))
        sellDataFile.write("{},".format(sellVolume))
        '''

# just calculates the percent change between two values


def calcPercentChange(startVal, endVal):
    """
    :param startVal:
    :param endVal:
    :return:
    """
    if (float(startVal) == 0.0):
        return float(endVal) * 100.0

    return (((float(endVal) - float(startVal)) / float(startVal)) * 100)


def calcVolumes(timestamp, maxLoss):
    threads = []

    for key, currency in priceSymbols.items():
        thread = volumeThread(currency, timestamp, -1)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

# start of the main code


# compare current time against 4 pm to see if its within a ten minute interval
baseTS = datetime.datetime(2018, 5, 25, 16, 31, 0)
baseTS = baseTS.astimezone(pytz.timezone('US/Eastern'))

x = 0

threads = []

'''
for key, currency in priceSymbols.items():
    print(currency)
    buyPickleFile = "DistributionData/Sunday/" + currency + "-1607-BuyVolume"
    sellPickleFile = "DistributionData/Sunday/" + currency + "-1607-SellVolume"
    print(buyPickleFile)
    with open(buyPickleFile, "rb") as pickle_in:
        buyVolume = pickle.load(pickle_in)

    with open(sellPickleFile, "rb") as pickle_in:
        sellVolume = pickle.load(pickle_in)

    print(buyVolume)
    print(sellVolume)
    print(currency)
    print("Amount of " + currency + " we can buy: " + str(buyVolume[currency]))
    print("Amount of " + currency + " we can sell: " + str(sellVolume[currency]))
'''

while(x < 3):
    # get the date current time and set it to US Eastern time
    currentTime = datetime.datetime.now(tz=pytz.UTC)
    currentTime = currentTime.astimezone(pytz.timezone('US/Eastern'))
    day = currentTime.isoweekday()
    weekday = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
    }[day]
    print(weekday)
    print(currentTime)

    # find time delta between current time and the base timestamp
    timedelta = currentTime.minute - baseTS.minute
    x += 1
    print(timedelta)
    if (timedelta % 10 == 0):
        print("Time Difference is 10 minutes")

        #calcVolumes(currentTime, -1)

        threads = []

        for key, currency in priceSymbols.items():
            currency = currency.lower()
            thread = volumeThread(currency, currentTime, -1)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        print("finished")
        # while()
        # for key, value in priceSymbols.items():
        # asyncio.get_event_loop().run_until_complete(getDepth(value, timestamp)
