import websockets
import asyncio
import os
import ast
import requests
import threading
import sqlite3
import time
import pathlib

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


priceSymbols = {'bitcoin': 'btcusdt', 'ripple': "xrpbtc",
                'ethereum': 'ethbtc', 'bcc': 'bccbtc',
                'ltc': 'ltcbtc', 'dash': 'dashbtc',
                'monero': 'xmrbtc', 'qtum': 'qtumbtc', 'etc': 'etcbtc',
                'zcash': 'zecbtc', 'ada': 'adabtc', 'adx': 'adxbtc', 'aion' : 'aionbtc', 'amb': 'ambbtc', 'appc': 'appcbtc', 'ark': 'arkbtc', 'arn': 'arnbtc', 'ast': 'astbtc', 'bat': 'batbtc', 'bcd': 'bcdbtc', 'bcpt': 'bcptbtc', 'bnb': 'bnbbtc', 'bnt': 'bntbtc', 'bqx': 'bqxbtc', 'brd': 'brdbtc', 'bts': 'btsbtc', 'cdt': 'cdtbtc', 'cmt': 'cmtbtc', 'cnd': 'cndbtc', 'dgd': 'dgdbtc', 'dlt': 'dltbtc', 'dnt': 'dntbtc', 'edo': 'edobtc', 'elf': 'elfbtc', 'eng': 'engbtc', 'enj': 'enjbtc', 'eos': 'eosbtc', 'evx': 'evxbtc', 'fuel': 'fuelbtc', 'fun': 'funbtc', 'gas': 'gasbtc', 'gto': 'gtobtc', 'gvt': 'gvtbtc', 'gxs': 'gxsbtc', 'hsr': 'hsrbtc', 'icn': 'icnbtc', 'icx': 'icxbtc', 'iota': "iotabtc", 'kmd': 'kmdbtc', 'knc': 'kncbtc', 'lend': 'lendbtc', 'link':'linkbtc', 'lrc':'lrcbtc', 'lsk':'lskbtc', 'lun': 'lunbtc', 'mana': 'manabtc', 'mco': 'mcobtc', 'mda': 'mdabtc', 'mod': 'modbtc', 'mth': 'mthbtc', 'mtl': 'mtlbtc', 'nav': 'navbtc', 'nebl': 'neblbtc', 'neo': 'neobtc', 'nuls': 'nulsbtc', 'oax': 'oaxbtc', 'omg': 'omgbtc', 'ost': 'ostbtc', 'poe': 'poebtc', 'powr': 'powrbtc', 'ppt': 'pptbtc', 'qsp': 'qspbtc', 'rcn': 'rcnbtc', 'rdn': 'rdnbtc', 'req': 'reqbtc', 'salt': 'saltbtc', 'sngls': 'snglsbtc', 'snm': 'snmbtc', 'snt': 'sntbtc', 'storj': 'storjbtc', 'strat': 'stratbtc', 'sub': 'subbtc', 'tnb': 'tnbbtc', 'tnt': 'tntbtc', 'trig': 'trigbtc', 'trx': 'trxbtc', 'ven': 'venbtc', 'vib': 'vibbtc', 'vibe': 'vibebtc', 'wabi': 'wabibtc', 'waves': 'wavesbtc', 'wings': 'wingsbtc', 'wtc': 'wtcbtc', 'xvg': 'xvgbtc', 'xzc': 'xzcbtc', 'yoyo': 'yoyobtc', 'zrx': 'zrxbtc'}

symbols = ['btcusdt', "xrpbtc",
                'ethbtc', 'bccbtc',
               'ltcbtc', 'dashbtc',
                'xmrbtc','qtumbtc','etcbtc',
                'zecbtc', 'adabtc', 'adxbtc',  'aionbtc','ambbtc','appcbtc','arkbtc', 'arnbtc',  'astbtc',  'batbtc', 'bcdbtc', 'bcptbtc',  'bnbbtc',  'bntbtc',  'bqxbtc','brdbtc', 'btsbtc',  'cdtbtc', 'cmtbtc', 'cndbtc', 'dgdbtc', 'dltbtc', 'dntbtc',  'edobtc',  'elfbtc','engbtc',  'enjbtc', 'eosbtc', 'evxbtc',  'fuelbtc',  'funbtc',  'gasbtc',  'gtobtc', 'gvtbtc', 'gxsbtc', 'hsrbtc', 'icnbtc', 'icxbtc', "iotabtc", 'kmdbtc', 'kncbtc', 'lendbtc', 'linkbtc', 'lrcbtc', 'lskbtc', 'lunbtc', 'manabtc', 'mcobtc', 'mdabtc', 'modbtc','mthbtc', 'mtlbtc', 'navbtc', 'neblbtc', 'neobtc', 'nulsbtc', 'oaxbtc','omgbtc',  'ostbtc', 'poebtc',  'powrbtc',  'pptbtc',  'qspbtc',  'rcnbtc',  'rdnbtc', 'reqbtc', 'saltbtc', 'snglsbtc', 'snmbtc', 'sntbtc', 'storjbtc', 'stratbtc', 'subbtc',  'tnbbtc',  'tntbtc',  'trigbtc', 'trxbtc',  'venbtc', 'vibbtc', 'vibebtc',  'wabibtc',  'wavesbtc',  'wingsbtc', 'wtcbtc', 'xvgbtc', 'xzcbtc',  'yoyobtc',  'zrxbtc']

possibleBuyCryptos = []
possibleSellCryptos = []
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
                while((currBuyLoss > maxLoss and currBuyVolume < desiredVolume)):
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
                    bitcoinPrice = price[0]

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
                            if(currBuyLoss < maxLoss and currBuyVolume > desiredVolume):
                                currBuyLoss = maxLoss + 0.01
                                break
                            elif(currBuyLoss < maxLoss):
                                break
                            # multiply the quantity by the dollar price of crypto to add to the $$ volume we could buy of this crypto
                            currBuyVolume += dollarPrice * float(value[1])


                while((currSellVolume < desiredVolume and currSellLoss > maxLoss)):

                    depth = await websocket.recv()

                    depth = ast.literal_eval(depth)

                    cryptoPrice = await tradesocket.recv()

                    cryptoPrice = ast.literal_eval(cryptoPrice)
                    if('b' in cryptoPrice.keys()):
                        cryptoPrice = float(cryptoPrice['b'])
                    else:
                        break

                    # get the bitcoin price to scale the crypto price to dollars
                    bitcoinPrice = price[0]
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
                            if(currSellLoss < maxLoss and currSellVolume > desiredVolume):
                                currSellLoss = maxLoss + 0.01
                                break
                            elif(currSellLoss < maxLoss):
                                break
                            # multiply by the dollarPrice times the amount of coins you can sell
                            currSellVolume += dollarPrice * float(value[1])



                print(symbol + " Buy Volume: " + str(currBuyVolume) + " Buy Loss: " + str(currBuyLoss) + " Sell Volume: " + str(currSellVolume) + " Sell Loss: " + str(currSellLoss))

                #if it exited the loop with a greater $$$ amount tradable and buyable than we wanted
                if(currBuyVolume > desiredVolume and currBuyLoss > maxLoss):
                    global possibleBuyCryptos
                    with lock:
                        possibleBuyCryptos.append(symbol)

                if(currSellVolume > desiredVolume and currSellLoss > maxLoss):
                    global possibleSellCryptos
                    with lock:
                        possibleSellCryptos.append(symbol)


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


def generatePriceSymbols(desiredVolume, maxLoss, price):
    """
    :param desiredVolume:
    :param maxLoss:
    :return:
    """

    #list to hold all the threads
    threads = []

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
    for i in possibleBuyCryptos:
        i.upper()

    for i in possibleSellCryptos:
        i.upper()

    print("Buy List: {}".format(possibleBuyCryptos))
    print("Num Items: {}".format(len(possibleBuyCryptos)))
    print("Sell List: {}".format(possibleSellCryptos))
    print('Num Items: {}'.format(len(possibleSellCryptos)))
    return possibleBuyCryptos

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
generatePriceSymbols(1000, -1, price)
