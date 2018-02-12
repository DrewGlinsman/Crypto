
import time
import requests
import os
import datetime

#dictionary that contains all the symbols for the binance API calls
priceSymbols = {'bitcoin': 'BTCUSDT', 'ripple': "XRPBTC",
                'ethereum': 'ETHBTC', 'BCC': 'BCCBTC',
                'LTC': 'LTCBTC', 'Dash': 'DASHBTC',
                'Monero': 'XMRBTC', 'Qtum': 'QTUMBTC', 'ETC': 'ETCBTC',
                'Zcash': 'ZECBTC', 'ADA': 'ADABTC', 'ADX': 'ADXBTC', 'AION' : 'AIONBTC', 'AMB': 'AMBBTC', 'APPC': 'APPCBTC', 'ARK': 'ARKBTC', 'ARN': 'ARNBTC', 'AST': 'ASTBTC', 'BAT': 'BATBTC', 'BCD': 'BCDBTC', 'BCPT': 'BCPTBTC', 'BNB': 'BNBBTC', 'BNT': 'BNTBTC', 'BQX': 'BQXBTC', 'BRD': 'BRDBTC', 'BTS': 'BTSBTC', 'CDT': 'CDTBTC', 'CMT': 'CMTBTC', 'CND': 'CNDBTC', 'CTR':'CTRBTC', 'DGD': 'DGDBTC', 'DLT': 'DLTBTC', 'DNT': 'DNTBTC', 'EDO': 'EDOBTC', 'ELF': 'ELFBTC', 'ENG': 'ENGBTC', 'ENJ': 'ENJBTC', 'EOS': 'EOSBTC', 'EVX': 'EVXBTC', 'FUEL': 'FUELBTC', 'FUN': 'FUNBTC', 'GAS': 'GASBTC', 'GTO': 'GTOBTC', 'GVT': 'GVTBTC', 'GXS': 'GXSBTC', 'HSR': 'HSRBTC', 'ICN': 'ICNBTC', 'ICX': 'ICXBTC', 'IOTA': "IOTABTC", 'KMD': 'KMDBTC', 'KNC': 'KNCBTC', 'LEND': 'LENDBTC', 'LINK':'LINKBTC', 'LRC':'LRCBTC', 'LSK':'LSKBTC', 'LUN': 'LUNBTC', 'MANA': 'MANABTC', 'MCO': 'MCOBTC', 'MDA': 'MDABTC', 'MOD': 'MODBTC', 'MTH': 'MTHBTC', 'MTL': 'MTLBTC', 'NAV': 'NAVBTC', 'NEBL': 'NEBLBTC', 'NEO': 'NEOBTC', 'NULS': 'NULSBTC', 'OAX': 'OAXBTC', 'OMG': 'OMGBTC', 'OST': 'OSTBTC', 'POE': 'POEBTC', 'POWR': 'POWRBTC', 'PPT': 'PPTBTC', 'QSP': 'QSPBTC', 'RCN': 'RCNBTC', 'RDN': 'RDNBTC', 'REQ': 'REQBTC', 'SALT': 'SALTBTC', 'SNGLS': 'SNGLSBTC', 'SNM': 'SNMBTC', 'SNT': 'SNTBTC', 'STORJ': 'STORJBTC', 'STRAT': 'STRATBTC', 'SUB': 'SUBBTC', 'TNB': 'TNBBTC', 'TNT': 'TNTBTC', 'TRIG': 'TRIGBTC', 'TRX': 'TRXBTC', 'VEN': 'VENBTC', 'VIB': 'VIBBTC', 'VIBE': 'VIBEBTC', 'WABI': 'WABIBTC', 'WAVES': 'WAVESBTC', 'WINGS': 'WINGSBTC', 'WTC': 'WTCBTC', 'XVG': 'XVGBTC', 'XZC': 'XZCBTC', 'YOYO': 'YOYOBTC', 'ZRX': 'ZRXBTC'}
#path to save the different text files in
cryptoPaths = r'C:\Users\DrewG\Documents\GitHub\Crypto\BackTestData'

#one day in ms
ONE_DAY = 86400000
ONE_THIRD_DAY = 28800000
count = 1

def getData(numDays):

  #code for writing the values into three text files for each crypto: an open price, close price, and volume file.
  for key, value in priceSymbols.items():
        #creating the file path lengths and opening them
        openPriceCryptoPath = os.path.join(cryptoPaths, value + "OpenPrice" + ".txt")
        closePriceCryptoPath = os.path.join(cryptoPaths, value + "ClosePrice" + ".txt")
        volumeCryptoPath = os.path.join(cryptoPaths, value + "Volume" + ".txt")
        oprice = open(openPriceCryptoPath, "a+")
        cprice = open(closePriceCryptoPath, "a+")
        volume = open(volumeCryptoPath, "a+")

        #while loop with a counter to make sure that the start and endtime stay one day apart but go backwards in time, numdays amount of days
        timeBackwards = 0
        while(timeBackwards < ONE_DAY*numDays):
            endTime = requests.get("https://api.binance.com/api/v1/time")
            endTime = endTime.json()
            endTime = endTime['serverTime'] - timeBackwards
            startTime = endTime - ONE_THIRD_DAY
            parameters = {'symbol': value, 'startTime': startTime, 'endTime': endTime, 'interval': '1m'}
            data = requests.get("https://api.binance.com/api/v1/klines", params=parameters)
            data = data.json()
            for i in data:
                oprice.write("{},".format(i[1]))
                cprice.write("{},".format(i[4]))
                volume.write("{},".format(i[5]))
            timeBackwards += ONE_THIRD_DAY

  #closing all the files once we're done
  oprice.close()
  cprice.close()
  volume.close()

def main():
    #creating the filepath for the file with the timestamp in it and reading it into the timestamp and converting it to int
    timefilePath = os.path.join(cryptoPaths, "timestamp.txt")
    timefile = open(timefilePath, "r")
    timestamp = int(timefile.readline())
    timefile.close()

    #after reading in timestamp convert to a date time object and then strip it down to only hours minutes and seconds
    timestamp = datetime.datetime.fromtimestamp(timestamp/1000.0).time()
    timestamp = int(timestamp.strftime("%H%M%S"))

    print("{}".format(timestamp))

    #infinite loop to keep the program running where it will get the data at
    while(0<1):

        #get the current time stamp and convert it into a time with only hours minutes and seconds
        currentTime = int(time.time()*1000)
        currentTime = datetime.datetime.fromtimestamp(currentTime/1000.0)
        currentTime = int(currentTime.strftime("%H%M%S"))

        if(currentTime != timestamp):
            print("Current Time: {} Timestamp to get to: {}".format(currentTime, timestamp))
            time.sleep(1)
        else:
            print("Getting data")
            getData(1)
 

if __name__ == "__main__":
    main()