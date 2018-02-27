# Copyright (c) 2018 A&D
# Auto trading bot that uses parameters sent by CryptoTrainer to test them


import os.path
import sys
import CryptoStatAnalysis

import CryptoStats

from CryptoTrainer import PARAMETERS
from CryptoStats import getOpenPrice, getClosePrice, getVolume

try:
    from urlib import urlencode

except ImportError:
    from urllib.parse import urlencode


#todo make a series of functions used that have random variables in them and random variables left out instead of a simple linear score and simple parameter variation
#todo add function to pull data from text files by day into data structures here
#todo add in a parser for the stdin
#todo add in a print statement to send back the parameters

logPath = r'C:\Users\katso\Documents\GitHub\Crypto\Logs\dlog.txt'
#logPath = r'C:\Users\DrewG\Documents\GitHub\Crypto\Logs\dlog.txt'
file = open(logPath, "a+")


#paramPaths = r'C:\Users\DrewG\Documents\GitHub\Crypto\Logs'
paramPaths = r'C:\Users\katso\Documents\GitHub\Crypto\Logs'

#param file name + path

#todo change to "BEST_PARAMETERS" when actually running
paramCompletePath = os.path.join(paramPaths, "testlog.txt")


#open a file for appending (a). + creates file if does not exist
file = open(paramCompletePath, "a+")


#GLOBAL_VARIABLES

#0 is false, 1 is true
RESTART = 0
RESTART_TN = 0
RESTART_LOW = 0
EXIT = 0

#price each crypto is bought at
priceBought = 0.0


#How much of bitcoin balance to buy to purhcase more of the crypto (should be fixed to account for the fee of buying)
PERCENT_QUANITITY_TO_SPEND = .9

#the name of each crypto as the key and the value is the Binance ticker symbol
priceSymbols = {'bitcoin': 'BTCUSDT', 'ripple': "XRPBTC",
                'ethereum': 'ETHBTC', 'BCC': 'BCCBTC',
                'LTC': 'LTCBTC', 'Dash': 'DASHBTC',
                'Monero': 'XMRBTC', 'Qtum': 'QTUMBTC', 'ETC': 'ETCBTC',
                'Zcash': 'ZECBTC', 'ADA': 'ADABTC', 'ADX': 'ADXBTC', 'AION' : 'AIONBTC', 'AMB': 'AMBBTC', 'APPC': 'APPCBTC', 'ARK': 'ARKBTC', 'ARN': 'ARNBTC', 'AST': 'ASTBTC', 'BAT': 'BATBTC', 'BCD': 'BCDBTC', 'BCPT': 'BCPTBTC', 'BNB': 'BNBBTC', 'BNT': 'BNTBTC', 'BQX': 'BQXBTC', 'BRD': 'BRDBTC', 'BTS': 'BTSBTC', 'CDT': 'CDTBTC', 'CMT': 'CMTBTC', 'CND': 'CNDBTC', 'CTR':'CTRBTC', 'DGD': 'DGDBTC', 'DLT': 'DLTBTC', 'DNT': 'DNTBTC', 'EDO': 'EDOBTC', 'ELF': 'ELFBTC', 'ENG': 'ENGBTC', 'ENJ': 'ENJBTC', 'EOS': 'EOSBTC', 'EVX': 'EVXBTC', 'FUEL': 'FUELBTC', 'FUN': 'FUNBTC', 'GAS': 'GASBTC', 'GTO': 'GTOBTC', 'GVT': 'GVTBTC', 'GXS': 'GXSBTC', 'HSR': 'HSRBTC', 'ICN': 'ICNBTC', 'ICX': 'ICXBTC', 'IOTA': "IOTABTC", 'KMD': 'KMDBTC', 'KNC': 'KNCBTC', 'LEND': 'LENDBTC', 'LINK':'LINKBTC', 'LRC':'LRCBTC', 'LSK':'LSKBTC', 'LUN': 'LUNBTC', 'MANA': 'MANABTC', 'MCO': 'MCOBTC', 'MDA': 'MDABTC', 'MOD': 'MODBTC', 'MTH': 'MTHBTC', 'MTL': 'MTLBTC', 'NAV': 'NAVBTC', 'NEBL': 'NEBLBTC', 'NEO': 'NEOBTC', 'NULS': 'NULSBTC', 'OAX': 'OAXBTC', 'OMG': 'OMGBTC', 'OST': 'OSTBTC', 'POE': 'POEBTC', 'POWR': 'POWRBTC', 'PPT': 'PPTBTC', 'QSP': 'QSPBTC', 'RCN': 'RCNBTC', 'RDN': 'RDNBTC', 'REQ': 'REQBTC', 'SALT': 'SALTBTC', 'SNGLS': 'SNGLSBTC', 'SNM': 'SNMBTC', 'SNT': 'SNTBTC', 'STORJ': 'STORJBTC', 'STRAT': 'STRATBTC', 'SUB': 'SUBBTC', 'TNB': 'TNBBTC', 'TNT': 'TNTBTC', 'TRIG': 'TRIGBTC', 'TRX': 'TRXBTC', 'VEN': 'VENBTC', 'VIB': 'VIBBTC', 'VIBE': 'VIBEBTC', 'WABI': 'WABIBTC', 'WAVES': 'WAVESBTC', 'WINGS': 'WINGSBTC', 'WTC': 'WTCBTC', 'XVG': 'XVGBTC', 'XZC': 'XZCBTC', 'YOYO': 'YOYOBTC', 'ZRX': 'ZRXBTC'}





#percent changes of the prices for each crypto with an interval size over a specified period of time
percentChanges = {'BTCUSDT': [], 'XRPBTC': [],
                'ETHBTC': [], 'BCCBTC': [],
                'LTCBTC': [], 'DASHBTC': [],
                'XMRBTC': [], 'QTUMBTC': [], 'ETCBTC': [],
                'ZECBTC': [], 'ADABTC': [], 'ADXBTC': [], 'AIONBTC' : [], 'AMBBTC': [], 'APPCBTC': [], 'ARKBTC': [], 'ARNBTC': [], 'ASTBTC': [], 'BATBTC': [], 'BCDBTC': [], 'BCPTBTC': [], 'BNBBTC': [], 'BNTBTC': [], 'BQXBTC': [], 'BRDBTC': [], 'BTSBTC': [], 'CDTBTC': [], 'CMTBTC': [], 'CNDBTC': [], 'CTRBTC': [], 'DGDBTC': [], 'DLTBTC': [], 'DNTBTC': [], 'EDOBTC': [], 'ELFBTC': [], 'ENGBTC': [], 'ENJBTC': [], 'EOSBTC': [], 'EVXBTC': [], 'FUELBTC': [], 'FUNBTC': [], 'GASBTC': [], 'GTOBTC': [], 'GVTBTC': [], 'GXSBTC': [], 'HSRBTC': [], 'ICNBTC': [], 'ICXBTC': [], 'IOTABTC': [], 'KMDBTC': [], 'KNCBTC': [], 'LENDBTC': [], 'LINKBTC': [], 'LRCBTC': [], 'LSKBTC': [], 'LUNBTC': [], 'MANABTC': [], 'MCOBTC': [], 'MDABTC': [], 'MODBTC': [], 'MTHBTC': [], 'MTLBTC': [], 'NAVBTC': [], 'NEBLBTC': [], 'NEOBTC': [], 'NULSBTC': [], 'OAXBTC': [], 'OMGBTC': [], 'OSTBTC': [], 'POEBTC': [], 'POWRBTC': [], 'PPTBTC': [], 'QSPBTC': [], 'RCNBTC': [], 'RDNBTC': [], 'REQBTC': [], 'SALTBTC': [], 'SNGLSBTC': [], 'SNMBTC': [], 'SNTBTC': [], 'STORJBTC': [], 'STRATBTC': [], 'SUBBTC': [], 'TNBBTC': [], 'TNTBTC': [], 'TRIGBTC': [], 'TRXBTC': [], 'VENBTC': [], 'VIBBTC': [], 'VIBEBTC': [], 'WABIBTC': [], 'WAVESBTC': [], 'WINGSBTC': [], 'WTCBTC': [], 'XVGBTC': [], 'XZCBTC': [], 'YOYOBTC': [], 'ZRXBTC': []}

#percent changes of the volume for each crypto with an interval size over a specified period of time
volumePercentChanges = {'BTCUSDT': [], 'XRPBTC': [],
                'ETHBTC': [], 'BCCBTC': [],
                'LTCBTC': [], 'DASHBTC': [],
                'XMRBTC': [], 'QTUMBTC': [], 'ETCBTC': [],
                'ZECBTC': [], 'ADABTC': [], 'ADXBTC': [], 'AIONBTC' : [], 'AMBBTC': [], 'APPCBTC': [], 'ARKBTC': [], 'ARNBTC': [], 'ASTBTC': [], 'BATBTC': [], 'BCDBTC': [], 'BCPTBTC': [], 'BNBBTC': [], 'BNTBTC': [], 'BQXBTC': [], 'BRDBTC': [], 'BTSBTC': [], 'CDTBTC': [], 'CMTBTC': [], 'CNDBTC': [], 'CTRBTC': [], 'DGDBTC': [], 'DLTBTC': [], 'DNTBTC': [], 'EDOBTC': [], 'ELFBTC': [], 'ENGBTC': [], 'ENJBTC': [], 'EOSBTC': [], 'EVXBTC': [], 'FUELBTC': [], 'FUNBTC': [], 'GASBTC': [], 'GTOBTC': [], 'GVTBTC': [], 'GXSBTC': [], 'HSRBTC': [], 'ICNBTC': [], 'ICXBTC': [], 'IOTABTC': [], 'KMDBTC': [], 'KNCBTC': [], 'LENDBTC': [], 'LINKBTC': [], 'LRCBTC': [], 'LSKBTC': [], 'LUNBTC': [], 'MANABTC': [], 'MCOBTC': [], 'MDABTC': [], 'MODBTC': [], 'MTHBTC': [], 'MTLBTC': [], 'NAVBTC': [], 'NEBLBTC': [], 'NEOBTC': [], 'NULSBTC': [], 'OAXBTC': [], 'OMGBTC': [], 'OSTBTC': [], 'POEBTC': [], 'POWRBTC': [], 'PPTBTC': [], 'QSPBTC': [], 'RCNBTC': [], 'RDNBTC': [], 'REQBTC': [], 'SALTBTC': [], 'SNGLSBTC': [], 'SNMBTC': [], 'SNTBTC': [], 'STORJBTC': [], 'STRATBTC': [], 'SUBBTC': [], 'TNBBTC': [], 'TNTBTC': [], 'TRIGBTC': [], 'TRXBTC': [], 'VENBTC': [], 'VIBBTC': [], 'VIBEBTC': [], 'WABIBTC': [], 'WAVESBTC': [], 'WINGSBTC': [], 'WTCBTC': [], 'XVGBTC': [], 'XZCBTC': [], 'YOYOBTC': [], 'ZRXBTC': []}


#volume data for each interval over a specified period fo time
volumeAmounts = {'BTCUSDT': [], 'XRPBTC': [],
                'ETHBTC': [], 'BCCBTC': [],
                'LTCBTC': [], 'DASHBTC': [],
                'XMRBTC': [], 'QTUMBTC': [], 'ETCBTC': [],
                'ZECBTC': [], 'ADABTC': [], 'ADXBTC': [], 'AIONBTC' : [], 'AMBBTC': [], 'APPCBTC': [], 'ARKBTC': [], 'ARNBTC': [], 'ASTBTC': [], 'BATBTC': [], 'BCDBTC': [], 'BCPTBTC': [], 'BNBBTC': [], 'BNTBTC': [], 'BQXBTC': [], 'BRDBTC': [], 'BTSBTC': [], 'CDTBTC': [], 'CMTBTC': [], 'CNDBTC': [], 'CTRBTC': [], 'DGDBTC': [], 'DLTBTC': [], 'DNTBTC': [], 'EDOBTC': [], 'ELFBTC': [], 'ENGBTC': [], 'ENJBTC': [], 'EOSBTC': [], 'EVXBTC': [], 'FUELBTC': [], 'FUNBTC': [], 'GASBTC': [], 'GTOBTC': [], 'GVTBTC': [], 'GXSBTC': [], 'HSRBTC': [], 'ICNBTC': [], 'ICXBTC': [], 'IOTABTC': [], 'KMDBTC': [], 'KNCBTC': [], 'LENDBTC': [], 'LINKBTC': [], 'LRCBTC': [], 'LSKBTC': [], 'LUNBTC': [], 'MANABTC': [], 'MCOBTC': [], 'MDABTC': [], 'MODBTC': [], 'MTHBTC': [], 'MTLBTC': [], 'NAVBTC': [], 'NEBLBTC': [], 'NEOBTC': [], 'NULSBTC': [], 'OAXBTC': [], 'OMGBTC': [], 'OSTBTC': [], 'POEBTC': [], 'POWRBTC': [], 'PPTBTC': [], 'QSPBTC': [], 'RCNBTC': [], 'RDNBTC': [], 'REQBTC': [], 'SALTBTC': [], 'SNGLSBTC': [], 'SNMBTC': [], 'SNTBTC': [], 'STORJBTC': [], 'STRATBTC': [], 'SUBBTC': [], 'TNBBTC': [], 'TNTBTC': [], 'TRIGBTC': [], 'TRXBTC': [], 'VENBTC': [], 'VIBBTC': [], 'VIBEBTC': [], 'WABIBTC': [], 'WAVESBTC': [], 'WINGSBTC': [], 'WTCBTC': [], 'XVGBTC': [], 'XZCBTC': [], 'YOYOBTC': [], 'ZRXBTC': []}


#the percent price change over an hour, the number of intervals the price increased, and the weighted time where the crypto increased
pricePercentData = {'BTCUSDT': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XRPBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'ETHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'LTCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DASHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'XMRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'QTUMBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ETCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'ZECBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ADABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ADXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'AIONBTC' : {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'AMBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'APPCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ARKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ARNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ASTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BATBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCPTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BNBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BQXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BRDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BTSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CDTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CMTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CNDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CTRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DGDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DLTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EDOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ELFBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ENGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ENJBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EOSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EVXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'FUELBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'FUNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GASBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GTOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GVTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GXSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'HSRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ICNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ICXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'IOTABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'KMDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'KNCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LENDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LINKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LRCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LSKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LUNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MANABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MCOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MDABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MODBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MTHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MTLBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NAVBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NEBLBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NEOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NULSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OAXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OMGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OSTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'POEBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'POWRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'PPTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'QSPBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'RCNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'RDNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'REQBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SALTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNGLSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNMBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'STORJBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'STRATBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SUBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TNBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TRIGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TRXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VENBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VIBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VIBEBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WABIBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WAVESBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WINGSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WTCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XVGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XZCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'YOYOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ZRXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}}

#holds the percent volume change over an hour, the number of intervals the volume increased, and the weighted time where the crypto increased
volumePercentData = {'BTCUSDT': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XRPBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'ETHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'LTCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DASHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'XMRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'QTUMBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ETCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'ZECBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ADABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ADXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'AIONBTC' : {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'AMBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'APPCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ARKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ARNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ASTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BATBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCPTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BNBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BQXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BRDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BTSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CDTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CMTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CNDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CTRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DGDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DLTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EDOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ELFBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ENGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ENJBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EOSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EVXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'FUELBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'FUNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GASBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GTOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GVTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GXSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'HSRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ICNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ICXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'IOTABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'KMDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'KNCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LENDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LINKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LRCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LSKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LUNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MANABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MCOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MDABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MODBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MTHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MTLBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NAVBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NEBLBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NEOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NULSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OAXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OMGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OSTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'POEBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'POWRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'PPTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'QSPBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'RCNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'RDNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'REQBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SALTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNGLSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNMBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'STORJBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'STRATBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SUBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TNBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TRIGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TRXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VENBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VIBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VIBEBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WABIBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WAVESBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WINGSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WTCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XVGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XZCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'YOYOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ZRXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}}

#stores the calculated weightedMovingAverad
weightedMovingAverage = {'BTCUSDT': [], 'XRPBTC': [],
                'ETHBTC': [], 'BCCBTC': [],
                'LTCBTC': [], 'DASHBTC': [],
                'XMRBTC': [], 'QTUMBTC': [], 'ETCBTC': [],
                'ZECBTC': [], 'ADABTC': [], 'ADXBTC': [], 'AIONBTC' : [], 'AMBBTC': [], 'APPCBTC': [], 'ARKBTC': [], 'ARNBTC': [], 'ASTBTC': [], 'BATBTC': [], 'BCDBTC': [], 'BCPTBTC': [], 'BNBBTC': [], 'BNTBTC': [], 'BQXBTC': [], 'BRDBTC': [], 'BTSBTC': [], 'CDTBTC': [], 'CMTBTC': [], 'CNDBTC': [], 'CTRBTC': [], 'DGDBTC': [], 'DLTBTC': [], 'DNTBTC': [], 'EDOBTC': [], 'ELFBTC': [], 'ENGBTC': [], 'ENJBTC': [], 'EOSBTC': [], 'EVXBTC': [], 'FUELBTC': [], 'FUNBTC': [], 'GASBTC': [], 'GTOBTC': [], 'GVTBTC': [], 'GXSBTC': [], 'HSRBTC': [], 'ICNBTC': [], 'ICXBTC': [], 'IOTABTC': [], 'KMDBTC': [], 'KNCBTC': [], 'LENDBTC': [], 'LINKBTC': [], 'LRCBTC': [], 'LSKBTC': [], 'LUNBTC': [], 'MANABTC': [], 'MCOBTC': [], 'MDABTC': [], 'MODBTC': [], 'MTHBTC': [], 'MTLBTC': [], 'NAVBTC': [], 'NEBLBTC': [], 'NEOBTC': [], 'NULSBTC': [], 'OAXBTC': [], 'OMGBTC': [], 'OSTBTC': [], 'POEBTC': [], 'POWRBTC': [], 'PPTBTC': [], 'QSPBTC': [], 'RCNBTC': [], 'RDNBTC': [], 'REQBTC': [], 'SALTBTC': [], 'SNGLSBTC': [], 'SNMBTC': [], 'SNTBTC': [], 'STORJBTC': [], 'STRATBTC': [], 'SUBBTC': [], 'TNBBTC': [], 'TNTBTC': [], 'TRIGBTC': [], 'TRXBTC': [], 'VENBTC': [], 'VIBBTC': [], 'VIBEBTC': [], 'WABIBTC': [], 'WAVESBTC': [], 'WINGSBTC': [], 'WTCBTC': [], 'XVGBTC': [], 'XZCBTC': [], 'YOYOBTC': [], 'ZRXBTC': []}



#the modified cumulative volume over a period (a negative percent change will result in the volume change being counted as negative towards the
# cumulative volume stored here
modifiedVolume = {'BTCUSDT': 0.0, 'XRPBTC': 0.0,
                'ETHBTC': 0.0, 'BCCBTC': 0.0,
                'LTCBTC': 0.0, 'DASHBTC': 0.0,
                'XMRBTC': 0.0, 'QTUMBTC': 0.0, 'ETCBTC': 0.0,
                'ZECBTC': 0.0, 'ADABTC': 0.0, 'ADXBTC': 0.0, 'AIONBTC' : 0.0, 'AMBBTC': 0.0, 'APPCBTC': 0.0, 'ARKBTC': 0.0, 'ARNBTC': 0.0, 'ASTBTC': 0.0, 'BATBTC': 0.0, 'BCDBTC': 0.0, 'BCPTBTC': 0.0, 'BNBBTC': 0.0, 'BNTBTC': 0.0, 'BQXBTC': 0.0, 'BRDBTC': 0.0, 'BTSBTC': 0.0, 'CDTBTC': 0.0, 'CMTBTC': 0.0, 'CNDBTC': 0.0, 'CTRBTC': 0.0, 'DGDBTC': 0.0, 'DLTBTC': 0.0, 'DNTBTC': 0.0, 'EDOBTC': 0.0, 'ELFBTC': 0.0, 'ENGBTC': 0.0, 'ENJBTC': 0.0, 'EOSBTC': 0.0, 'EVXBTC': 0.0, 'FUELBTC': 0.0, 'FUNBTC': 0.0, 'GASBTC': 0.0, 'GTOBTC': 0.0, 'GVTBTC': 0.0, 'GXSBTC': 0.0, 'HSRBTC': 0.0, 'ICNBTC': 0.0, 'ICXBTC': 0.0, 'IOTABTC': 0.0, 'KMDBTC': 0.0, 'KNCBTC': 0.0, 'LENDBTC': 0.0, 'LINKBTC': 0.0, 'LRCBTC': 0.0, 'LSKBTC': 0.0, 'LUNBTC': 0.0, 'MANABTC': 0.0, 'MCOBTC': 0.0, 'MDABTC': 0.0, 'MODBTC': 0.0, 'MTHBTC': 0.0, 'MTLBTC': 0.0, 'NAVBTC': 0.0, 'NEBLBTC': 0.0, 'NEOBTC': 0.0, 'NULSBTC': 0.0, 'OAXBTC': 0.0, 'OMGBTC': 0.0, 'OSTBTC': 0.0, 'POEBTC': 0.0, 'POWRBTC': 0.0, 'PPTBTC': 0.0, 'QSPBTC': 0.0, 'RCNBTC': 0.0, 'RDNBTC': 0.0, 'REQBTC': 0.0, 'SALTBTC': 0.0, 'SNGLSBTC': 0.0, 'SNMBTC': 0.0, 'SNTBTC': 0.0, 'STORJBTC': 0.0, 'STRATBTC': 0.0, 'SUBBTC': 0.0, 'TNBBTC': 0.0, 'TNTBTC': 0.0, 'TRIGBTC': 0.0, 'TRXBTC': 0.0, 'VENBTC': 0.0, 'VIBBTC': 0.0, 'VIBEBTC': 0.0, 'WABIBTC': 0.0, 'WAVESBTC': 0.0, 'WINGSBTC': 0.0, 'WTCBTC': 0.0, 'XVGBTC': 0.0, 'XZCBTC': 0.0, 'YOYOBTC': 0.0, 'ZRXBTC': 0.0}




#holds the the other stat items in it
statDict = {}

#the binance intervals, their symbols, and their time in milliseconds
intervalTypes = { '1m': {'symbol': '1m', 'inMS': 60000},  '3m': {'symbol': '3m', 'inMS': 180000}, '5m': {'symbol': '5m', 'inMS': 300000}, '15m': {'symbol': '15m', 'inMS': 900000}, '30m': {'symbol': '30m', 'inMS': 1800000}, '1h': {'symbol': '1h', 'inMS': 3600000}, '2h': {'symbol': '2h', 'inMS': 7200000}, '4h': {'symbol': '4h', 'inMS': 14400000}, '6h': {'symbol': '6h', 'inMS': 21600000}, '8h': {'symbol': '8h', 'inMS': 28800000}, '12h': {'symbol': '12h', 'inMS': 43200000}, '1d': {'symbol': '1d', 'inMS': 86400000}, '3d': {'symbol': '3d', 'inMS': 259200000}, '1w': {'symbol': '1w' , 'inMS': 604800000}, '1M': {'symbol': '1M', 'inMS': 2629746000}}

#the score of each crypto
scores =  {}

#decimal precision allowed for trading each crypto
stepsizes = {}

#crypto being bouhgt and held
currencyToTrade = {}

#temporary variable that holds currently held crypto right before the logic to test if
#a new crypto is better to buy
oldCurrency = ''

#the new crytpo determined as the best one to buy
currentCurrency = ''

#in bitcoins (before trading)
initialBalance = 0.0

#in bitcoins (after trading)
currentBalance = 0.0

#cumulative percent change of a crypto's price over the course of owning it
CUMULATIVE_PERCENT_CHANGE = 0.0

#list to hold the values stored to find the max
values = {'PERCENT_BY_HOUR': [], 'VOLUME_BY_HOUR': [], 'TIME_INCREASING': [], 'WEIGHTED_TIME_INCREASING': [], 'VOLUME_TIME_INCREASING': [], 'WEIGHTED_VOLUME_TIME_INCREASING': [], 'MODIFIED_VOLUME': [], 'SCORE': []}


#hold the max values to be used for scaling
maxValues = {'PERCENT_BY_HOUR': 0.0, 'VOLUME_BY_HOUR': 0.0, 'TIME_INCREASING': 0.0, 'WEIGHTED_TIME_INCREASING': 0.0, 'VOLUME_TIME_INCREASING': 0.0, 'WEIGHTED_VOLUME_TIME_INCREASING': 0.0, 'MODIFIED_VOLUME': 0.0, 'SCORE': 0.0}

#todo remember that the wait parameters for this one should be different from the ones in auto trader where they are in seconds not minutes
PARAMETERS = {'PERCENT_QUANTITY_TO_SPEND': .9, 'PERCENT_TO_SPEND': 1.0, 'MINIMUM_PERCENT_INCREASE': 5.0, 'MINIMUM_SCORE': 0.01, 'MINIMUM_MOVING_AVERAGE': .001, 'MAX_DECREASE': -10.0, 'MAX_TIME_CYCLE': 60.0, 'MAX_CYCLES': 24, 'MAX_PERCENT_CHANGE': 15.0, 'NEGATIVE_WEIGHT': 1.0, 'CUMULATIVE_PERCENT_CHANGE': 0.0, 'CUMULATIVE_PERCENT_CHANGE_STORE': 0.0, 'SLOT_WEIGHT': 1.0, 'TIME_INCREASING_MODIFIER': 1.0, 'VOLUME_INCREASING_MODIFIER': 1.0, 'PERCENT_BY_HOUR_MODIFIER': 1.0, 'VOLUME_PERCENT_BY_HOUR_MODIFIER': 1.0, 'FLOOR_PRICE_MODIFIER': 1.005, 'MODIFIED_VOLUME_MODIFIER': 1.0, 'CUMULATIVE_PRICE_MODIFIER': 1.0, 'PRIMARY_MODIFIED_VOLUME_SCALER': 1.0, 'WAIT_FOR_CHECK_FAILURE': 5.0, 'WAIT_FOR_CHECK_TOO_LOW': 10.0, 'VARIATION_NUMBER': 0, 'CLASS_NUM': 0, 'INTERVAL_TO_TEST': 1440, 'MINUTES_IN_PAST': 0}


#number of minutes we want to iterate backwards
startMinute = 0
endMinute = 60
currentMinute = 0

#todo add a way to read in the runNumber from the crypto trainer
def readTheInput():
    stringKeySplit = ''
    stringValSplit = ''
    counter = 0

    for line in sys.stdin:

        if line != '':
            # split the passed string into a list seperated by spaces
            listSplits = line.split(' ')

            # loops through each string seperated out into listSplits
            for i in listSplits:
                # if the string is from an even position split it into a future key
                if (counter % 2 == 0):
                    stringKeySplit = i.split('\'')[1]
                # if the string is from an odd position split it to be a future value and update newDict to contain it
                if (counter % 2 != 0):
                    if ("," in i):
                        stringValSplit = i.split(',')[0]
                        PARAMETERS.update({stringKeySplit: float(stringValSplit)})
                    if ("}" in i):
                        stringValSplit = i.split('}')[0]
                        PARAMETERS.update({stringKeySplit: float(stringValSplit)})

                counter += 1


#get the balance in bitcoins

#buy the specified crypto currency
def buyBin(symbol, currentMinute):

    global priceBought
    ratio = getbinanceprice(symbol, currentMinute)
    priceBought = ratio
    #mark item as the current crypto being traded and save the buy price at for failure condition
    entry = {symbol:{'buyPrice': ratio, 'timestamp': 0}}
    currencyToTrade.clear()
    currencyToTrade.update(entry)

#sell the specified crypto
def sellBin(symbol):
   return 0


#add in the weight todo
#calculates the weighted moving average over the specified interval for a crypto currency

def setWeightedMovingAverage(currency, startMinute, endMinute):
    cumulativePrice = 0.0

    openPriceData = CryptoStats.getOpenPrice(PARAMETERS['INTERVAL_TO_TEST'], PARAMETERS['MINUTES_IN_PAST'])[currency]
    closePriceData = CryptoStats.getClosePrice(PARAMETERS['INTERVAL_TO_TEST'], PARAMETERS['MINUTES_IN_PAST'])[currency]

    slots = endMinute - startMinute - 1

    if openPriceData == []:
        return 0

    #adds up the cumulative price changes using each interval
    for x in range (startMinute, endMinute):
       startPrice = openPriceData[x]
       endPrice = closePriceData[x]
       change = calcPercentChange(startPrice, endPrice)

       cumulativePrice += change

    #the scaling of the cumulative price
    cumulativePrice = (cumulativePrice / slots) * PARAMETERS['CUMULATIVE_PRICE_MODIFIER']



    return cumulativePrice

# this function will update the weighted moving average every second the program runs todo
# def updateWeightedMovingAverage(currency, interval, starttime, endtime):


#gets the cumulative volume over a period and scales it based on the currency's price
def getVolume(currency, currentMinute):
    volume = []
    #building the request
    data = CryptoStats.getVolume(PARAMETERS['INTERVAL_TO_TEST'], PARAMETERS['MINUTES_IN_PAST'])[currency]
    #adds up all the volumes over the interval
    for x in data:
        if(x != ''):
            x = float(x)
            x *= float(getbinanceprice(currency, currentMinute))
        else:
            x = 0.0
        volume.append(x)
    return volume


#grabs the list of volumes over the interval and percent changes over the interal
#then interates through and calculates a cumulative volume where the volume is considered negative
#when the percent change was negative and positive when the percent change was positive
def getModifiedVolume(currency):
    oldVolume = 0
    currentSlot = 0

    percentChangesList = percentChanges[currency]
    volumeAmountList = volumeAmounts[currency]

    #adds up the volume with negative percent changes in price resulting in the volume
    #considered to be mostly 'negative', how much is determined by the magnitude
    #of the percent change in price
    for i in volumeAmountList:

        #makes each volume % change back into a decimal
        percentChangeScale = (percentChangesList[currentSlot] / 100)
        if percentChangeScale < 0:
            oldVolume += percentChangeScale * volumeAmountList[currentSlot] * PARAMETERS['NEGATIVE_WEIGHT']
        #todo the below may have not been there for the last set of tests
        if percentChangeScale >= 0:
            oldVolume += percentChangeScale * volumeAmountList[currentSlot]



        currentSlot += 1

    if(oldVolume == 0):
        file.write("Old volume was zero for " + str(currency))
    return float(oldVolume)

#get the binance price of the specified currency
def getbinanceprice(currency, currentMinute):

    priceDict = CryptoStats.getClosePrice(PARAMETERS['INTERVAL_TO_TEST'], PARAMETERS['MINUTES_IN_PAST'])
    if priceDict == {} or currency == '':
        return 0.0

    try:
        binPrice = priceDict[currency][currentMinute]
    except KeyError:
        file.write("price dict of " + str(currency) + str(priceDict))
        binPrice = 0.0
    return binPrice


    #interval based on this from binance API
    #     m -> minutes;     h -> hours;     d -> days;     w -> weeks;    M -> months
    #  1m  3m   5m  15m  30m  1h 2h 4h 6h 8h  12h  1d   3d  1w   1M
    # method used to update price lists on past hour of trends

#method to iterate through all the cryptos available on binance and store their price changes, percent price changes,
#volume changes, percent volume changes, scores, time increasing, and time decreasing


def updateCrypto(startMinute, endMinute, currentMinute):

    for key,value in priceSymbols.items():
        # Pulling the three dictionaries from the cryptostats class and getting the specific list associated with the current symbol
        openPriceData = CryptoStats.getOpenPrice(PARAMETERS['INTERVAL_TO_TEST'], PARAMETERS['MINUTES_IN_PAST'])[value]
        if startMinute == 0:
            file.write("Open data " + str(openPriceData))
        closePriceData = CryptoStats.getClosePrice(PARAMETERS['INTERVAL_TO_TEST'], PARAMETERS['MINUTES_IN_PAST'])[value]
        volumeData = getVolume(value, currentMinute)


        #todo figure out why this and the one below always starts at 0
        # calculate the percent change over the whole hour and store
        openPrice = openPriceData[startMinute]
        closePriceIndex = endMinute - 1
        closePrice = closePriceData[closePriceIndex]
        pricePercentData[value]['percentbyhour'] = calcPercentChange(openPrice, closePrice)

        values['PERCENT_BY_HOUR'].append(pricePercentData[value]['percentbyhour'])

        #todo figure out if it should have been endMinute - startMinute - 1 or just endMinute - 1
        # calculate the percent change in volume over the whole hour and store
        openVolume = volumeData[startMinute]
        closeVolumeIndex = endMinute - 1
        closeVolume = volumeData[closeVolumeIndex]
        volumePercentData[value]['percentbyhour'] = calcPercentChange(openVolume, closeVolume)

        # test.write("Currency: {} Open Price: {} Close Price: {} Open Volume: {} Close Volume: {} \n".format(value, openPrice, closePrice, openVolume, closeVolume))

        values['VOLUME_BY_HOUR'].append(volumePercentData[value]['percentbyhour'])

        # iterate through all the open and close prices for the given interval
        percentChanges[value] = []

        for i in range(startMinute, endMinute):
            percentChanges[value].append(calcPercentChange(openPriceData[i], closePriceData[i]))
            i+=1

        pricePercentData[value]['timeIncreasing'] = getTimeIncreasing(0, value)
        pricePercentData[value]['weightedtimeIncreasing'] = getTimeIncreasing(1, value)

        # calculate and store the percent time increasing for volume and price percent changes
        for i in range(startMinute, endMinute):
            volumePercentChanges[value].append(calcPercentChange(volumeData[i - 1], volumeData[i]))
            volumeAmounts[value].append(volumeData[i])

        volumePercentData[value]['timeIncreasing'] = getVolumeTimeIncreasing(0, value)
        volumePercentData[value]['weightedtimeIncreasing'] = getVolumeTimeIncreasing(1, value)

        # store the time increasing and weighted time increasing for price data to be used for scaling
        values['TIME_INCREASING'].append(pricePercentData[value]['timeIncreasing'])
        values['WEIGHTED_TIME_INCREASING'].append(pricePercentData[value]['weightedtimeIncreasing'])

        # reset the lists of the volume amounts and volume percent changes
        volumeAmounts[value] = []
        volumePercentChanges[value] = []

        # store the time increasing and weighted time increasing for volume data to be used for scaling
        values['VOLUME_TIME_INCREASING'].append(volumePercentData[value]['timeIncreasing'])
        values['WEIGHTED_VOLUME_TIME_INCREASING'].append(volumePercentData[value]['weightedtimeIncreasing'])

        volumeAmounts[value].append(volumeData[0])

        modifiedVolume[value] = 0
        # get the modified volume changes
        modifiedVolume[value] = getModifiedVolume(value)

        values['MODIFIED_VOLUME'].append(modifiedVolume[value])

        # calcualte a weightedMovingAverage
        weightedMovingAverage[value] = setWeightedMovingAverage(value, startMinute, endMinute)

    setMaxValue()

    resetValues()

    # gets the score for each crypto
    # moved to its own loop so all the values can be properly scaled by the largest value
    for key, value in priceSymbols.items():

        # use the calculations to get a score
        calc_score = getScore(value)
        new_score = {value: calc_score}
        scores.update(new_score)

        # calcualte a weightedMovingAverage
        weightedMovingAverage[value] = setWeightedMovingAverage(value, startMinute, endMinute)

    for key, value in scores.items():
        if (value > PARAMETERS['MINIMUM_SCORE']):
            entry = {key: value}
            currencyToTrade.update(entry)

    file.write("OUR LIST OF CRYPTO: " + str(scores))
    file.write("Currrenty to trade: " + str(currencyToTrade))


#caclulates and returns the time spent increasing
#weighted = 0 is false, weighted = 1 is true
 # TODO update the modulo so that it is a modulo not a multiplcation so that
 #patterns are detected
def getTimeIncreasing(isWeighted, currency):

    list = percentChanges[currency]
    slots = 0.0
    slots_increasing = 0.0

    for i in list:
            slots+=1

            #the four if statements only differ in that the second two
            #caclcualte slots_increasing using a weight
            #that casues positive increases early in the hour to matter less
            #than increases later in the hour
            #In addition, the second and fourth if statement consider the slots with a negative
            #percent change

            if float(i) > 0.0 and isWeighted == 0:
              slots_increasing+=1*i

            if float(i) < 0.0 and isWeighted == 0:
              slots_increasing += 1 * i * PARAMETERS['NEGATIVE_WEIGHT']

            if float(i) > 0.0 and isWeighted == 1:
              slots_increasing+=(1*(slots * PARAMETERS['SLOT_WEIGHT'])*i)


            if float(i) < 0.0 and isWeighted == 1:
              slots_increasing += (1*(slots * PARAMETERS['SLOT_WEIGHT'])*i * PARAMETERS['NEGATIVE_WEIGHT'])

    if(slots == 0.0):
        slots = 1.0

    return (slots_increasing/slots) * PARAMETERS['TIME_INCREASING_MODIFIER']


#caclulates and returns the time spent increasing for volume
#weighted = 0 is false, weighted = 1 is true
def getVolumeTimeIncreasing(isWeighted, currency):

    list = volumePercentChanges[currency]
    slots = 0.0
    slots_increasing = 0.0

    for i in list:
            slots+=1

            #first two if statements consider the slots_increasing for a nonweighted calcualtion
            #second and fourth if statements consider the negative percent changes

            if float(i) > 0.0 and isWeighted == 0:
              slots_increasing+=1*i

            if float(i) < 0.0 and isWeighted == 0:
              slots_increasing += 1 * i * PARAMETERS['NEGATIVE_WEIGHT']

            if float(i) > 0.0 and isWeighted == 1:
              slots_increasing+=(1*(slots * PARAMETERS['SLOT_WEIGHT']) * i )

            if float(i) < 0.0 and isWeighted == 1:
              slots_increasing += (1*(slots * PARAMETERS['SLOT_WEIGHT']) * i * PARAMETERS['NEGATIVE_WEIGHT'])

    if (slots == 0.0):
        slots = 1.0

    return (slots_increasing/slots) * PARAMETERS['VOLUME_INCREASING_MODIFIER']

# method to calculate the "score" that crypto get when they are updated by hour
# score is a combination of weighted time increasing and % change over hour.
# for both volume and price
def getScore(symbol):

    new_score = 0.0


    # setting up the scaled values for checking
    values['VOLUME_BY_HOUR'].append(volumePercentData[symbol]['percentbyhour'] / maxValues['VOLUME_BY_HOUR'])
    values['PERCENT_BY_HOUR'].append(((pricePercentData[symbol]['percentbyhour']) / maxValues['PERCENT_BY_HOUR']))
    if(maxValues['TIME_INCREASING']!=0):
        values['TIME_INCREASING'].append(pricePercentData[symbol]['timeIncreasing'] / maxValues['TIME_INCREASING'])
    values['VOLUME_TIME_INCREASING'].append(volumePercentData[symbol]['timeIncreasing'] / maxValues['TIME_INCREASING'])
    values['WEIGHTED_TIME_INCREASING'].append((pricePercentData[symbol]['weightedtimeIncreasing'] / maxValues['WEIGHTED_TIME_INCREASING']))
    values['WEIGHTED_VOLUME_TIME_INCREASING'].append((volumePercentData[symbol]['weightedtimeIncreasing'] / maxValues['WEIGHTED_VOLUME_TIME_INCREASING']))

    try:
        values['MODIFIED_VOLUME'].append((modifiedVolume[symbol] / maxValues['MODIFIED_VOLUME']))
    except ZeroDivisionError:
        file.write("Whoopsie zero by division error!" + str(maxValues))
        for i in values:
            file.write(str(i) + '\n')


    #addingup the parameters to the score variable
    new_score += (volumePercentData[symbol]['percentbyhour'] / maxValues['VOLUME_BY_HOUR']) * PARAMETERS['VOLUME_PERCENT_BY_HOUR_MODIFIER']
    new_score += ((pricePercentData[symbol]['percentbyhour']) / maxValues['PERCENT_BY_HOUR']) * PARAMETERS['PERCENT_BY_HOUR_MODIFIER']


    new_score += (pricePercentData[symbol]['weightedtimeIncreasing'] / maxValues['WEIGHTED_TIME_INCREASING'])

    new_score += (volumePercentData[symbol]['weightedtimeIncreasing'] / maxValues['WEIGHTED_VOLUME_TIME_INCREASING'])

    try:
        new_score += (modifiedVolume[symbol] / maxValues['MODIFIED_VOLUME']) * PARAMETERS['MODIFIED_VOLUME_MODIFIER']
    except ZeroDivisionError:
        file.write("Whoopsie this other zero by division error!" + str(maxValues))
        for i in values:
            file.write(str(i) + '\n')



    return new_score


#finds the next currency to buy
def priceChecker():
    currencyToBuy = ''
    #Compares the two price lists and sets the currencyToBuy to be
    # the coin with the highest score that also is above the minimum moving average
    maxScore = 0
    for key, value in currencyToTrade.items():
        #print("The score of {} is {} ".format(key, scores[key]))

        try:
            if(maxScore < scores[key] and float(weightedMovingAverage[key]) > float(PARAMETERS['MINIMUM_MOVING_AVERAGE'])):
                maxScore = scores[key]
                #print("CURRENT HIGH SCORE: The score of {} is {}".format(key, scores[key]))
                currencyToBuy = key
        except KeyError:
            file.write(" LINE 550 key error " + str(key) + " scores[key] " + weightedMovingAverage[key])

    #print("Coin with the highest score is {} which is {}".format(currencyToBuy, maxScore))

    return currencyToBuy #potential runtime error if all negative todo


#just calculates the percent change between two values
def calcPercentChange(startVal, endVal):
    if(float(startVal) == 0.0):
        return float(endVal) * 100.0

    return (((float(endVal) - float(startVal))/float(startVal) ) * 100)


#checks if the current crypto has been decreasing the past ten minutes
#if yes it forces a new check to see if there is a better crypto
def checkFailureCondition(currency, timesIncreasing, startMinute, endMinute):

    #print("New Interval")

    openPriceData = CryptoStats.getOpenPrice(PARAMETERS['INTERVAL_TO_TEST'], PARAMETERS['MINUTES_IN_PAST'])[currency]
    closePriceData = CryptoStats.getClosePrice(PARAMETERS['INTERVAL_TO_TEST'], PARAMETERS['MINUTES_IN_PAST'])[currency]

    #get the starting price of the interval
    startPriceInterval = openPriceData[startMinute]
    timeIncreasingCounter = 0

    #iterate through the list of percent changes and add up when the percent change was positive
    for x in range(startMinute, endMinute):
        startPrice = openPriceData[x]
        endPrice = closePriceData[x]
        #print("Current Crypto: {} Start Price: {} End Price: {}".format(currency, startPrice, endPrice))
        percentChange = calcPercentChange(startPrice, endPrice)
        if(percentChange > 0):
            timeIncreasingCounter += 1


    intervalPercentChange = calcPercentChange(startPriceInterval, endPrice)
    #print("Cumulative percent change over THIS INTERVAL {}".format(intervalPercentChange))
    #print("Times Increasing over the interval: {}".format(timeIncreasingCounter))

    if(timeIncreasingCounter <= timesIncreasing):
        #print("DECREASED ALL INTERVALS. RESTART")
        return 1

    return 0

#checks whether the function has caused too large of negative decrease the specified interval
def checkTooNegative(symbol, currentMinute):

    openPriceData = CryptoStats.getOpenPrice(PARAMETERS['INTERVAL_TO_TEST'], PARAMETERS['MINUTES_IN_PAST'])[symbol]
    closePriceData = CryptoStats.getClosePrice(PARAMETERS['INTERVAL_TO_TEST'], PARAMETERS['MINUTES_IN_PAST'])[symbol]

    startPrice = openPriceData[currentMinute]
    endPrice = closePriceData[currentMinute]
    percentChange = calcPercentChange(startPrice, endPrice)

    if(percentChange < PARAMETERS['MAX_DECREASE']):
        #print("TOO NEGATIVE. RESTART")
        return 1

    return 0

#checks to see if the currency has increased or decreased more than is allowed
# if yes, then the reevaluation process is restarted
def checkExitCondition(currency, currentMinute):

    global priceBought

    currentPrice= getbinanceprice(currency, currentMinute)

    percentChange = calcPercentChange(priceBought, currentPrice)

    if(percentChange >= PARAMETERS['MAX_PERCENT_CHANGE']):
        #print("HIT MAX PERCENT CHANGE")
        return 1

    if(percentChange <= -1 * PARAMETERS['MAX_PERCENT_CHANGE']):
        #print("HIT MINIMUM PERCENT CHANGE")
        return 1

    return 0

#checks to see if the current currency is too near to its starting point
def checkTooLow(currency, timesIncreasing, startMinute, endMinute):
    global priceBought

    currentPrice = getbinanceprice(currency, startMinute)
    floorPrice = PARAMETERS['FLOOR_PRICE_MODIFIER'] * float(priceBought)

    #checks to see if the coin was increasing or decreasing over the last 15 minutes. +13 since endMinute is already one greater than start minute and +8 since checkFailureCondition uses 10 minute intervals
    direction = increasingOrDecreasing(currency, startMinute, endMinute+13)
    allIntervalsDecreasing = checkFailureCondition(currency, timesIncreasing, startMinute, endMinute+8)

    #check to see if the current price is too low, the crypto is decreasing over the past 15 minutes
    #and all the intervals are decreasing
    if(float(currentPrice) < float(floorPrice) and direction == 0 & allIntervalsDecreasing == 1):
        #print("WAS TOO LOW")
        return 1

    return 0

#returns whether the specified currency is increasing or decreasing over the interval
# 0 means decreasing, 1 means stable or increasing
def increasingOrDecreasing(currency, startMinute, endMinute):

    openPriceData = CryptoStats.getOpenPrice(PARAMETERS['INTERVAL_TO_TEST'], PARAMETERS['MINUTES_IN_PAST'])[currency]
    closePriceData = CryptoStats.getClosePrice(PARAMETERS['INTERVAL_TO_TEST'], PARAMETERS['MINUTES_IN_PAST'])[currency]


    startPrice = openPriceData[startMinute]
    endPrice = closePriceData[endMinute]

    calcPChange = calcPercentChange(startPrice, endPrice)

    if(calcPChange >= 0.0):
        return 1

    return 0


def resetValues():
    #reset the list of parameter value that are calculated below
    for key, value in values.items():
        values[key] = []


#runs through the values collected and storess the max value
def setMaxValue():

    for key, value in values.items():
        currentMaxVal = 0

        for i in values[key]:
            if i > currentMaxVal or currentMaxVal == 0:
                maxValues[key] = i
                currentMaxVal = i

    #print("THE VALUES {}".format(values))
    #print("THE MAX {}".format(maxValues))

#creates a dictionary with all the different statistic holding dictionaries that are created with each run
def createStatsDict():
    statDict.update({'percentChanges': percentChanges})
    statDict.update({'volumePercentChanges': volumePercentChanges})
    statDict.update({'volumeAmounts': volumeAmounts})
    statDict.update({'pricePercentData': pricePercentData})
    statDict.update({'volumePercentData': volumePercentData})
    statDict.update({'weightedMovingAverage': weightedMovingAverage})
    statDict.update({'modifiedVolume': modifiedVolume})



#todo add in a parser to read the stdin that will be passed with the parameters from cryptotrainer

def main():
    global CUMULATIVE_PERCENT_CHANGE
    global initialBalance
    global RESTART
    global RESTART_TN
    global RESTART_LOW
    global EXIT
    global pricesold
    global priceBought
    global startMinute
    global endMinute
    global currentMinute

    startMinute = 0
    endMinute = 60
    currentMinute = startMinute

    #creates a statistic object to record the different decisions and then analyze them
    cryptoRunStats = CryptoStatAnalysis.CryptoStatsAnalysis(PARAMETERS['VARIATION_NUMBER'], PARAMETERS['CLASS_NUM'], 'NT', startMinute, endMinute, PARAMETERS)

    currentCurrency = ''
    x = 0

    readTheInput()
    PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE'] = 0.0
    PARAMETERS['CUMULATIVE_PERCENT_CHANGE'] = 0.0
    #print("Date and Time of Run {}".format(datetime.datetime.now()))

    while(x < PARAMETERS['MAX_CYCLES'] and EXIT == 0):
        t = 0
        RESTART = 0
        RESTART_LOW = 0
        RESTART_TN = 0
        didSell = 0
        didBuy = 0
        currentMinute = startMinute

        updateCrypto(startMinute, endMinute, currentMinute)
        currentMinute += 1

        oldCurrency = currentCurrency
        currentCurrency = priceChecker()


        if(oldCurrency != currentCurrency and oldCurrency != ''):

            pricesold = getbinanceprice(oldCurrency, currentMinute)
            sellBin(oldCurrency)
            didSell = 1

            #print("THIS RUN SOLD AT: {}".format(currentMinute))
            cumulativePercentChange = calcPercentChange(priceBought, pricesold)
            PARAMETERS['CUMULATIVE_PERCENT_CHANGE'] = cumulativePercentChange
            PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE'] += cumulativePercentChange

            #print('Selling: {} Price bought: {} Price sold: {} '.format(oldCurrency, priceBought, pricesold))
            #print("FINAL percent change over the life of owning this crypto " + str(PARAMETERS['CUMULATIVE_PERCENT_CHANGE']))

        if(oldCurrency != currentCurrency)and (currentCurrency != ''):
            buyBin(currentCurrency, currentMinute)
            didBuy = 1
            #print("THIS RUN BOUGHT AT: {}".format(currentMinute))
            #print("Buying {} at price: {}".format(currentCurrency, priceBought))

        # if you bought or sold something OR if you did neither than set up a new dictionary of holders to evaluate this decision
        if didBuy == 1 or didSell == 1 or currentCurrency == '':
            cryptoRunStats.newStats(currentMinute, statDict, didBuy, didSell, currentCurrency, oldCurrency)


        #while statement is more flexible way to wait for a period of time or a restart
        # restart could be caused by a met failure condition or a met sustained one

        while(t < PARAMETERS['MAX_TIME_CYCLE'] and RESTART == 0 and RESTART_TN == 0 and RESTART_LOW == 0 and currentCurrency != ''):

            if(t % PARAMETERS['WAIT_FOR_CHECK_FAILURE'] == 0 and t != 0):
                RESTART = checkFailureCondition(currentCurrency, 0, currentMinute, currentMinute+9)

            if(t > PARAMETERS['WAIT_FOR_CHECK_TOO_LOW'] and t % PARAMETERS['WAIT_FOR_CHECK_FAILURE']):
                RESTART_LOW = checkTooLow(currentCurrency, 0, currentMinute, currentMinute+1)

            RESTART_TN = checkTooNegative(currentCurrency, currentMinute)
            t+=1
            currentMinute += 1


        if(oldCurrency == currentCurrency and currentCurrency != ''):
            newPrice = getbinanceprice(currentCurrency, currentMinute)
            cumulativePercentChange = calcPercentChange(priceBought, newPrice)
            PARAMETERS['CUMULATIVE_PERCENT_CHANGE'] = cumulativePercentChange
            PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE'] += cumulativePercentChange
            priceBought = newPrice

        if currentCurrency != '':
            EXIT = checkExitCondition(currentCurrency, currentMinute)

        if currentCurrency == '':
            temp = startMinute
            startMinute += 5 + (currentMinute - startMinute)
            endMinute += 5 + (currentMinute - temp)

        else:
            temp = startMinute
            startMinute += (currentMinute - startMinute)
            endMinute += (currentMinute - temp)

        x+=1


    #print("Cumulative percent change over the life of all cryptos owneed so far {}".format(PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE']))
    sellBin(currentCurrency)

    #special print statement used to get the parameters back
    print("LINEBEGIN" + str(PARAMETERS) + "DONEEND")
    #print(len(CryptoStats.getOpenPrice(PARAMETERS['INTERVAL_TO_TEST'], PARAMETERS['MINUTES_IN_PAST'])['BTCUSDT']))
    #print(str(CryptoStats.getOpenPrice(PARAMETERS['INTERVAL_TO_TEST'], PARAMETERS['MINUTES_IN_PAST'])['BTCUSDT'][0]))
    #print(str(CryptoStats.getOpenPrice(PARAMETERS['INTERVAL_TO_TEST'], PARAMETERS['MINUTES_IN_PAST'])['BTCUSDT'][len(CryptoStats.getOpenPrice(PARAMETERS['INTERVAL_TO_TEST'], PARAMETERS['MINUTES_IN_PAST'])['BTCUSDT']) - 1]))


if __name__ == "__main__":
    main()
