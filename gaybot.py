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

#dictionary with lists that will hold the % changes for each crypto calculated from the klines data
percentChanges = {'BTCUSDT': [], 'XRPBTC': [],
                'ETHBTC': [], 'BCCBTC': [],
                'LTCBTC': [], 'DASHBTC': [],
                'XMRBTC': [], 'QTUMBTC': [], 'ETCBTC': [],
                'ZECBTC': [], 'ADABTC': [], 'ADXBTC': [], 'AIONBTC' : [], 'AMBBTC': [], 'APPCBTC': [], 'ARKBTC': [], 'ARNBTC': [], 'ASTBTC': [], 'BATBTC': [], 'BCDBTC': [], 'BCPTBTC': [], 'BNBBTC': [], 'BNTBTC': [], 'BQXBTC': [], 'BRDBTC': [], 'BTSBTC': [], 'CDTBTC': [], 'CMTBTC': [], 'CNDBTC': [], 'CTRBTC': [], 'DGDBTC': [], 'DLTBTC': [], 'DNTBTC': [], 'EDOBTC': [], 'ELFBTC': [], 'ENGBTC': [], 'ENJBTC': [], 'EOSBTC': [], 'EVXBTC': [], 'FUELBTC': [], 'FUNBTC': [], 'GASBTC': [], 'GTOBTC': [], 'GVTBTC': [], 'GXSBTC': [], 'HSRBTC': [], 'ICNBTC': [], 'ICXBTC': [], 'IOTABTC': [], 'KMDBTC': [], 'KNCBTC': [], 'LENDBTC': [], 'LINKBTC': [], 'LRCBTC': [], 'LSKBTC': [], 'LUNBTC': [], 'MANABTC': [], 'MCOBTC': [], 'MDABTC': [], 'MODBTC': [], 'MTHBTC': [], 'MTLBTC': [], 'NAVBTC': [], 'NEBLBTC': [], 'NEOBTC': [], 'NULSBTC': [], 'OAXBTC': [], 'OMGBTC': [], 'OSTBTC': [], 'POEBTC': [], 'POWRBTC': [], 'PPTBTC': [], 'QSPBTC': [], 'RCNBTC': [], 'RDNBTC': [], 'REQBTC': [], 'SALTBTC': [], 'SNGLSBTC': [], 'SNMBTC': [], 'SNTBTC': [], 'STORJBTC': [], 'STRATBTC': [], 'SUBBTC': [], 'TNBBTC': [], 'TNTBTC': [], 'TRIGBTC': [], 'TRXBTC': [], 'VENBTC': [], 'VIBBTC': [], 'VIBEBTC': [], 'WABIBTC': [], 'WAVESBTC': [], 'WINGSBTC': [], 'WTCBTC': [], 'XVGBTC': [], 'XZCBTC': [], 'YOYOBTC': [], 'ZRXBTC': []}

#special dictionary, houses the % change by hour, the % time spent increasing, and the % of time increasing (weighted)
differentName = {'BTCUSDT': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XRPBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'ETHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'LTCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DASHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'XMRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'QTUMBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ETCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'ZECBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ADABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ADXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'AIONBTC' : {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'AMBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'APPCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ARKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ARNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ASTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BATBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCPTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BNBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BQXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BRDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BTSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CDTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CMTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CNDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CTRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DGDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DLTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EDOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ELFBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ENGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ENJBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EOSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EVXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'FUELBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'FUNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GASBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GTOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GVTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GXSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'HSRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ICNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ICXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'IOTABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'KMDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'KNCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LENDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LINKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LRCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LSKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LUNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MANABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MCOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MDABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MODBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MTHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MTLBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NAVBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NEBLBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NEOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NULSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OAXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OMGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OSTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'POEBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'POWRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'PPTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'QSPBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'RCNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'RDNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'REQBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SALTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNGLSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNMBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'STORJBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'STRATBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SUBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TNBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TRIGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TRXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VENBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VIBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VIBEBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WABIBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WAVESBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WINGSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WTCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XVGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XZCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'YOYOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ZRXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}}

#dictionary just to hold the scores calculated for each crypto
scores =  {}

stepsizes = {}

currentCrypto = {}

currencyToTrade = {}

priceList = {}

oldCurrency = ''

currentCurrency = ''

initialBalance = 0.0

currentBalance = 0.0

minimumPercentIncrease = 5.0

zeroCounter = 0

minimumScore = 2.7

#number in seconds that determines the maximum time a crypto will be held without checkin for a potential switch
MAX_TIME_CYCLE = 3600

#number of cycles run with each run of this bot
MAX_CYCLES = 24

#max percent change before the bot sells and exits
MAX_PERCENT_CHANGE = 20

#weight to make negative numbers worse than positive.
NEGATIVE_WEIGHT = 1.6
#0 is false, 1 is true
RESTART = 0
RESTART_TN = 0
EXIT = 0

#calculated cumulative percentChange with the current cycle

cumulativePercentChange = 0.0


priceBought = 0.0

today = datetime.date.today()


def getBalance(symbol):
    timestamp = int(time.time() * 1000) - 1000
    # building the request query url plus other parameters(signed)
    headers = {'X-MBX-APIKEY': api_key}
    infoParameter = {'timestamp': timestamp}
    query = urlencode(sorted(infoParameter.items()))
    signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    query += "&signature=" + signature

    # requesting account info to get the balance
    accountInfo = requests.get("https://api.binance.com/api/v3/account?" + query, headers=headers)
    print(str(accountInfo.text))
    accountInfo = accountInfo.json()["balances"]

    balance = 0

    for val in accountInfo:
        if(val["asset"] == symbol):
            balance = val["free"]

    return balance

def buyBin(symbol):
    timestamp = int(time.time() * 1000)
    balance = getBalance('BTC')

    #multiply balance by constant ratio of how much we want to spend
    # and then convert quantity from BTC price to amount of coin
    balancetospend = float(balance) * percent_to_spend
    ratio = getbinanceprice(symbol)
    #mark item as the current crypto being traded and save the buy price at for failure condition
    entry = {symbol:{'buyPrice': ratio, 'timestamp': timestamp}}
    currentCrypto.clear()
    currentCrypto.update(entry)
    quantity = balancetospend / float(ratio) * .9

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
    headers = {'X-MBX-APIKEY': api_key}
    buyParameters = {'symbol': symbol, 'side': 'buy', 'type': 'market', 'timestamp': timestamp, 'quantity': quantity}
    query = urlencode(sorted(buyParameters.items()))
    signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    query += "&signature=" + signature

    #actually buying
   # testBuy = requests.post("https://api.binance.com/api/v3/order?" + query, headers=headers)
   # print(testBuy.text)
   # file.write(testBuy.text + "\n")


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
    file.write(str(accountInfo.json())+ "\n")
    for i in accountInfo.json()["balances"]:
        if (i["asset"] == asset):
            balance = i["free"]

    #set the step size for the given coin
    stepsize = stepsizes[symbol]
    print("Stepsize of " + symbol + " is " + stepsize)
    file.write("Stepsize of " + str(symbol) + " is " + str(stepsize) + "\n")
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
   # testSell = requests.post("https://api.binance.com/api/v3/order?" + query, headers=headers)
   # print(testSell.text)
   # file.write(testSell.text + "\n")


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


def getVolume(interval, starttime, endtime, currency):
    parameters = {"symbol": currency, "interval": interval, 'startTime': starttime, 'endTime': endtime}
    data = requests.get("https://api.binance.com/api/v1/klines", params=parameters)
    data = data.json()
    slots = 0
    volume = 0
    print(data)
    for value in data:
        slots += 1
        fuckthis = float(value[5])
        fuckthis = int(fuckthis)
        volume += (fuckthis * (slots/45))
    volume *= float(getbinanceprice(currency))
    print(currency + " Volume/Price: " + str(volume))
    return volume

def getbinanceprice(currency):
    #getting the aggregate trade data and finding one price to return
    binData = requests.get("https://api.binance.com/api/v1/ticker/allPrices")
    binData = binData.json()
    for value in binData:
        if(value["symbol"] == currency):
            binPrice = value["price"]

            break;
    print("Price: " + str(binPrice))
    priceBought = binPrice

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


    #interval based on this from binance API
    #     m -> minutes;     h -> hours;     d -> days;     w -> weeks;    M -> months
    #  1m  3m   5m  15m  30m  1h 2h 4h 6h 8h  12h  1d   3d  1w   1M
    # method used to update price lists on past hour of trends

def updateCrypto(interval, starttime, endtime):

    for key,value in priceSymbols.items():
        parameter = {'symbol': value, 'interval': interval, 'startTime': starttime, 'endTime': endtime}
        percentChange = requests.get("https://api.binance.com/api/v1/klines", params=parameter)
        percentChange = percentChange.json()

        #calculate the percent change over the whole hour and store
        openPrice = percentChange[0][1]
        closePrice = percentChange[19][4]
        differentName[value]['percentbyhour'] = calcPercentChange(openPrice, closePrice)
        #print(str(value) + ' open  ' + str(openPrice) + ' close ' + str(closePrice) + ' % change ' + str(differentName[value]['percentbyhour']))

        #calculate the percentage change between the minute intervals and store
        #reset the list of stored percentages so a fresh list is stored
        percentChanges[value] = []
        for i in percentChange:
            percentChanges[value].append(calcPercentChange(i[1], i[4]))
        #print(str(value) + ' % percent changes ' + str(percentChanges[value]))

        #calculate and store the % time increasing
        differentName[value]['timeIncreasing'] = getTimeIncreasing(0, value)
        differentName[value]['weightedtimeIncreasing'] = getTimeIncreasing(1, value)
        #print (str(value) + ' % time increasing ' + str(differentName[value]['timeIncreasing']))
       # print(str(value) + ' % time increasing weighted ' + str(differentName[value]['weightedtimeIncreasing']))

        #use the calculations to get a score
        calc_score = getScore(value)
        new_score = {value: calc_score}
        scores.update(new_score)

    for key, value in scores.items():
        if(value > minimumScore):
            entry = {key: value}
            currencyToTrade.update(entry)

    print ("OUR LIST OF CRYPTO")
    print(currencyToTrade)
    file.write("OUR LIST OF CRYPTO")
    file.write(str(currencyToTrade))

#caclulates and returns the time spent increasing
#weighted = 0 is false, weighted = 1 is true
def getTimeIncreasing(isWeighted, currency):

    list = percentChanges[currency]
    slots = 0.0
    slots_increasing = 0.0
    positiveCounter = 0
    negativeCounter = 0
    for  i in list:
            slots+=1

            #the two if statements only differ in that the second one
            #caclcualtes slots_increasing using a weight
            #that casues positive increases early in the hour to matter less
            #than increases later in the hour
            if(currency == "VENBTC"):
                print("Current Percent Increase/Decrease: " + str(i))
                print("Previous Weight: " + str(slots_increasing))

            if float(i)  > 0.0 and isWeighted == 0:
              slots_increasing+=1*i
              positiveCounter+=1

            if float(i) < 0.0 and isWeighted == 0:
              slots_increasing += 1 * i * NEGATIVE_WEIGHT
              negativeCounter+=1
            if float(i) > 0.0 and isWeighted == 1:
              slots_increasing+=(1*(slots/50.0)*i)
              positiveCounter+=1

            if float(i) < 0.0 and isWeighted == 1:
              slots_increasing += (1*(slots/50.0)*i * NEGATIVE_WEIGHT)
              negativeCounter+=1

            if(currency=="VENBTC"):
              print("Current Weight: " + str(slots_increasing))
              print("Positive increases: " + str(positiveCounter) + "Negative increases: " + str(negativeCounter))

    return (slots_increasing/slots)

# method to calculate the "score" that crypto get when they are updated by hour
# score is a combination of weighted time increasing and %change over hour.
#calculation should have more factors added
def getScore(symbol):
    new_score = 1

    new_score *= differentName[symbol]['percentbyhour']
    m = new_score * differentName[symbol]['weightedtimeIncreasing']
    w = new_score + differentName[symbol]['weightedtimeIncreasing']
    c = new_score * differentName[symbol]['timeIncreasing']
    e = new_score + differentName[symbol]['timeIncreasing']
    print(symbol + ": " + str(w) + " Absolute increasing weight: " + str(e))
    #print(' multiply by weight ' + str(m))
    #print(' add the weight ' + str(w))

    return w



def priceChecker():

    #Compares the two price lists and sets the currencyToBuy to be
    # the coin with the highest score
    maxScore = 0 #moved out of for loop
    for key, value in currencyToTrade.items():
        print("The score of " + key + " is " + str(scores[key]))
        file.write("The score of " + key + " is " + str(scores[key]) + "\n")
        if(maxScore < scores[key]):
            maxScore = scores[key]
            print("CURRENT HIGH SCORE: The score of " + key + " is " + str(scores[key]))
            file.write("CURRENT HIGH SCORE: The score of " + key + " is " + str(scores[key]) + "\n")
            currencyToBuy = key

    print("Coin with the highest score is " + currencyToBuy + " which is " + str(maxScore))
    file.write("Coin with the highest score is " + currencyToBuy + " which is " + str(maxScore) + "\n")
    return currencyToBuy #potential runtime error if all negative todo


#just calculates the percent change between two values
def calcPercentChange(startVal, endVal):
    if(endVal == 0):
        return startVal * 100
    return (((float(endVal) - float(startVal))/float(startVal) ) * 100)


#checks if the current crypto has been decreasing the past five minutes
#if yes it forces a new check to see if there is a better crypto
def checkFailureCondition(currency):
    print("New Interval")
    file.write("New Interval")
    #price = getbinanceprice(currency)
    #change = calcPercentChange(currentCrypto[currency]['buyPrice'], price)

    startTime = int(time.time()*1000) - 300000
    endTime = int(time.time())*1000

    parameter = {'symbol': currency, 'interval': '1m', 'startTime': startTime, 'endTime': endTime}
    percentChange = requests.get("https://api.binance.com/api/v1/klines", params=parameter)
    percentChange = percentChange.json()
    timeIncreasingCounter = 0

    for i in percentChange:
        startPrice = i[1]
        endPrice = i[4]
        print("Current Crypto: " + currency + " Start Price: " + str(startPrice) + " End Price: " + str(endPrice))
        file.write("Current Crypto: " + currency + " Start Price: " + str(startPrice) + " End Price: " + str(endPrice))
        percentChange = calcPercentChange(startPrice, endPrice)
        if(percentChange > 0):
            timeIncreasingCounter += 1

    cumulativePercentChange = calcPercentChange(priceBought, endPrice)
    print("Cumulative percent change over THIS INTERVAL " + str(cumulativePercentChange))
    file.write("Cumulative percent change over THIS INTERVAL " + str(cumulativePercentChange))

    print("Times Increasing over the interval: " + str(timeIncreasingCounter))
    file.write("Times Increasing over the interval: " + str(timeIncreasingCounter) + "\n")
    if(timeIncreasingCounter==0):
        print("DECREASED ALL INTERVALS. RESTART")
        file.write("DECREASED ALL INTERVALS. RESTART")
        return 1

    return 0

#checks whether the function has caused too large of negative decrease the specified interval
def checkTooNegative(symbol):
    startTime = int(time.time()) * 1000 - 60000
    endTime = int(time.time()) * 1000

    parameter = {'symbol': symbol, 'interval': '1m', 'startTime': startTime, 'endTime': endTime}
    percentChange = requests.get("https://api.binance.com/api/v1/klines", params=parameter)
    percentChange = percentChange.json()

    if (percentChange == []):
        return 0


    startPrice = percentChange[0][1]
    endPrice = percentChange[0][4]
    percentChange = calcPercentChange(startPrice, endPrice)

    if(percentChange < -15):
        print("TOO NEGATIVE. RESTART")
        file.write("TOO NEGATIVE. RESTART")
        return 1

    return 0

def checkExitCondition(currency):
    currentBalance = getBalance(currency)

    global initialBalance
    percentChange = calcPercentChange(initialBalance, currentBalance)

    if(percentChange >= MAX_PERCENT_CHANGE):
        return 1

    if(percentChanges <= -1 * MAX_PERCENT_CHANGE):
        return 1

    return 0

def main():
    file.write("\n")
    file.write('------------------------------------------------------------------------------------' + "\n")


    #pickCrypto()
    binStepSize()
    endTime = int(time.time() * 1000)
    startTime = endTime - 3600000
    #updateCrypto('1m', startTime, endTime)
    #priceChecker()

    x=0
    t=0

    currentCurrency = ''

    priceSold = 0.0
    global initialBalance
    initialBalance = getBalance('BTC')
    for key, value in priceSymbols.items():
        getVolume('3m', startTime, endTime, value)
    '''
    binStepSize()
    while(x < MAX_CYCLES and EXIT == 0):

        endTime = int(time.time() * 1000) - 3600000
        startTime = endTime - 3600000*2
        updateCrypto('3m', startTime, endTime)
        oldCurrency = currentCurrency
        currentCurrency = priceChecker()
        if(oldCurrency != currentCurrency and oldCurrency != ''):
            sellBin(oldCurrency)
        if(oldCurrency != currentCurrency):
            buyBin(currentCurrency)
        global RESTART
        global RESTART_TN
        #while statement is more flexible way to wait for a period of time or a restart
        # restart could be caused by a met failure condition or a met sustained one
        while(t < MAX_TIME_CYCLE and RESTART == 0 and RESTART_TN == 0):
            time.sleep(1)
            if(t % 300 == 0 and t != 0):
                RESTART = checkFailureCondition(currentCurrency)
            RESTART_TN = checkTooNegative(currentCurrency)
            t+=1
        t=0

        priceSold = getbinanceprice(currentCurrency)
        cumulativePercentChange = calcPercentChange(priceBought, priceSold)

        print("FINAL percent change over the life of owning this crypto " + str(cumulativePercentChange))
        file.write("FINAL percent change over the life of owning this crypto " + str(cumulativePercentChange))

        checkExitCondition(currentCurrency)
        x+=1

    sellBin(currentCurrency)


    file.write('---------------------------||||||||||||||||----------------------------------------' + "\n")
    file.write("\n" + "\n" + "\n")
    '''

if __name__ == "__main__":
    main()