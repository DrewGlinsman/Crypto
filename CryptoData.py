<<<<<<< HEAD
=======
# Copyright (c) 2018 A&D
# Sets up text files to hold price and volume data over a specified interval
# for the different cryptocurrency on Binance




import requests
import hmac
import hashlib
>>>>>>> 1be2caf00c832f2fdfa50402d058f3b05601f7ab
import time
import requests
import os


#dictionary that contains all the symbols for the binance API calls
priceSymbols = {'bitcoin': 'BTCUSDT', 'ripple': "XRPBTC",
                'ethereum': 'ETHBTC', 'BCC': 'BCCBTC',
                'LTC': 'LTCBTC', 'Dash': 'DASHBTC',
                'Monero': 'XMRBTC', 'Qtum': 'QTUMBTC', 'ETC': 'ETCBTC',
                'Zcash': 'ZECBTC', 'ADA': 'ADABTC', 'ADX': 'ADXBTC', 'AION' : 'AIONBTC', 'AMB': 'AMBBTC', 'APPC': 'APPCBTC', 'ARK': 'ARKBTC', 'ARN': 'ARNBTC', 'AST': 'ASTBTC', 'BAT': 'BATBTC', 'BCD': 'BCDBTC', 'BCPT': 'BCPTBTC', 'BNB': 'BNBBTC', 'BNT': 'BNTBTC', 'BQX': 'BQXBTC', 'BRD': 'BRDBTC', 'BTS': 'BTSBTC', 'CDT': 'CDTBTC', 'CMT': 'CMTBTC', 'CND': 'CNDBTC', 'CTR':'CTRBTC', 'DGD': 'DGDBTC', 'DLT': 'DLTBTC', 'DNT': 'DNTBTC', 'EDO': 'EDOBTC', 'ELF': 'ELFBTC', 'ENG': 'ENGBTC', 'ENJ': 'ENJBTC', 'EOS': 'EOSBTC', 'EVX': 'EVXBTC', 'FUEL': 'FUELBTC', 'FUN': 'FUNBTC', 'GAS': 'GASBTC', 'GTO': 'GTOBTC', 'GVT': 'GVTBTC', 'GXS': 'GXSBTC', 'HSR': 'HSRBTC', 'ICN': 'ICNBTC', 'ICX': 'ICXBTC', 'IOTA': "IOTABTC", 'KMD': 'KMDBTC', 'KNC': 'KNCBTC', 'LEND': 'LENDBTC', 'LINK':'LINKBTC', 'LRC':'LRCBTC', 'LSK':'LSKBTC', 'LUN': 'LUNBTC', 'MANA': 'MANABTC', 'MCO': 'MCOBTC', 'MDA': 'MDABTC', 'MOD': 'MODBTC', 'MTH': 'MTHBTC', 'MTL': 'MTLBTC', 'NAV': 'NAVBTC', 'NEBL': 'NEBLBTC', 'NEO': 'NEOBTC', 'NULS': 'NULSBTC', 'OAX': 'OAXBTC', 'OMG': 'OMGBTC', 'OST': 'OSTBTC', 'POE': 'POEBTC', 'POWR': 'POWRBTC', 'PPT': 'PPTBTC', 'QSP': 'QSPBTC', 'RCN': 'RCNBTC', 'RDN': 'RDNBTC', 'REQ': 'REQBTC', 'SALT': 'SALTBTC', 'SNGLS': 'SNGLSBTC', 'SNM': 'SNMBTC', 'SNT': 'SNTBTC', 'STORJ': 'STORJBTC', 'STRAT': 'STRATBTC', 'SUB': 'SUBBTC', 'TNB': 'TNBBTC', 'TNT': 'TNTBTC', 'TRIG': 'TRIGBTC', 'TRX': 'TRXBTC', 'VEN': 'VENBTC', 'VIB': 'VIBBTC', 'VIBE': 'VIBEBTC', 'WABI': 'WABIBTC', 'WAVES': 'WAVESBTC', 'WINGS': 'WINGSBTC', 'WTC': 'WTCBTC', 'XVG': 'XVGBTC', 'XZC': 'XZCBTC', 'YOYO': 'YOYOBTC', 'ZRX': 'ZRXBTC'}

#dictionarys to store the data after its read in from a text file.
cryptoOpenPriceData = {}
cryptoClosePriceData = {}
cryptoVolumeData = {}

#path to save the different text files in
cryptoPaths = r'C:\Users\DrewG\Documents\GitHub\Crypto\CryptoData'

#one day in ms
ONE_DAY = 86400000

def getData(numDays):

  #code for writing the values into three text files for each crypto: an open price, close price, and volume file.
  for key, value in priceSymbols.items():
        #creating the file path lengths and opening them
        openPriceCryptoPath = os.path.join(cryptoPaths, value + "OpenPrice" + ".txt")
        closePriceCryptoPath = os.path.join(cryptoPaths, value + "ClosePrice" + ".txt")
        volumeCryptoPath = os.path.join(cryptoPaths, value + "Volume" + ".txt")
        oprice = open(openPriceCryptoPath, "w")
        cprice = open(closePriceCryptoPath, "w")
        volume = open(volumeCryptoPath, "w")

        #while loop with a counter to make sure that the start and endtime stay one day apart but go backwards in time, numdays amount of days
        timeBackwards = 0
        while(timeBackwards <= ONE_DAY*numDays):
            endTime = int(time.time()*1000) - timeBackwards
            startTime = endTime - ONE_DAY
            parameters = {'symbol': value, 'startTime': startTime, 'endTime': endTime, 'interval': '1m'}
            data = requests.get("https://api.binance.com/api/v1/klines", params=parameters)
            data = data.json()
            for i in data:
                oprice.write("{},".format(i[1]))
                cprice.write("{},".format(i[4]))
                volume.write("{},".format(i[5]))
            timeBackwards += ONE_DAY

  for key, value in priceSymbols.items():

      #creating the path lengths and opening the files with read permissions
      openPriceCryptoPath = os.path.join(cryptoPaths, value + "OpenPrice" + ".txt")
      closePriceCryptoPath = os.path.join(cryptoPaths, value + "ClosePrice" + ".txt")
      volumeCryptoPath = os.path.join(cryptoPaths, value + "Volume" + ".txt")
      oprice = open(openPriceCryptoPath, "r")
      cprice = open(closePriceCryptoPath, "r")
      volume = open(volumeCryptoPath, "r")

      #reading through each of the files
      odata = oprice.readlines()
      cdata = cprice.readlines()
      vol = volume.readlines()

      #iterating through each file and adding the correct data to each dictionary
      for line in odata:
        words = line.split(",")
        temp = {value: words}
        cryptoOpenPriceData.update(temp)
      for line in cdata:
          words = line.split(",")
          temp = {value: words}
          cryptoClosePriceData.update(temp)
      for line in vol:
          words = line.split(",")
          temp = {value: words}
          cryptoVolumeData.update(temp)
          print("Volume: {}".format(words))

  #closing all the files once we're done
  oprice.close()
  cprice.close()
  volume.close()

  print("Open Price Dict: {}".format(cryptoOpenPriceData))
  print("Close Price DIct: {}".format(cryptoClosePriceData))
  print("Volume Dict: {}". format(cryptoVolumeData))

def main():
    getData(7)

if __name__ == "__main__":
    main()