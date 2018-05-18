# Copyright (c) 2018 A&D
#facilitates all buy/sell requests by the different files


import hmac
import hashlib

from math import floor
from urllib.parse import urlencode
from PrivateData import secret_key, api_key
from Generics import PARAMETERS
from time import time
from requests import get

#decimal precision allowed for trading each crypto
stepsizes = {}


#get the binance step sizes of each crypto (the step size is the minimum significant digits allowed by binance for crypto to be traded in)
def binStepSize():
    #getting the dictionary of a lot of aggregate data for all symbols
    stepsizeinfo = get("https://api.binance.com/api/v1/exchangeInfo")
    bigdata = stepsizeinfo.json()["symbols"]

    #iterating through the dictionary and adding just the stepsizes into our own dictionary
    for i in bigdata:
        symbol = i["symbol"]
        stepsize = i["filters"][1]["stepSize"]
        temp = {symbol: stepsize}
        stepsizes.update(temp)

#buy the specified crypto currency
#returns the new currencytotrade and pricebought in case it is used
def buyBin(symbol, stepsize, currencyToTrade, percenttospend=PARAMETERS['PERCENT_TO_SPEND'], percentquantitytospend=PARAMETERS['PERCENT_QUANTITY_TO_SPEND']):

    timestamp = int(time.time() * 1000)
    balance = getBalance('BTC')

    #multiply balance by constant ratio of how much we want to spend
    # and then convert quantity from BTC price to amount of coin
    balancetospend = float(balance) * percenttospend
    ratio = getbinanceprice(symbol)

    #store the price the crypto was a bought at for cumulative percent change calculations
    priceBought = ratio

    #mark item as the current crypto being traded and save the buy price at for failure condition
    entry = {symbol:{'buyPrice': ratio, 'timestamp': timestamp}}
    currencyToTrade.clear()
    currencyToTrade.update(entry)
    quantity = balancetospend / float(ratio) * float(percentquantitytospend)

    # making the quantity to buy
    quantity = float(quantity)

    # based on the stepsize of the currency round the quantity to that amount
    if (float(stepsize) == float(1)):
        quantity = int(quantity)
    if (float(stepsize) == 0.1):
        quantity = floor(quantity * 10) / 10
    if (float(stepsize) == 0.01):
        quantity = floor(quantity * 100) / 100
    if (float(stepsize) == 0.001):
        quantity = floor(quantity * 1000) / 1000

    #building the query string for buying(signed)
    headers = {'X-MBX-APIKEY': api_key}
    buyParameters = {'symbol': symbol, 'side': 'buy', 'type': 'market', 'timestamp': timestamp, 'quantity': quantity}
    query = urlencode(sorted(buyParameters.items()))
    signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    query += "&signature=" + signature


   # testBuy = requests.post("https://api.binance.com/api/v3/order?" + query, headers=headers)

    return currencyToTrade, priceBought

#sell the specified crypto
def sellBin(symbol, stepsize):
    #current time in ms
    timestamp = int(time.time() * 1000) - 1000

    #building the request query url plus other parameters(signed)
    headers = {'X-MBX-APIKEY': api_key}
    infoParameter = {'timestamp': timestamp}
    query = urlencode(sorted(infoParameter.items()))
    signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    query += "&signature=" + signature

    #getting the account info
    accountInfo = get("https://api.binance.com/api/v3/account?" + query, headers=headers)


    #getting rid of the 'BTC' part of the crypto asset name
    if(len(symbol) == 6):
        asset = symbol[0:3]

    if(len(symbol) == 7):
        asset = symbol[0:4]

    if(len(symbol) == 8):
        asset = symbol[0:5]


    #iterating through the account info to find the balance of the coin we're selling
    for i in accountInfo.json()["balances"]:
        if (i["asset"] == asset):
            balance = i["free"]

    #making the quantity to sell
    quantity = float(balance)

    #based on the stepsize of the currency round the quantity to that amount
    if (float(stepsize) == float(1)):
        quantity = int(quantity)
    if (float(stepsize) == 0.1):
        quantity = floor(quantity*10)/10
    if (float(stepsize) == 0.01):
        quantity = floor(quantity*100)/100
    if (float(stepsize) == 0.001):
        quantity = floor(quantity*1000)/1000

    #building the sell query string
    sellParameters = {'symbol': symbol, 'side': 'sell', 'type': 'market', 'timestamp': timestamp, 'quantity': quantity}
    query = urlencode(sorted(sellParameters.items()))
    signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    query += "&signature=" + signature

    #actually selling
   # testSell = requests.post("https://api.binance.com/api/v3/order?" + query, headers=headers)

#get the balance in bitcoins
def getBalance(symbol):
    timestamp = int(time.time() * 1000)
    # building the request query url plus other parameters(signed)
    headers = {'X-MBX-APIKEY': api_key}
    infoParameter = {'timestamp': timestamp}
    query = urlencode(sorted(infoParameter.items()))
    signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    query += "&signature=" + signature

    # requesting account info to get the balance
    accountInfo = get("https://api.binance.com/api/v3/account?" + query, headers=headers)
    accountInfo = accountInfo.json()["balances"]

    balance = 0

    for val in accountInfo:
        if(val["asset"] == symbol):
            balance = val["free"]

    return balance


#get the binance price of the specified currency
def getbinanceprice(currency):
    #getting the aggregate trade data and finding one price to return
    parameters = {'symbol': currency}
    binData = get("https://api.binance.com/api/v3/ticker/price", params= parameters)
    binData = binData.json()
    binPrice = binData['price']
    return binPrice