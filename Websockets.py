import websockets
import asyncio
import os
import ast
import threading
import time


import PriceSymbolsUpdater

from Generics import priceSymbols, getLowerCaseDict



#setup the relative file path
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname + '/', '')


class depthThread(threading.Thread):
    def __init__(self, symbol, desiredVolume, maxLoss, price):
        threading.Thread.__init__(self)
        self.symbol = symbol
        self.desiredVolume = desiredVolume
        self.maxLoss = maxLoss
        self.price = price

    def run(self):
        asyncio.new_event_loop().run_until_complete(getDepth(self.symbol, self.desiredVolume, self.maxLoss, self.price))

class priceThread(threading.Thread):
    def __init__(self, price):
        threading.Thread.__init__(self)
        self.price = price

    def run(self):
        #path to save the different text files in
        while True:
            asyncio.new_event_loop().run_until_complete(getBTC(price))
            time.sleep(1)




possibleCryptos = []
lock = threading.Lock()

base = 'wss://stream.binance.com:9443/ws/'
getPriceURL = 'https://api.binance.com/api/v3/ticker/price'

async def getDepth(symbol, desiredVolume, maxLoss, price):
    """
    :param symbol the currency we want the depth for:
    :param desiredPrice the $$$ amount we want to be able to trade:
    :param maxPercent the max percent loss we will take to trade this much money:
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
    global bitcoinPrice
    symbol = symbol
    depthNum = 0
    currBuyLoss = 0
    currSellLoss = 0
    currBuyVolume = 0
    currSellVolume = 0
    symbolPath = str(symbol) + "@depth"
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
                #while the current percentage we allow for both overbuying and underselling is less than our max loss
                # and we still have not reached a quantity high enough that we could buy and sell our target $$$ amount then continue to iterate
                while((currBuyLoss > maxLoss or currBuyVolume < desiredVolume)):
                    #set a variable equal to the payload received from the websocket
                    depth = await websocket.recv()
                    #recv() returns a string represnetaiton of a dictionary but we need a dictionary so this line changes a string to a dictionary
                    depth = ast.literal_eval(depth)

                    cryptoPrice = await tradesocket.recv()

                    cryptoPrice = ast.literal_eval(cryptoPrice)

                    if('a' in cryptoPrice.keys()):
                        cryptoPrice = float(cryptoPrice['a'])
                    else:
                        break

                    #get the bitcoin price to scale the crypto price to dollars
                    bitcoinPrice = price[0]

                    if (bitcoinPrice == None):
                        break;
                    #if the symbol were looking at isnt bitcoin to USDT we need to scale it to dollars using the BTCUSDT price
                    if(symbol != 'btcusdt'):
                        #print(str(symbol) + ':' + str(cryptoPrice) + " BTC: " + str(bitcoinPrice))
                        dollarPrice = float(cryptoPrice) * float(bitcoinPrice)
                    else:
                        dollarPrice = float(cryptoPrice)

                    #this means that there is either a bid or an ask
                    if (depth["u"] - depth["U"] > 0):
                        #iterate through the bids
                        for value in depth['b']:
                            if (value != None):
                                #add the percent change between the price we were expecting to pay and the actualy price of the bid to the percent change for the crypto
                                currBuyLoss = calcPercentChange(cryptoPrice, value[0])
                                #multiply the quantity by the dollar price of crypto to add to the $$ volume we could buy of this crypto
                                currBuyVolume += dollarPrice * float(value[1])

                    #count how many times you've searched for bids and asks to break if we're stuck on a bad coin that isn't being traded
                    depthNum += 1
                    if (depthNum >= 20):
                        break

                depthNum = 0

                while((currSellVolume < desiredVolume or currSellLoss > maxLoss)):

                    depth = await websocket.recv()

                    depth = ast.literal_eval(depth)

                    cryptoPrice = await tradesocket.recv()

                    cryptoPrice = ast.literal_eval(cryptoPrice)
                    if('b' in cryptoPrice.keys()):
                        cryptoPrice = float(cryptoPrice['b'])
                    else:
                        break

                    #get the bitcoin price to scale the crypto price to dollars
                    bitcoinPrice = price[0]
                    if (bitcoinPrice == None):
                        break;

                    # if the symbol were looking at isnt bitcoin to USDT we need to scale it to dollars using the BTCUSDT price
                    if (symbol != 'btcusdt'):
                        #print(str(symbol) + ':' + str(cryptoPrice) + " BTC: " + str(bitcoinPrice))
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
                                currSellVolume += dollarPrice * float(value[1])


                    depthNum += 1
                    if (depthNum >= 20):
                        break

                print(symbol + " Buy Volume: " + str(currBuyVolume) + " Buy Loss: " + str(currBuyLoss) + " Sell Volume: " + str(currSellVolume) + " Sell Loss: " + str(currSellLoss) + " Depth Num: " + str(depthNum))

                #if it exited the loop with a greater $$$ amount tradable and buyable than we wanted
                if(currBuyVolume > desiredVolume and currSellVolume > desiredVolume and currSellLoss > maxLoss and currBuyLoss > maxLoss):
                    global possibleCryptos
                    with lock:
                        possibleCryptos.append(symbol)


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



def generatePriceSymbols(desiredVolume, maxLoss, website='binance'):

    """
    :param desiredVolume:
    :param maxLoss:
    :param website:
    :return:
    """
    global priceSymbols

    #list to hold all the threads
    threads = []

    #get an updated version of price symbols
    symbols = PriceSymbolsUpdater.chooseUpdate(website)

    #get the prices to lowercase
    priceSymbols = getLowerCaseDict(symbols)

    #iterate through the price symbols dictionary and create a thread to find the the depth of that crypto then append the thread to the list of threads
    for key, currencyname in priceSymbols.items():
        thread = depthThread(currencyname, desiredVolume, maxLoss, price)
        thread.start()
        threads.append(thread)
        #asyncio.get_event_loop().run_until_complete(getDepth(value, 10000, -1))

    #wait for all the threads to finish
    for thread in threads:
        thread.join()

    #uppercase the symbols
    for i in possibleCryptos:
        i.upper()

    print("List: {}".format(possibleCryptos))
    print("Num Items: {}".format(len(possibleCryptos)))
    return possibleCryptos

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

#Parallel(n_jobs=-1)(delayed(asyncio.get_event_loop().run_until_complete(getDepth(value, 10000, -1))(value, 10000, -1) for key, value in priceSymbols.items()))
price = [0.0]
thread = priceThread(price)
thread.start()
generatePriceSymbols(1000, -2, price)
