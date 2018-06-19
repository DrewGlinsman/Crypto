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
import time
import datetime
from pathlib import Path
from Generics import priceSymbols, maxVolume

style.use("ggplot")


class volumeThread(threading.Thread):
    def __init__(self, symbol, timestamp, percentLoss, priceThread):
        threading.Thread.__init__(self)
        self.symbol = symbol
        self.timestamp = timestamp
        self.percentLoss = percentLoss
        self.priceThread = priceThread

    def run(self):
        asyncio.new_event_loop().run_until_complete(getData(self.symbol, self.timestamp, self.percentLoss, self.priceThread))


class priceThread(threading.Thread):
    def __init__(self, price):
        threading.Thread.__init__(self)
        self.price = price

    def run(self):
        # path to save the different text files in
        while True:
            asyncio.new_event_loop().run_until_complete(getBTC(self.price))
            time.sleep(1)

    def getPrice(self):
        return self.price[0]


async def getData(symbol, timestamp, percentLoss, priceThread):
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
    symbol = symbol
    currBuyLoss = 0
    currSellLoss = 0
    currBuyVolume = 0
    currSellVolume = 0
    buyVolumeDict = {}
    sellVolumeDict = {}
    base = 'wss://stream.binance.com:9443/ws/'
    symbolPath = str(symbol) + "@depth" + '20'
    wsURL = os.path.join(base, symbolPath)
    aggTradeURL = os.path.join(base, str(symbol) + "@ticker")
    '''
    cryptoPaths = os.path.join(dirname + '/', 'databases/')
    pathlib.Path(cryptoPaths).mkdir(parents=True, exist_ok=True)
    database = cryptoPaths + 'btc.db'
    conn = sqlite3.connect(database)
    '''
    async with websockets.connect(wsURL) as websocket:
        async with websockets.connect(aggTradeURL) as tradesocket:
            # while the current percentage we allow for both overbuying and underselling is less than our max loss
            # and we still have not reached a quantity high enough that we could buy and sell our target $$$ amount then continue to iterate
            while(currBuyLoss > percentLoss and currBuyVolume < maxVolume):
                # set a variable equal to the payload received from the websocket
                depth = await websocket.recv()
                # recv() returns a string represnetaiton of a dictionary but we need a dictionary so this line changes a string to a dictionary
                depth = ast.literal_eval(depth)

                cryptoPrice = await tradesocket.recv()

                cryptoPrice = ast.literal_eval(cryptoPrice)

                if('a' in cryptoPrice.keys()):
                    cryptoPrice = float(cryptoPrice['a'])
                else:
                    break

                # get the bitcoin price to scale the crypto price to dollars
                bitcoinPrice = priceThread.getPrice()

                if (bitcoinPrice is None):
                    break
                # if the symbol were looking at isnt bitcoin to USDT we need to scale it to dollars using the BTCUSDT price
                if(symbol != 'btcusdt'):
                    # print(str(symbol) + ':' + str(cryptoPrice) + " BTC: " + str(bitcoinPrice))
                    dollarPrice = float(cryptoPrice) * float(bitcoinPrice)
                else:
                    dollarPrice = float(cryptoPrice)

                # iterate through the bids
                for value in depth['asks']:
                    if (value is not None):
                        # add the percent change between the price we were expecting to pay and the actualy price of the bid to the percent change for the crypto
                        currBuyLoss = calcPercentChange(cryptoPrice, value[0])
                        currBuyLoss = -currBuyLoss
                        # if the loss of the current trade is too high but we already have enough volume set loss to just below max loss so
                        # crypto gets included but if the volume isn't enough simply break out of loop and don't add the volume of the trade
                        # that exceeded the maxloss
                        if(currBuyLoss < percentLoss):
                            currBuyLoss = percentLoss + 0.01
                            break
                        # multiply the quantity by the dollar price of crypto to add to the $$ volume we could buy of this crypto
                        currBuyVolume += dollarPrice * float(value[1])
                        print(str(symbol) + ' Current Buy Volume: ' + str(currBuyVolume) + ' Current Loss ' + str(currBuyLoss))

                if(currBuyLoss == (percentLoss + 0.01)):
                    break

            while(currSellLoss > percentLoss and currSellVolume < maxVolume):

                depth = await websocket.recv()

                depth = ast.literal_eval(depth)

                cryptoPrice = await tradesocket.recv()

                cryptoPrice = ast.literal_eval(cryptoPrice)
                if('b' in cryptoPrice.keys()):
                    cryptoPrice = float(cryptoPrice['b'])
                else:
                    break

                # get the bitcoin price to scale the crypto price to dollars
                bitcoinPrice = priceThread.getPrice()
                if (bitcoinPrice is None):
                    break

                # if the symbol were looking at isnt bitcoin to USDT we need to scale it to dollars using the BTCUSDT price
                if (symbol != 'btcusdt'):
                    # print(str(symbol) + ':' + str(cryptoPrice) + " BTC: " + str(bitcoinPrice))
                    dollarPrice = float(cryptoPrice) * float(bitcoinPrice)
                else:
                    dollarPrice = float(cryptoPrice)

                # check the ask
                for value in depth['bids']:
                    if value is not None:
                        # add the percent change between the actual price we would get for an ask and the price we thought we would get at the beginning
                        currSellLoss = calcPercentChange(cryptoPrice, value[0])

                        # if the current bid exceeded the maxLoss but we already have enough volume to sell set maxLoss to just less than the
                        # maxloss so the crypto will get included and break out of the loop. If the current volume is too low simply break out
                        # of the loop
                        if(currSellLoss < percentLoss):
                            currSellLoss = percentLoss + 0.01
                            break
                        # multiply by the dollarPrice times the amount of coins you can sell
                        currSellVolume += dollarPrice * float(value[1])
                        print(str(symbol) + ' Current Sell Volume: ' + str(currSellVolume) + ' Current Loss ' + str(currSellLoss))

                if(currSellLoss == (percentLoss + 0.01)):
                    break

            print(symbol + " Buy Volume: " + str(currBuyVolume) + " Buy Loss: " + str(currBuyLoss) + " Sell Volume: " + str(currSellVolume) + " Sell Loss: " + str(currSellLoss))

        # creating two dictionaries to store the currency and how much we can buy and sell of it in $$$
        buyVolumeDict = {symbol: [currBuyVolume]}
        sellVolumeDict = {symbol: [currSellVolume]}

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

        # now that we have a timestamp, weekday, the dictionaries we want and the currency pass them to get pickled in the proper place.
        writePickle(symbol, weekday, hourtimestamp, buyVolumeDict, sellVolumeDict)


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


async def getBTC(price):
    base = 'wss://stream.binance.com:9443/ws/'
    btcURL = os.path.join(base, 'btcusdt@aggTrade')
    async with websockets.connect(btcURL) as btcWebsocket:
        btcPrice = await btcWebsocket.recv()

        # have to strip the string of the last two parts of the dictionary
        # because it uses a lowercase true or false which breaks pythons syntax
        btcPrice = btcPrice[:-19]
        btcPrice += '}'
        btcPrice = ast.literal_eval(btcPrice)

    price[0] = float(btcPrice['p'])


def writePickle(symbol, weekday, timestamp, buyVolumeDict, sellVolumeDict):
    # creating the picklefile paths for the dictionaries in the distribution folder, corresponding day of the week and then symbol-timestamp-buyVolume
    buyPickleFile = "DistributionData/" + weekday + "/" + symbol + "-" + timestamp + "-BuyVolume"
    sellPickleFile = "DistributionData/" + weekday + "/" + symbol + "-" + timestamp + "-SellVolume"

    buyPicklePath = Path(buyPickleFile)
    sellPicklePath = Path(sellPickleFile)

    # if the current time stamp already has a pickled dictionary we just want to add to it
    if(buyPicklePath.is_file()):
        with open(buyPickleFile, "rb") as pickle_in:
            newBuyVolumeDict = pickle.load(pickle_in)
            newBuyVolumeDict[symbol].append(buyVolumeDict[symbol][0])
            buyVolumeDict = newBuyVolumeDict

    # if the current time stamp already has a pickled sell dictionary want to add to it
    if(sellPicklePath.is_file()):
        with open(sellPickleFile, "rb") as pickle_in:
            newSellVolumeDict = pickle.load(pickle_in)
            newSellVolumeDict[symbol].append(sellVolumeDict[symbol][0])
            sellVolumeDict = newSellVolumeDict

    # write both the dictionaries into memory
    with open(buyPickleFile, "wb") as pickle_out:
        pickle.dump(buyVolumeDict, pickle_out)

    with open(sellPickleFile, "wb") as pickle_out:
        pickle.dump(sellVolumeDict, pickle_out)


# reads the file given a symbol, day of the week, and hour minute time stamp then returns the dictionaries buy first sell second.
def readPickle(symbol, weekday, timestamp):
    buyPickleFile = 'DistributionData/' + weekday + '/' + symbol + '-' + timestamp + '-' + 'BuyVolume'
    sellPickleFile = 'DistributionData/' + weekday + '/' + symbol + '-' + timestamp + '-' + 'SellVolume'

    with open(buyPickleFile, "rb") as pickle_in:
        buyVolume = pickle.load(pickle_in)

    with open(sellPickleFile, "rb") as pickle_in:
        sellVolume = pickle.load(pickle_in)

    return buyVolume, sellVolume


def main():
    # start of the main code
    # compare current time against 4 pm to see if its within a ten minute interval
    baseTS = datetime.datetime(2018, 5, 25, 16, 30, 0)
    baseTS = baseTS.astimezone(pytz.timezone('US/Eastern'))

    threads = []
    price = [0.0]
    pThread = priceThread(price)
    pThread.start()

    while(True):
        # get the date current time and set it to US Eastern time
        currentTime = datetime.datetime.now(tz=pytz.UTC)
        currentTime = currentTime.astimezone(pytz.timezone('US/Eastern'))

        # find time delta between current time and the base timestamp
        timedelta = currentTime.minute - baseTS.minute
        print('Time delta = ' + str(timedelta))
        if (timedelta % 10 == 0):
            print("Time Difference is 10 minutes")
            threads = []

            for key, currency in priceSymbols.items():
                currency = currency.lower()
                thread = volumeThread(currency, currentTime, -1, pThread)
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()
        time.sleep(1)


if __name__ == "__main__":
    main()