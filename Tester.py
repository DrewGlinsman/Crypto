# Copyright (c) 2018 A&D
# Small tester to measure the effectiveness of the CryptoTrainer
import sys
import time
import os
import pickle
import pathlib
from AutoTrader import getbinanceprice
from CryptoEvaluator import PARAMETERS


#dictionary that contains all the symbols for the binance API calls
priceSymbols = {'bitcoin': 'BTCUSDT', 'ripple': "XRPBTC",
                'ethereum': 'ETHBTC', 'BCC': 'BCCBTC',
                'LTC': 'LTCBTC', 'Dash': 'DASHBTC',
                'Monero': 'XMRBTC', 'Qtum': 'QTUMBTC', 'ETC': 'ETCBTC',
                'Zcash': 'ZECBTC', 'ADA': 'ADABTC', 'ADX': 'ADXBTC', 'AION' : 'AIONBTC', 'AMB': 'AMBBTC', 'APPC': 'APPCBTC', 'ARK': 'ARKBTC', 'ARN': 'ARNBTC', 'AST': 'ASTBTC', 'BAT': 'BATBTC', 'BCD': 'BCDBTC', 'BCPT': 'BCPTBTC', 'BNB': 'BNBBTC', 'BNT': 'BNTBTC', 'BQX': 'BQXBTC', 'BRD': 'BRDBTC', 'BTS': 'BTSBTC', 'CDT': 'CDTBTC', 'CMT': 'CMTBTC', 'CND': 'CNDBTC', 'CTR':'CTRBTC', 'DGD': 'DGDBTC', 'DLT': 'DLTBTC', 'DNT': 'DNTBTC', 'EDO': 'EDOBTC', 'ELF': 'ELFBTC', 'ENG': 'ENGBTC', 'ENJ': 'ENJBTC', 'EOS': 'EOSBTC', 'EVX': 'EVXBTC', 'FUEL': 'FUELBTC', 'FUN': 'FUNBTC', 'GAS': 'GASBTC', 'GTO': 'GTOBTC', 'GVT': 'GVTBTC', 'GXS': 'GXSBTC', 'HSR': 'HSRBTC', 'ICN': 'ICNBTC', 'ICX': 'ICXBTC', 'IOTA': "IOTABTC", 'KMD': 'KMDBTC', 'KNC': 'KNCBTC', 'LEND': 'LENDBTC', 'LINK':'LINKBTC', 'LRC':'LRCBTC', 'LSK':'LSKBTC', 'LUN': 'LUNBTC', 'MANA': 'MANABTC', 'MCO': 'MCOBTC', 'MDA': 'MDABTC', 'MOD': 'MODBTC', 'MTH': 'MTHBTC', 'MTL': 'MTLBTC', 'NAV': 'NAVBTC', 'NEBL': 'NEBLBTC', 'NEO': 'NEOBTC', 'NULS': 'NULSBTC', 'OAX': 'OAXBTC', 'OMG': 'OMGBTC', 'OST': 'OSTBTC', 'POE': 'POEBTC', 'POWR': 'POWRBTC', 'PPT': 'PPTBTC', 'QSP': 'QSPBTC', 'RCN': 'RCNBTC', 'RDN': 'RDNBTC', 'REQ': 'REQBTC', 'SALT': 'SALTBTC', 'SNGLS': 'SNGLSBTC', 'SNM': 'SNMBTC', 'SNT': 'SNTBTC', 'STORJ': 'STORJBTC', 'STRAT': 'STRATBTC', 'SUB': 'SUBBTC', 'TNB': 'TNBBTC', 'TNT': 'TNTBTC', 'TRIG': 'TRIGBTC', 'TRX': 'TRXBTC', 'VEN': 'VENBTC', 'VIB': 'VIBBTC', 'VIBE': 'VIBEBTC', 'WABI': 'WABIBTC', 'WAVES': 'WAVESBTC', 'WINGS': 'WINGSBTC', 'WTC': 'WTCBTC', 'XVG': 'XVGBTC', 'XZC': 'XZCBTC', 'YOYO': 'YOYOBTC', 'ZRX': 'ZRXBTC'}
basesource = r'wss://stream.binance.com:9443'

#param file name + path
paramPaths = r'C:\Users\katso\Documents\GitHub\Crypto'
#makes the directorys in the path variable if they do not exist
pathlib.Path(paramPaths).mkdir(parents=True, exist_ok=True)

paramCompletePath = os.path.join(paramPaths, "param.pickle")

#open a file for appending (a). + creates file if does not exist
file = open(paramCompletePath, "w+")


#list of colors that can be copied into the fivethirtyeightfile
colors = ['008fd5', 'fc4f30', 'e5ae38', '6d904f', '8b8b8b', '810f7c', 'f2d4b6', 'f2ae1b', 'f4bbc2', '1209e0', 'b0dlc5', 'dd1d36', '55b4d4', 'ff8f40', 'd35058', '252a8b', '623b19', 'b8962e', 'ff66be', '35679a', '7fffd4', '458b74', '8a2be2', 'ff4040', '8b2323', 'ffd39b', '98f5ff', '53868b', '7fff00', '458b00', 'd2691e', 'ff7256', '6495ed', 'fff8dc', '00ffff', '008b8b', 'ffb90f', '006400', 'caff70', 'ff8c00', 'cd6600', '9932cc', 'bf3eff', '8fbc8f', 'c1ffc1', '9bcd9b', '97ffff', '00ced1', '9400d3', 'ff1493', '8b0a50', '00bfff', '1e90fff', 'b22222', 'ff3030', '228b22', 'ffd700', 'adff2f', 'ff69b4', 'ff6a6a', '7cfc00', 'bfefff', 'ee9572', '20b2aa', 'ff00ff', '66cdaa', '0000cd', 'e066ff', '00fa9a', '191970', 'b3ee3a', 'ff4500', 'ff83fa', 'bbffff', 'ff0000', '4169e1', '54ff9f', '87ceeb', 'a0522d', '836fff', '00ff7f', '008b45', '63b8ff', 'd2b48c', 'ffe1ff', 'ff6347', '8b3626', '00f5ff', '00868b', 'ee82ee', 'ff3e96', 'f5deb3', 'd02090', 'ffff00', '9acd32', '00c5cd', 'ff7256', '00cdcd', 'eead0e', '6e8b3d', 'ee7800', 'b23aee', '483d8b', '00b2ee', 'ee2c2c', 'ffc125', '00cd00', 'ee6aa7', 'ee6363', 'f08080', 'eedd82', 'ffb6c1', '87cefa', 'b03060', '3cb371', '191970', 'c0ff3e', 'db7093', '98fb98', 'ff82ab', 'cdaf95', 'ffbbff', 'b0e0e6' ]
def main():
    time.sleep(1)
    testWriteParamPickle()
    testReadParamPickle()

    print(len(priceSymbols))
    print(len(colors))

#reads pickle from a file
def testReadParamPickle():
    logPaths = r'C:\Users\katso\Documents\GitHub\Crypto\\'
    pickle_in = open(logPaths + '\\' + "param.pkl", "rb")
    testDict = pickle.load(pickle_in)

    print(testDict)


#write pickle to a file
def testWriteParamPickle():
    testDict = PARAMETERS
    logPaths = r'C:\Users\katso\Documents\GitHub\Crypto\\'
    pickle_out = open(logPaths + '\\' + "param.pkl", "wb")
    pickle.dump(testDict, pickle_out)
    pickle_out.close()

#gets the minimum $$ amounts that still get the accepted level of percentage lost to overbuying and underselling
# levelToAccess is a parameter that determines how many 'levels' of the bids/asks you get from the api 5,10,20 only
def testCalcMinBidandAsk(acceptedLossPercentage,levelsToAccess):
    prices = {}
    minBid = 0.0
    minAsk = 0.0
    global basesource

    for key, currencyname in priceSymbols.items():
        source = basesource + '/ws/' + str(currencyname) + '@depth' + str(levelsToAccess)
        # try to open with urllib (if source is http, ftp, or file URL)
        try:
            print(source)
        except (IOError, OSError):
            print('error')
            pass


def testCryptoTrainer():
    for line in sys.stdin:
        print("LINEBEGIN" + line + "DONEEND")

def testCalcPercentChange():
    startVal = 1.0
    endVal = 4.0
    result = (((float(endVal) - float(startVal)) / float(startVal)) * 100)

    print(str(result))

if __name__ == "__main__":
    main()












