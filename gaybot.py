import requests
import hmac
import hashlib
import time
import math
import datetime
from multiprocessing import Pool

try:
    from urlib import urlencode

except ImportError:
    from urllib.parse import urlencode

#open a file for appending (a). + creates file if does not exist
file = open("log.txt", "a+")

priceSymbols = {'bitcoin': 'BTCUSDT', 'ripple': "XRPBTC",
                'ethereum': 'ETHBTC', 'BCC': 'BCCBTC',
                'LTC': 'LTCBTC', 'Dash': 'DASHBTC',
                'Monero': 'XMRBTC', 'Qtum': 'QTUMBTC', 'ETC': 'ETCBTC',
                'Zcash': 'ZECBTC', 'ADA': 'ADABTC', 'ADX': 'ADXBTC', 'AION' : 'AIONBTC', 'AMB': 'AMBBTC', 'APPC': 'APPCBTC', 'ARK': 'ARKBTC', 'ARN': 'ARNBTC', 'AST': 'ASTBTC', 'BAT': 'BATBTC', 'BCD': 'BCDBTC', 'BCPT': 'BCPTBTC', 'BNB': 'BNBBTC', 'BNT': 'BNTBTC', 'BQX': 'BQXBTC', 'BRD': 'BRDBTC', 'BTS': 'BTSBTC', 'CDT': 'CDTBTC', 'CMT': 'CMTBTC', 'CND': 'CNDBTC', 'CTR':'CTRBTC', 'DGD': 'DGDBTC', 'DLT': 'DLTBTC', 'DNT': 'DNTBTC', 'EDO': 'EDOBTC', 'ELF': 'ELFBTC', 'ENG': 'ENGBTC', 'ENJ': 'ENJBTC', 'EOS': 'EOSBTC', 'EVX': 'EVXBTC', 'FUEL': 'FUELBTC', 'FUN': 'FUNBTC', 'GAS': 'GASBTC', 'GTO': 'GTOBTC', 'GVT': 'GVTBTC', 'GXS': 'GXSBTC', 'HSR': 'HSRBTC', 'ICN': 'ICNBTC', 'ICX': 'ICXBTC', 'IOTA': "IOTABTC", 'KMD': 'KMDBTC', 'KNC': 'KNCBTC', 'LEND': 'LENDBTC', 'LINK':'LINKBTC', 'LRC':'LRCBTC', 'LSK':'LSKBTC', 'LUN': 'LUNBTC', 'MANA': 'MANABTC', 'MCO': 'MCOBTC', 'MDA': 'MDABTC', 'MOD': 'MODBTC', 'MTH': 'MTHBTC', 'MTL': 'MTLBTC', 'NAV': 'NAVBTC', 'NEBL': 'NEBLBTC', 'NEO': 'NEOBTC', 'NULS': 'NULSBTC', 'OAX': 'OAXBTC', 'OMG': 'OMGBTC', 'OST': 'OSTBTC', 'POE': 'POEBTC', 'POWR': 'POWRBTC', 'PPT': 'PPTBTC', 'QSP': 'QSPBTC', 'RCN': 'RCNBTC', 'RDN': 'RDNBTC', 'REQ': 'REQBTC', 'SALT': 'SALTBTC', 'SNGLS': 'SNGLSBTC', 'SNM': 'SNMBTC', 'SNT': 'SNTBTC', 'STORJ': 'STORJBTC', 'STRAT': 'STRATBTC', 'SUB': 'SUBBTC', 'TNB': 'TNBBTC', 'TNT': 'TNTBTC', 'TRIG': 'TRIGBTC', 'TRX': 'TRXBTC', 'VEN': 'VENBTC', 'VIB': 'VIBBTC', 'VIBE': 'VIBEBTC', 'WABI': 'WABIBTC', 'WAVES': 'WAVESBTC', 'WINGS': 'WINGSBTC', 'WTC': 'WTCBTC', 'XVG': 'XVGBTC', 'XZC': 'XZCBTC', 'YOYO': 'YOYOBTC', 'ZRX': 'ZRXBTC'}

api_key = '7WzDy6Hw7HBozQiR1UEpWMgdpzAKQ3ZUSBX6QMra723KO4ot6iAQykbqtqM4hL7Y'

secret_key = 'cHFo1FUc4zRgydNpTDip51S2s12yd7SKe65LS96AgrUxfm8B5Q7HgQcJghitSlNo'

percent_to_spend = 1  # CHANGE TO 0.5

minTransactionAmount = {'BTC': 0.003, 'ETH': 0.01, 'Dash': 0.01, 'LTC': 0.01, 'ETC': 0.01, 'XRP': 21, 'BCH': 0.005,
                        'XMR': 0.1, 'ZEC': 0.01, 'QTUM': 0.1}

stepsizes = {}

potentialCurrency = {}

currencyToTrade = {}

priceList = {}

oldCurrency = ''

currentCurrency = ''

minimumPercentIncrease = 5.0

zeroCounter = 0

today = datetime.date.today()


def buyBin(symbol):
    #current time in ms
    timestamp = int(time.time() * 1000)

    #building the request query url plus other parameters(signed)
    headers = {'X-MBX-APIKEY': api_key}
    infoParameter = {'timestamp': timestamp}
    query = urlencode(sorted(infoParameter.items()))
    signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    query += "&signature=" + signature

    #requesting account info to get the balance
    accountInfo = requests.get("https://api.binance.com/api/v3/account?" + query, headers=headers)
    balance = accountInfo.json()["balances"][0]["free"]

    #multiply balance by constant ratio of how much we want to spend
    # and then convert quantity from BTC price to amount of coin
    balancetospend = float(balance) * percent_to_spend
    ratio = getbinanceprice(symbol)
    quantity = balancetospend / float(ratio) * .95

    # set the step size for the given coin
    stepsize = stepsizes[symbol]
    print("Stepsize of " + symbol + " is " + stepsize + "\n")
    file.write("Stepsize of " + symbol + " is " + stepsize + "\n")
    # making the quantity to buy
    print("Balance: " + str(balance))
    file.write("Balance: " + str(balance) + "\n")
    quantity = float(quantity)

    # based on the stepsize of the currency round the quantity to that amount
    if (float(stepsize) == float(1)):
        quantity = int(quantity)
    if (float(stepsize) == 0.1):
        quantity = math.floor(quantity * 10) / 10
    if (float(stepsize) == 0.01):
        quantity = math.floor(quantity * 100) / 100
    if (float(stepsize) == 0.001):
        quantity = math.floor(quantity * 1000) / 1000

    print('Quantity to buy: ' + str(quantity) + 'of' + symbol)
    file.write('Quantity to buy: ' + str(quantity) + 'of' + symbol + "\n")

    #building the query string for buying(signed)
    buyParameters = {'symbol': symbol, 'side': 'buy', 'type': 'market', 'timestamp': timestamp, 'quantity': quantity}
    query = urlencode(sorted(buyParameters.items()))
    signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    query += "&signature=" + signature

    #actually buying
    testBuy = requests.post("https://api.binance.com/api/v3/order?" + query, headers=headers)
    print(testBuy.text)
    file.write(testBuy.text + "\n")


def sellBin(symbol):
    #current time in ms
    timestamp = int(time.time() * 1000)

    #building the request query url plus other parameters(signed)
    headers = {'X-MBX-APIKEY': api_key}
    infoParameter = {'timestamp': timestamp}
    query = urlencode(sorted(infoParameter.items()))
    signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    query += "&signature=" + signature

    #getting the account info
    accountInfo = requests.get("https://api.binance.com/api/v3/account?" + query, headers=headers)


    #getting rid of the BTC part of the crypto asset name
    if(len(symbol) == 6):
        asset = symbol[0:3]

    if(len(symbol) == 7):
        asset = symbol[0:4]

    if(len(symbol) == 8):
        asset = symbol[0:5]


    #iterating through the account info to find the balance of the coin we're selling
    print(accountInfo.json())
    file.write(accountInfo.json() + "\n")
    for i in accountInfo.json()["balances"]:
        if (i["asset"] == asset):
            balance = i["free"]

    #set the step size for the given coin
    stepsize = stepsizes[symbol]
    print("Stepsize of " + symbol + " is " + stepsize)
    file.write("Stepsize of " + symbol + " is " + stepsize + "\n")
    #making the quantity to sell
    print("Balance: " + str(balance))
    file.write("Balance: " + str(balance) + "\n")
    quantity = float(balance)


    #based on the stepsize of the currency round the quantity to that amount
    if (float(stepsize) == float(1)):
        quantity = int(quantity)
    if (float(stepsize) == 0.1):
        quantity = math.floor(quantity*10)/10
    if (float(stepsize) == 0.01):
        quantity = math.floor(quantity*100)/100
    if (float(stepsize) == 0.001):
        quantity = math.floor(quantity*1000)/1000

    print('Quantity to sell: ' + str(quantity) + ' of ' + symbol + ' with stepsize ' + stepsize)
    file.write('Quantity to sell: ' + str(quantity) + ' of ' + symbol + ' with stepsize ' + stepsize + "\n")

    #building the sell query string
    sellParameters = {'symbol': symbol, 'side': 'sell', 'type': 'market', 'timestamp': timestamp, 'quantity': quantity}
    query = urlencode(sorted(sellParameters.items()))
    signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    query += "&signature=" + signature

    #actually selling
    testSell = requests.post("https://api.binance.com/api/v3/order?" + query, headers=headers)
    print(testSell.text)
    file.write(testSell.text + "\n")


def binStepSize():
    #getting the dictionary of a lot of aggregate data for all symbols
    stepsizeinfo = requests.get("https://api.binance.com/api/v1/exchangeInfo")
    bigdata = stepsizeinfo.json()["symbols"]

    #iterating through the dictionary and adding just the stepsizes into our own dictionary
    for i in bigdata:
        symbol = i["symbol"]
        stepsize = i["filters"][1]["stepSize"]
        temp = {symbol: stepsize}
        stepsizes.update(temp)
        if(float(stepsize) != 1 and float(stepsize) != 0.1 and float(stepsize) != 0.01 and float(stepsize) != 0.001 and 'BTC' in symbol and 'USDT' not in symbol):
            print(str(symbol) + " stepsize: " + stepsize)
            file.write(str(symbol) + " stepsize: " + stepsize + "\n")


def getbinanceprice(currency):
    #setting a start time ~1 hr before the current time for our aggregate price range
    startTime = int(time.time()*1000) - 3500000
    endTime = int(time.time()*1000)

    #getting the aggregate trade data and finding one price to return
    parameter = {'symbol': currency, 'startTime': startTime, 'endTime': endTime}
    binData = requests.get("https://api.binance.com/api/v1/aggTrades", params=parameter)
    binPrice = binData.json()[1]['p']
    return binPrice

def pickCrypto():
    #iterates through our dictionary of every price symbol and find the percent change through api
    startTime = int(time.time()*1000)
    for key, value in priceSymbols.items():
        parameter = {'symbol': value}
        percentChange = requests.get("https://api.binance.com/api/v1/ticker/24hr", params=parameter)
        percentChange = percentChange.json()["priceChangePercent"]

        #checks to see if the percent change is above a threshold
        if (float(percentChange) >= float(minimumPercentIncrease)):
            entry = {value: percentChange}
            currencyToTrade.update(entry)
    endTime = int(time.time()*1000)
    realTime = startTime - endTime
    print(str(realTime))

def priceGetter():
    #creates a list of prices based on the list of 15 cryptos we are looking at
    for key, value in currencyToTrade.items():
        price = getbinanceprice(key)
        priceS = {key: price}
        priceList.update(priceS)


def priceChecker():
    #creates a list of new prices to compare against old price list
    # for the 15 cryptos we are looking at
    newPriceList = {}
    for key, value in currencyToTrade.items():
        price = getbinanceprice(key)
        priceS = {key: price}
        newPriceList.update(priceS)

    #Compares the two price lists and sets the currencyToBuy to be
    # the coin with the highest price increase
    maxPercentChange = 0 #moved out of for loop
    for key, value in priceList.items():
        percentChange = ((float(newPriceList[key]) - float(priceList[key]))/float(priceList[key])) * 100.0
        print(key + " New Price is " + str(newPriceList[key]) + " Old price was: " + str(priceList[key]) + " which gives you a percent change of " + str(percentChange))
        file.write(key + " New Price is " + str(newPriceList[key]) + " Old price was: " + str(priceList[key]) + " which gives you a percent change of " + str(percentChange) + "\n")
        if(percentChange > maxPercentChange):
            maxPercentChange = percentChange
            symbol = key
            currencyToBuy = symbol

    print("Coin with the highest percent change is " + currencyToBuy + " which is " + str(maxPercentChange))
    file.write("Coin with the highest percent change is " + currencyToBuy + " which is " + str(maxPercentChange) + "\n")
    return currencyToBuy #potential runtime error if all negative todo


def main():
    file.write("\n")
    print('------------------------------------------------------------------------------------')
    file.write('------------------------------------------------------------------------------------' + "\n")

    pickCrypto()
    binStepSize()

    x=0
    currentCurrency = ''

    while(x<24):
        priceGetter()
        time.sleep(3600)
        pickCrypto()
        oldCurrency = currentCurrency
        currentCurrency = priceChecker()
        if(oldCurrency != currentCurrency and oldCurrency != ''):
            sellBin(oldCurrency)
        if(oldCurrency != currentCurrency):
            buyBin(currentCurrency)

        x+=1

    sellBin(currentCurrency)


    print('---------------------------||||||||||||||||----------------------------------------')
    file.write('---------------------------||||||||||||||||----------------------------------------' + "\n")
    file.write("\n" + "\n" + "\n")

if __name__ == "__main__":
    main()