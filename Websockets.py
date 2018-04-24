import websockets
import asyncio
import os
import ast
import requests
import threading

class depthThread(threading.Thread):
    def __init__(self, symbol, desiredVolume, maxLoss):
        threading.Thread.__init__(self)
        self.symbol = symbol
        self.desiredVolume = desiredVolume
        self.maxLoss = maxLoss

    def run(self):
        asyncio.new_event_loop().run_until_complete(getDepth(self.symbol, self.desiredVolume, self.maxLoss))

priceSymbols = {'bitcoin': 'btcusdt', 'ripple': "xrpbtc",
                'ethereum': 'ethbtc', 'bcc': 'bccbtc',
                'ltc': 'ltcbtc', 'dash': 'dashbtc',
                'monero': 'xmrbtc', 'qtum': 'qtumbtc', 'etc': 'etcbtc',
                'zcash': 'zecbtc', 'ada': 'adabtc', 'adx': 'adxbtc', 'aion' : 'aionbtc', 'amb': 'ambbtc', 'appc': 'appcbtc', 'ark': 'arkbtc', 'arn': 'arnbtc', 'ast': 'astbtc', 'bat': 'batbtc', 'bcd': 'bcdbtc', 'bcpt': 'bcptbtc', 'bnb': 'bnbbtc', 'bnt': 'bntbtc', 'bqx': 'bqxbtc', 'brd': 'brdbtc', 'bts': 'btsbtc', 'cdt': 'cdtbtc', 'cmt': 'cmtbtc', 'cnd': 'cndbtc', 'ctr':'ctrbtc', 'dgd': 'dgdbtc', 'dlt': 'dltbtc', 'dnt': 'dntbtc', 'edo': 'edobtc', 'elf': 'elfbtc', 'eng': 'engbtc', 'enj': 'enjbtc', 'eos': 'eosbtc', 'evx': 'evxbtc', 'fuel': 'fuelbtc', 'fun': 'funbtc', 'gas': 'gasbtc', 'gto': 'gtobtc', 'gvt': 'gvtbtc', 'gxs': 'gxsbtc', 'hsr': 'hsrbtc', 'icn': 'icnbtc', 'icx': 'icxbtc', 'iota': "iotabtc", 'kmd': 'kmdbtc', 'knc': 'kncbtc', 'lend': 'lendbtc', 'link':'linkbtc', 'lrc':'lrcbtc', 'lsk':'lskbtc', 'lun': 'lunbtc', 'mana': 'manabtc', 'mco': 'mcobtc', 'mda': 'mdabtc', 'mod': 'modbtc', 'mth': 'mthbtc', 'mtl': 'mtlbtc', 'nav': 'navbtc', 'nebl': 'neblbtc', 'neo': 'neobtc', 'nuls': 'nulsbtc', 'oax': 'oaxbtc', 'omg': 'omgbtc', 'ost': 'ostbtc', 'poe': 'poebtc', 'powr': 'powrbtc', 'ppt': 'pptbtc', 'qsp': 'qspbtc', 'rcn': 'rcnbtc', 'rdn': 'rdnbtc', 'req': 'reqbtc', 'salt': 'saltbtc', 'sngls': 'snglsbtc', 'snm': 'snmbtc', 'snt': 'sntbtc', 'storj': 'storjbtc', 'strat': 'stratbtc', 'sub': 'subbtc', 'tnb': 'tnbbtc', 'tnt': 'tntbtc', 'trig': 'trigbtc', 'trx': 'trxbtc', 'ven': 'venbtc', 'vib': 'vibbtc', 'vibe': 'vibebtc', 'wabi': 'wabibtc', 'waves': 'wavesbtc', 'wings': 'wingsbtc', 'wtc': 'wtcbtc', 'xvg': 'xvgbtc', 'xzc': 'xzcbtc', 'yoyo': 'yoyobtc', 'zrx': 'zrxbtc'}


symbols = ['btcusdt', "xrpbtc",
                'ethbtc', 'bccbtc',
               'ltcbtc', 'dashbtc',
                'xmrbtc','qtumbtc','etcbtc',
                'zecbtc', 'adabtc', 'adxbtc',  'aionbtc','ambbtc','appcbtc','arkbtc', 'arnbtc',  'astbtc',  'batbtc', 'bcdbtc', 'bcptbtc',  'bnbbtc',  'bntbtc',  'bqxbtc','brdbtc', 'btsbtc',  'cdtbtc', 'cmtbtc', 'cndbtc', 'ctrbtc', 'dgdbtc', 'dltbtc', 'dntbtc',  'edobtc',  'elfbtc','engbtc',  'enjbtc', 'eosbtc', 'evxbtc',  'fuelbtc',  'funbtc',  'gasbtc',  'gtobtc', 'gvtbtc', 'gxsbtc', 'hsrbtc', 'icnbtc', 'icxbtc', "iotabtc", 'kmdbtc', 'kncbtc', 'lendbtc', 'linkbtc', 'lrcbtc', 'lskbtc', 'lunbtc', 'manabtc', 'mcobtc', 'mdabtc', 'modbtc','mthbtc', 'mtlbtc', 'navbtc', 'neblbtc', 'neobtc', 'nulsbtc', 'oaxbtc','omgbtc',  'ostbtc', 'poebtc',  'powrbtc',  'pptbtc',  'qspbtc',  'rcnbtc',  'rdnbtc', 'reqbtc', 'saltbtc', 'snglsbtc', 'snmbtc', 'sntbtc', 'storjbtc', 'stratbtc', 'subbtc',  'tnbbtc',  'tntbtc',  'trigbtc', 'trxbtc',  'venbtc', 'vibbtc', 'vibebtc',  'wabibtc',  'wavesbtc',  'wingsbtc', 'wtcbtc', 'xvgbtc', 'xzcbtc',  'yoyobtc',  'zrxbtc']

possibleCryptos = []
lock = threading.Lock()

base = 'wss://stream.binance.com:9443/ws/'
getPriceURL = 'https://api.binance.com/api/v3/ticker/price'

async def getDepth(symbol, desiredVolume, maxLoss):

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

    symbol = symbol
    depthNum = 0
    currBuyLoss = 0
    currSellLoss = 0
    currBuyVolume = 0
    currSellVolume = 0
    symbolPath = str(symbol) + "@depth"
    wsURL = os.path.join(base, symbolPath)

    async with websockets.connect(wsURL) as websocket:

            #while the current percentage we allow for both overbuying and underselling is less than our max loss
            # and we still have not reached a quantity high enough that we could buy and sell our target $$$ amount then continue to iterate
            while((currBuyLoss > maxLoss or currSellLoss > maxLoss) and (currSellVolume < desiredVolume or currBuyVolume < desiredVolume)):

                #set a variable equal to the payload received from the websocket
                depth = await websocket.recv()

                #recv() returns a string represnetaiton of a dictionary but we need a dictionary so this line changes a string to a dictionary
                depth = ast.literal_eval(depth)

                #building the param string to get the price of the crypto in bitcoin need to uppercase the symbol cuz binance sucks
                param = symbol.upper()
                parameter = {'symbol' : param}
                cryptoPrice = requests.get(getPriceURL, params=parameter).json()
                if('price' in cryptoPrice.keys()):
                    cryptoPrice = cryptoPrice['price']
                else:
                    currBuyVolume = desiredVolume + 1
                    break

                #get the bitcoin price to scale the crypto price to dollars
                bitcoinPrice = requests.get(getPriceURL, params={'symbol' : 'BTCUSDT'}).json()
                if ('price' in bitcoinPrice.keys()):
                    bitcoinPrice = bitcoinPrice['price']
                else:
                    currBuyVolume = desiredVolume + 1
                    break

                #if the symbol were looking at isnt bitcoin to USDT we need to scale it to dollars using the BTCUSDT price
                if(symbol != 'btcusdt'):
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
                    #iterate through the asks
                    for value in depth['a']:
                        if(value != None):
                            #add the percent change between the actual price we would get for an ask and the price we thought we would get at the beginning
                            currSellLoss = calcPercentChange(value[0], cryptoPrice)
                            ##multiply the quantity by the dollar price of crypto to add to the $$ volume we could sell of this crypto
                            currSellVolume += float(value[0]) * float(bitcoinPrice) * float(value[1])

                #count how many times you've searched for bids and asks to break if we're stuck on a bad coin that isn't being traded
                depthNum += 1
                if (depthNum >= 20):
                    currBuyVolume = desiredVolume + 1
                    break

            #if it exited the loop with a greater $$$ amount tradable and buyable than we wanted
            if(currBuyVolume > desiredVolume and currSellVolume > desiredVolume):
                global possibleCryptos
                with lock:
                    possibleCryptos.append(symbol)


# just calculates the percent change between two values
def calcPercentChange(startVal, endVal):
    if (float(startVal) == 0.0):
        return float(endVal) * 100.0

    return (((float(endVal) - float(startVal)) / float(startVal)) * 100)


def generatePriceSymbols(desiredVolume, maxLoss):
    #list to hold all the threads
    threads = []

    #iterate through the price symbols dictionary and create a thread to find the the depth of that crypto then append the thread to the list of threads
    for key, currencyname in priceSymbols.items():
        thread = depthThread(currencyname, desiredVolume, maxLoss)
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


#Parallel(n_jobs=-1)(delayed(asyncio.get_event_loop().run_until_complete(getDepth(value, 10000, -1))(value, 10000, -1) for key, value in priceSymbols.items()))

#for key, value in priceSymbols.items():
    #asyncio.get_event_loop().run_until_complete(getDepth(value, 10000, -1))





