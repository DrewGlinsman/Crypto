
import time
import requests
import os

#ADDS TO THE LIST IN REVERSE CHRONOLOGICAL ORDER SO WHENEVER ITERATING THROUGH BACKTESTED DATA USE THE REVERSE FUNCTION

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
COUNT = 7

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
            print("Length of data set: {} coin associated with data set: {} data set: {}".format(len(data), value, data))
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
    timestamp = requests.get("https://api.binance.com/api/v1/time")
    timestamp = timestamp.json()
    #todo after successful run change this code so that it grabs from the text file so timestamp is always the same or maybe put this in a function
    timestamp = timestamp['serverTime']
    print("{}".format(timestamp))
    timestampPath = os.path.join(cryptoPaths, "timestamp.txt")
    timefile = open(timestampPath, "w")
    timefile.write(str(timestamp))
    while(0<1):
        currentTime = int(time.time()*1000)
        if(timestamp != currentTime):
            print("I'm sleeping")
            time.sleep(1)
        else:
            print("Getting data")
            getData(7)

if __name__ == "__main__":
    main()