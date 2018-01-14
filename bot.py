import requests
import hmac
import hashlib
import time
#from xcoin_api_client import XCoinAPI

try:
    from urlib import urlencode

except ImportError:
    from urllib.parse import urlencode

bithumb_secret_key = 'da6d04780679d61b3f68e4c3cee20e2f'

bithumb_connect_key = '2d076dbe6984596f446d0a761cdf88a8'

# FIELDS
priceSymbols = {'bitcoin': {'bin': 'BTCUSDT', 'bthumb': 'BTC'}, 'ripple': {'bin': "XRPBTC", "bthumb": 'XRP'},
                'ethereum': {'bin': 'ETHBTC', 'bthumb': 'ETH'}, 'BCC': {'bin': 'BCCBTC', 'bthumb': 'BCH'},
                'LTC': {'bin': 'LTCBTC', 'bthumb': 'LTC'}, 'Dash': {'bin': 'DASHBTC', 'bthumb': 'DASH'},
                'Monero': {'bin': 'XMRBTC', 'bthumb': 'XMR'}, 'Qtum': {'bin': 'QTUMBTC', 'bthumb': 'QTUM'}, 'ETC': {'bin': 'ETCBTC', 'bthumb': 'ETC'},
                'Zcash': {'bin': 'ZECBTC', 'bthumb': 'ZEC'}}

api_key = '7WzDy6Hw7HBozQiR1UEpWMgdpzAKQ3ZUSBX6QMra723KO4ot6iAQykbqtqM4hL7Y'

secret_key = 'cHFo1FUc4zRgydNpTDip51S2s12yd7SKe65LS96AgrUxfm8B5Q7HgQcJghitSlNo'

percent_to_spend = .01  # CHANGE TO 0.5

minTransactionAmount = {'BTC': 0.003, 'ETH': 0.01, 'Dash': 0.01, 'LTC': 0.01, 'ETC': 0.01, 'XRP': 21, 'BCH': 0.005,
                        'XMR': 0.1, 'ZEC': 0.01, 'QTUM': 0.1}

stepsizes = {}

currencyToTrade = {}

class bot():

    #def _init_(self):
        #super(bot, self)._init_(self, bithumb_connect_key, bithumb_secret_key)

    def getbinanceprice(self, currency):
        startTime = int(time.time()*1000) - 3600000
        endTime = int(time.time()*1000)
        parameter = {'symbol': currency, 'startTime': startTime, 'endTime': endTime}
        binData = requests.get("https://api.binance.com/api/v1/aggTrades", params=parameter)
        binPrice = binData.json()[1]['p']
        return binPrice

    def getbthumbprice(self, currency):
        btCURR = requests.get("https://api.bithumb.com/public/ticker/" + currency)
        btCURRprice = btCURR.json()['data']['sell_price']
        return btCURRprice

    def wontoUSD(self):
        erData = requests.get("https://api.fixer.io/latest?base=USD&symbols=KRW")
        exchangeRate = erData.json()["rates"]["KRW"]
        return exchangeRate

    def findpriceratio(self, bincurrency, bthumbcurrency):
        binPriceRatio = self.getbinanceprice(bincurrency)
        if(bincurrency == 'BTCUSDT'):
            binPrice = binPriceRatio
        else:
            binPrice = float(self.getbinanceprice('BTCUSDT')) * float(binPriceRatio)
        bthumbPrice = self.getbthumbprice(bthumbcurrency)
        bthumbPrice = float(bthumbPrice)/self.wontoUSD()
        ratio = bthumbPrice / float(binPrice)
        return ratio

    def decisioneminem(self, dict, maxRatio, minRatio):
        maxRatio = 0
        minRatio = 1000000
        for key, value in priceSymbols.items():
            print(key)
            print(value)
            currRatio = self.findpriceratio(value['bin'], value['bthumb'])
            if(maxRatio < currRatio):
                print('new max ratio = ' + str(currRatio))
                maxRatio = currRatio
                maxSymbol = {'maxSymbol': value}
                dict.update(maxSymbol)
            if(minRatio > currRatio):
                print('new min ratio = ' + str(currRatio))
                minRatio = currRatio
                minSymbol = {'minSymbol': value}
                dict.update(minSymbol)

        if(maxRatio >= minRatio + .03):
            print("I would buy here")
        print("final max ratio = " + str(maxRatio) + " final min ratio = " + str(minRatio))
        print("I would recommend to buy " + maxSymbol['maxSymbol']['bthumb'] + " to turn into " + minSymbol['minSymbol']['bthumb'] + " on bithumb")

    def buyBin(self, symbol, asset, address, addressTag=""):

        timestamp = int(time.time() * 1000)

        headers = {'X-MBX-APIKEY': api_key}
        infoParameter = {'timestamp': timestamp}
        query = urlencode(sorted(infoParameter.items()))
        signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
        query += "&signature=" + signature

        accountInfo = requests.get("https://api.binance.com/api/v3/account?" + query, headers=headers)
        balance = accountInfo.json()["balances"][0]["free"]
        print("Balance: " + balance)
        balancetospend = float(balance) * percent_to_spend
        ratio = self.getbinanceprice(symbol)
        quantity = balancetospend / float(ratio) * .9
        quantity = round(quantity, 3)
        print(quantity)

        '''
        print(asset)
        addressParameters = {'currency': asset}

        address = self.xcoinApiCall("/info/balance", addressParameters)
        print(address.text)
        
        '''

        buyParameters = {'symbol': symbol, 'side': 'buy', 'type': 'market', 'timestamp': timestamp, 'quantity': quantity}
        #sendParameters = {'asset': asset, 'address': address, 'amount': quantity, 'recvWindow': 5000, 'timestamp': timestamp, 'addressTag': addressTag}

        query = urlencode(sorted(buyParameters.items()))
        signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
        query += "&signature=" + signature

        testBuy = requests.post("https://api.binance.com/api/v3/order?" + query, headers=headers)
        print(testBuy.text)

        #query = urlencode(sorted(sendParameters.items()))
        #signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
        #query += "&signature=" + signature
        #queryURL = 'https://api.binance.com/wapi/v3/withdraw.html?' + query
        #testSend = requests.post(queryURL, headers=headers)

    def sellBin(self, symbol, asset, address, addressTag=""):
        timestamp = int(time.time() * 1000)

        headers = {'X-MBX-APIKEY': api_key}
        infoParameter = {'timestamp': timestamp}
        query = urlencode(sorted(infoParameter.items()))
        signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
        query += "&signature=" + signature

        accountInfo = requests.get("https://api.binance.com/api/v3/account?" + query, headers=headers)
        print (accountInfo.text)

        for i in accountInfo.json()["balances"]:
            if(i["asset"] == asset):
                balance = i["free"]

        stepsize = stepsizes[symbol]

        print(stepsize)
        print("Balance: " + balance)

        quantity = float(balance)
        if (float(stepsize) == float(1)):
            quantity = int(quantity)
        if (float(stepsize) == 0.1):
            quantity = round(quantity,1)
        if(float(stepsize) == 0.01):
            quantity = round(quantity,2)
        if(float(stepsize) == 0.001):
            quantity = round(quantity,3)

        print(quantity)

        sellParameters = {'symbol': symbol, 'side': 'sell', 'type': 'market', 'timestamp': timestamp, 'quantity': quantity}

        query = urlencode(sorted(sellParameters.items()))
        signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
        query += "&signature=" + signature

        testSell = requests.post("https://api.binance.com/api/v3/order?" + query, headers=headers)
        print(testSell.text)

    def binStepSize(self):
        stepsizeinfo = requests.get("https://api.binance.com/api/v1/exchangeInfo")
        bigdata = stepsizeinfo.json()["symbols"]
        for i in bigdata:
            symbol = i["symbol"]
            stepsize = i["filters"][1]["stepSize"]
            temp = {symbol: stepsize}
            stepsizes.update(temp)


bot = bot()
bot.binStepSize()
bot.decisioneminem(currencyToTrade, 0.0, 0.0)
#print(currencyToTrade)
#buyBin(currencyToTrade['maxSymbol']['bin'], currencyToTrade['maxSymbol']['bthumb'], '', '')
bot.buyBin('XRPBTC', 'XRP', "", "")
