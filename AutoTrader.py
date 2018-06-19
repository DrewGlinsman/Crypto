# Copyright (c) 2018 A&D
# This is an auto trading bot for cryptocurrency on Binance

#todo add social media data input
#todo make the slots work as modulos so that we can detect patterns
#todo initilaize parameters from best parameter text file
#todo add youtube channel data
#todo add suspect youtube channels from reddit list
#todo make a true weighted mean function that pulls the most recent price every minute from the current crypto and calculates the new mean (if possible pull
#todo continued... every crypto and store the mean in a list so it can be continuously calculated
#todo continued remember to reset the time values on best parameters.txt
#todo make it so that it maxValue is not equal to 0 thereby causing division by 0

#import for python3 to increase compatability
from __future__ import absolute_import

import requests
import hmac
import hashlib
import time
import math
import datetime
import os


from PrivateData import api_key, secret_key, solume_api_key
import CryptoStatAnalysis

try:
    from urlib import urlencode

except ImportError:
    from urllib.parse import urlencode


#if 1 it does not reset the parameters to be the best ones
TESTING = 1

#setup the relative file path
dirname = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dirname + '/', 'Logs')

#Directory path (r makes this a raw string so the backslashes do not cause a compiler issue
logPaths = os.path.join(dirname + '/', 'Logs')

#log file name + path
logCompletePath = os.path.join(logPaths, "log.txt")

#open a file for appending (a). + creates file if does not exist
file = open(logCompletePath, "a+")

#Directory path (r makes this a raw string so the backslashes do not cause a compiler issue
paramPaths = os.path.join(dirname, '')

#param file name + path
paramCompletePath = os.path.join(paramPaths, "BEST_PARAMETERS.txt")

#open a file for appending (a). + creates file if does not exist
fileParams = open(paramCompletePath, "r")

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
                'Zcash': 'ZECBTC', 'ADA': 'ADABTC', 'ADX': 'ADXBTC', 'AION' : 'AIONBTC', 'AMB': 'AMBBTC', 'APPC': 'APPCBTC', 'ARK': 'ARKBTC', 'ARN': 'ARNBTC', 'AST': 'ASTBTC', 'BAT': 'BATBTC', 'BCD': 'BCDBTC', 'BCPT': 'BCPTBTC', 'BNB': 'BNBBTC', 'BNT': 'BNTBTC', 'BQX': 'BQXBTC', 'BRD': 'BRDBTC', 'BTS': 'BTSBTC', 'CDT': 'CDTBTC', 'CMT': 'CMTBTC', 'CND': 'CNDBTC', 'DGD': 'DGDBTC', 'DLT': 'DLTBTC', 'DNT': 'DNTBTC', 'EDO': 'EDOBTC', 'ELF': 'ELFBTC', 'ENG': 'ENGBTC', 'ENJ': 'ENJBTC', 'EOS': 'EOSBTC', 'EVX': 'EVXBTC', 'FUEL': 'FUELBTC', 'FUN': 'FUNBTC', 'GAS': 'GASBTC', 'GTO': 'GTOBTC', 'GVT': 'GVTBTC', 'GXS': 'GXSBTC', 'HSR': 'HSRBTC', 'ICN': 'ICNBTC', 'ICX': 'ICXBTC', 'IOTA': "IOTABTC", 'KMD': 'KMDBTC', 'KNC': 'KNCBTC', 'LEND': 'LENDBTC', 'LINK':'LINKBTC', 'LRC':'LRCBTC', 'LSK':'LSKBTC', 'LUN': 'LUNBTC', 'MANA': 'MANABTC', 'MCO': 'MCOBTC', 'MDA': 'MDABTC', 'MOD': 'MODBTC', 'MTH': 'MTHBTC', 'MTL': 'MTLBTC', 'NAV': 'NAVBTC', 'NEBL': 'NEBLBTC', 'NEO': 'NEOBTC', 'NULS': 'NULSBTC', 'OAX': 'OAXBTC', 'OMG': 'OMGBTC', 'OST': 'OSTBTC', 'POE': 'POEBTC', 'POWR': 'POWRBTC', 'PPT': 'PPTBTC', 'QSP': 'QSPBTC', 'RCN': 'RCNBTC', 'RDN': 'RDNBTC', 'REQ': 'REQBTC', 'SALT': 'SALTBTC', 'SNGLS': 'SNGLSBTC', 'SNM': 'SNMBTC', 'SNT': 'SNTBTC', 'STORJ': 'STORJBTC', 'STRAT': 'STRATBTC', 'SUB': 'SUBBTC', 'TNB': 'TNBBTC', 'TNT': 'TNTBTC', 'TRIG': 'TRIGBTC', 'TRX': 'TRXBTC', 'VEN': 'VENBTC', 'VIB': 'VIBBTC', 'VIBE': 'VIBEBTC', 'WABI': 'WABIBTC', 'WAVES': 'WAVESBTC', 'WINGS': 'WINGSBTC', 'WTC': 'WTCBTC', 'XVG': 'XVGBTC', 'XZC': 'XZCBTC', 'YOYO': 'YOYOBTC', 'ZRX': 'ZRXBTC'}





#percent changes of the prices for each crypto with an interval size over a specified period of time
percentChanges = {'BTCUSDT': [], 'XRPBTC': [],
                'ETHBTC': [], 'BCCBTC': [],
                'LTCBTC': [], 'DASHBTC': [],
                'XMRBTC': [], 'QTUMBTC': [], 'ETCBTC': [],
                'ZECBTC': [], 'ADABTC': [], 'ADXBTC': [], 'AIONBTC' : [], 'AMBBTC': [], 'APPCBTC': [], 'ARKBTC': [], 'ARNBTC': [], 'ASTBTC': [], 'BATBTC': [], 'BCDBTC': [], 'BCPTBTC': [], 'BNBBTC': [], 'BNTBTC': [], 'BQXBTC': [], 'BRDBTC': [], 'BTSBTC': [], 'CDTBTC': [], 'CMTBTC': [], 'CNDBTC': [], 'DGDBTC': [], 'DLTBTC': [], 'DNTBTC': [], 'EDOBTC': [], 'ELFBTC': [], 'ENGBTC': [], 'ENJBTC': [], 'EOSBTC': [], 'EVXBTC': [], 'FUELBTC': [], 'FUNBTC': [], 'GASBTC': [], 'GTOBTC': [], 'GVTBTC': [], 'GXSBTC': [], 'HSRBTC': [], 'ICNBTC': [], 'ICXBTC': [], 'IOTABTC': [], 'KMDBTC': [], 'KNCBTC': [], 'LENDBTC': [], 'LINKBTC': [], 'LRCBTC': [], 'LSKBTC': [], 'LUNBTC': [], 'MANABTC': [], 'MCOBTC': [], 'MDABTC': [], 'MODBTC': [], 'MTHBTC': [], 'MTLBTC': [], 'NAVBTC': [], 'NEBLBTC': [], 'NEOBTC': [], 'NULSBTC': [], 'OAXBTC': [], 'OMGBTC': [], 'OSTBTC': [], 'POEBTC': [], 'POWRBTC': [], 'PPTBTC': [], 'QSPBTC': [], 'RCNBTC': [], 'RDNBTC': [], 'REQBTC': [], 'SALTBTC': [], 'SNGLSBTC': [], 'SNMBTC': [], 'SNTBTC': [], 'STORJBTC': [], 'STRATBTC': [], 'SUBBTC': [], 'TNBBTC': [], 'TNTBTC': [], 'TRIGBTC': [], 'TRXBTC': [], 'VENBTC': [], 'VIBBTC': [], 'VIBEBTC': [], 'WABIBTC': [], 'WAVESBTC': [], 'WINGSBTC': [], 'WTCBTC': [], 'XVGBTC': [], 'XZCBTC': [], 'YOYOBTC': [], 'ZRXBTC': []}

#percent changes of the volume for each crypto with an interval size over a specified period of time
volumePercentChanges = {'BTCUSDT': [], 'XRPBTC': [],
                'ETHBTC': [], 'BCCBTC': [],
                'LTCBTC': [], 'DASHBTC': [],
                'XMRBTC': [], 'QTUMBTC': [], 'ETCBTC': [],
                'ZECBTC': [], 'ADABTC': [], 'ADXBTC': [], 'AIONBTC' : [], 'AMBBTC': [], 'APPCBTC': [], 'ARKBTC': [], 'ARNBTC': [], 'ASTBTC': [], 'BATBTC': [], 'BCDBTC': [], 'BCPTBTC': [], 'BNBBTC': [], 'BNTBTC': [], 'BQXBTC': [], 'BRDBTC': [], 'BTSBTC': [], 'CDTBTC': [], 'CMTBTC': [], 'CNDBTC': [], 'DGDBTC': [], 'DLTBTC': [], 'DNTBTC': [], 'EDOBTC': [], 'ELFBTC': [], 'ENGBTC': [], 'ENJBTC': [], 'EOSBTC': [], 'EVXBTC': [], 'FUELBTC': [], 'FUNBTC': [], 'GASBTC': [], 'GTOBTC': [], 'GVTBTC': [], 'GXSBTC': [], 'HSRBTC': [], 'ICNBTC': [], 'ICXBTC': [], 'IOTABTC': [], 'KMDBTC': [], 'KNCBTC': [], 'LENDBTC': [], 'LINKBTC': [], 'LRCBTC': [], 'LSKBTC': [], 'LUNBTC': [], 'MANABTC': [], 'MCOBTC': [], 'MDABTC': [], 'MODBTC': [], 'MTHBTC': [], 'MTLBTC': [], 'NAVBTC': [], 'NEBLBTC': [], 'NEOBTC': [], 'NULSBTC': [], 'OAXBTC': [], 'OMGBTC': [], 'OSTBTC': [], 'POEBTC': [], 'POWRBTC': [], 'PPTBTC': [], 'QSPBTC': [], 'RCNBTC': [], 'RDNBTC': [], 'REQBTC': [], 'SALTBTC': [], 'SNGLSBTC': [], 'SNMBTC': [], 'SNTBTC': [], 'STORJBTC': [], 'STRATBTC': [], 'SUBBTC': [], 'TNBBTC': [], 'TNTBTC': [], 'TRIGBTC': [], 'TRXBTC': [], 'VENBTC': [], 'VIBBTC': [], 'VIBEBTC': [], 'WABIBTC': [], 'WAVESBTC': [], 'WINGSBTC': [], 'WTCBTC': [], 'XVGBTC': [], 'XZCBTC': [], 'YOYOBTC': [], 'ZRXBTC': []}


#volume data for each interval over a specified period fo time
volumeAmounts = {'BTCUSDT': [], 'XRPBTC': [],
                'ETHBTC': [], 'BCCBTC': [],
                'LTCBTC': [], 'DASHBTC': [],
                'XMRBTC': [], 'QTUMBTC': [], 'ETCBTC': [],
                'ZECBTC': [], 'ADABTC': [], 'ADXBTC': [], 'AIONBTC' : [], 'AMBBTC': [], 'APPCBTC': [], 'ARKBTC': [], 'ARNBTC': [], 'ASTBTC': [], 'BATBTC': [], 'BCDBTC': [], 'BCPTBTC': [], 'BNBBTC': [], 'BNTBTC': [], 'BQXBTC': [], 'BRDBTC': [], 'BTSBTC': [], 'CDTBTC': [], 'CMTBTC': [], 'CNDBTC': [], 'DGDBTC': [], 'DLTBTC': [], 'DNTBTC': [], 'EDOBTC': [], 'ELFBTC': [], 'ENGBTC': [], 'ENJBTC': [], 'EOSBTC': [], 'EVXBTC': [], 'FUELBTC': [], 'FUNBTC': [], 'GASBTC': [], 'GTOBTC': [], 'GVTBTC': [], 'GXSBTC': [], 'HSRBTC': [], 'ICNBTC': [], 'ICXBTC': [], 'IOTABTC': [], 'KMDBTC': [], 'KNCBTC': [], 'LENDBTC': [], 'LINKBTC': [], 'LRCBTC': [], 'LSKBTC': [], 'LUNBTC': [], 'MANABTC': [], 'MCOBTC': [], 'MDABTC': [], 'MODBTC': [], 'MTHBTC': [], 'MTLBTC': [], 'NAVBTC': [], 'NEBLBTC': [], 'NEOBTC': [], 'NULSBTC': [], 'OAXBTC': [], 'OMGBTC': [], 'OSTBTC': [], 'POEBTC': [], 'POWRBTC': [], 'PPTBTC': [], 'QSPBTC': [], 'RCNBTC': [], 'RDNBTC': [], 'REQBTC': [], 'SALTBTC': [], 'SNGLSBTC': [], 'SNMBTC': [], 'SNTBTC': [], 'STORJBTC': [], 'STRATBTC': [], 'SUBBTC': [], 'TNBBTC': [], 'TNTBTC': [], 'TRIGBTC': [], 'TRXBTC': [], 'VENBTC': [], 'VIBBTC': [], 'VIBEBTC': [], 'WABIBTC': [], 'WAVESBTC': [], 'WINGSBTC': [], 'WTCBTC': [], 'XVGBTC': [], 'XZCBTC': [], 'YOYOBTC': [], 'ZRXBTC': []}


#the percent price change over an hour, the number of intervals the price increased, and the weighted time where the crypto increased
pricePercentData = {'BTCUSDT': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XRPBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'ETHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'LTCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DASHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'XMRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'QTUMBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ETCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'ZECBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ADABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ADXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'AIONBTC' : {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'AMBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'APPCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ARKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ARNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ASTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BATBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCPTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BNBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BQXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BRDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BTSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CDTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CMTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CNDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DLTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EDOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ELFBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ENGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ENJBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EOSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EVXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'FUELBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'FUNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GASBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GTOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GVTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GXSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'HSRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ICNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ICXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'IOTABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'KMDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'KNCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LENDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LINKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LRCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LSKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LUNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MANABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MCOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MDABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MODBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MTHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MTLBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NAVBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NEBLBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NEOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NULSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OAXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OMGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OSTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'POEBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'POWRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'PPTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'QSPBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'RCNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'RDNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'REQBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SALTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNGLSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNMBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'STORJBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'STRATBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SUBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TNBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TRIGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TRXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VENBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VIBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VIBEBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WABIBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WAVESBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WINGSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WTCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XVGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XZCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'YOYOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ZRXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}}

#holds the percent volume change over an hour, the number of intervals the volume increased, and the weighted time where the crypto increased
volumePercentData = {'BTCUSDT': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XRPBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'ETHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'LTCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DASHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'XMRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'QTUMBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ETCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'ZECBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ADABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ADXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'AIONBTC' : {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'AMBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'APPCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ARKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ARNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ASTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BATBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCPTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BNBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BQXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BRDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BTSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CDTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CMTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CNDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DGDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DLTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EDOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ELFBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ENGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ENJBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EOSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EVXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'FUELBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'FUNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GASBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GTOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GVTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GXSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'HSRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ICNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ICXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'IOTABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'KMDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'KNCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LENDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LINKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LRCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LSKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LUNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MANABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MCOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MDABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MODBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MTHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MTLBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NAVBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NEBLBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NEOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NULSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OAXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OMGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OSTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'POEBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'POWRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'PPTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'QSPBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'RCNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'RDNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'REQBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SALTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNGLSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNMBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'STORJBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'STRATBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SUBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TNBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TRIGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TRXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VENBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VIBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VIBEBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WABIBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WAVESBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WINGSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WTCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XVGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XZCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'YOYOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ZRXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}}

#stores the calculated weightedMovingAverad
weightedMovingAverage = {'BTCUSDT': 0, 'XRPBTC': 0,
                'ETHBTC': 0, 'BCCBTC': 0,
                'LTCBTC': 0, 'DASHBTC': 0,
                'XMRBTC': 0, 'QTUMBTC': 0, 'ETCBTC': 0,
                'ZECBTC': 0, 'ADABTC': 0, 'ADXBTC': 0, 'AIONBTC' : 0, 'AMBBTC': 0, 'APPCBTC': 0, 'ARKBTC': 0, 'ARNBTC': 0, 'ASTBTC': 0, 'BATBTC': 0, 'BCDBTC': 0, 'BCPTBTC': 0, 'BNBBTC': 0, 'BNTBTC': 0, 'BQXBTC': 0, 'BRDBTC': 0, 'BTSBTC': 0, 'CDTBTC': 0, 'CMTBTC': 0, 'CNDBTC': 0, 'DGDBTC': 0, 'DLTBTC': 0, 'DNTBTC': 0, 'EDOBTC': 0, 'ELFBTC': 0, 'ENGBTC': 0, 'ENJBTC': 0, 'EOSBTC': 0, 'EVXBTC': 0, 'FUELBTC': 0, 'FUNBTC': 0, 'GASBTC': 0, 'GTOBTC': 0, 'GVTBTC': 0, 'GXSBTC': 0, 'HSRBTC': 0, 'ICNBTC': 0, 'ICXBTC': 0, 'IOTABTC': 0, 'KMDBTC': 0, 'KNCBTC': 0, 'LENDBTC': 0, 'LINKBTC': 0, 'LRCBTC': 0, 'LSKBTC': 0, 'LUNBTC': 0, 'MANABTC': 0, 'MCOBTC': 0, 'MDABTC': 0, 'MODBTC': 0, 'MTHBTC': 0, 'MTLBTC': 0, 'NAVBTC': 0, 'NEBLBTC': 0, 'NEOBTC': 0, 'NULSBTC': 0, 'OAXBTC': 0, 'OMGBTC': 0, 'OSTBTC': 0, 'POEBTC': 0, 'POWRBTC': 0, 'PPTBTC': 0, 'QSPBTC': 0, 'RCNBTC': 0, 'RDNBTC': 0, 'REQBTC': 0, 'SALTBTC': 0, 'SNGLSBTC': 0, 'SNMBTC': 0, 'SNTBTC': 0, 'STORJBTC': 0, 'STRATBTC': 0, 'SUBBTC': 0, 'TNBBTC': 0, 'TNTBTC': 0, 'TRIGBTC': 0, 'TRXBTC': 0, 'VENBTC': 0, 'VIBBTC': 0, 'VIBEBTC': 0, 'WABIBTC': 0, 'WAVESBTC': 0, 'WINGSBTC': 0, 'WTCBTC': 0, 'XVGBTC': 0, 'XZCBTC': 0, 'YOYOBTC': 0, 'ZRXBTC': 0}



#the modified cumulative volume over a period (a negative percent change will result in the volume change being counted as negative towards the
# cumulative volume stored here
modifiedVolume = {'BTCUSDT': 0.0, 'XRPBTC': 0.0,
                'ETHBTC': 0.0, 'BCCBTC': 0.0,
                'LTCBTC': 0.0, 'DASHBTC': 0.0,
                'XMRBTC': 0.0, 'QTUMBTC': 0.0, 'ETCBTC': 0.0,
                'ZECBTC': 0.0, 'ADABTC': 0.0, 'ADXBTC': 0.0, 'AIONBTC' : 0.0, 'AMBBTC': 0.0, 'APPCBTC': 0.0, 'ARKBTC': 0.0, 'ARNBTC': 0.0, 'ASTBTC': 0.0, 'BATBTC': 0.0, 'BCDBTC': 0.0, 'BCPTBTC': 0.0, 'BNBBTC': 0.0, 'BNTBTC': 0.0, 'BQXBTC': 0.0, 'BRDBTC': 0.0, 'BTSBTC': 0.0, 'CDTBTC': 0.0, 'CMTBTC': 0.0, 'CNDBTC': 0.0, 'DGDBTC': 0.0, 'DLTBTC': 0.0, 'DNTBTC': 0.0, 'EDOBTC': 0.0, 'ELFBTC': 0.0, 'ENGBTC': 0.0, 'ENJBTC': 0.0, 'EOSBTC': 0.0, 'EVXBTC': 0.0, 'FUELBTC': 0.0, 'FUNBTC': 0.0, 'GASBTC': 0.0, 'GTOBTC': 0.0, 'GVTBTC': 0.0, 'GXSBTC': 0.0, 'HSRBTC': 0.0, 'ICNBTC': 0.0, 'ICXBTC': 0.0, 'IOTABTC': 0.0, 'KMDBTC': 0.0, 'KNCBTC': 0.0, 'LENDBTC': 0.0, 'LINKBTC': 0.0, 'LRCBTC': 0.0, 'LSKBTC': 0.0, 'LUNBTC': 0.0, 'MANABTC': 0.0, 'MCOBTC': 0.0, 'MDABTC': 0.0, 'MODBTC': 0.0, 'MTHBTC': 0.0, 'MTLBTC': 0.0, 'NAVBTC': 0.0, 'NEBLBTC': 0.0, 'NEOBTC': 0.0, 'NULSBTC': 0.0, 'OAXBTC': 0.0, 'OMGBTC': 0.0, 'OSTBTC': 0.0, 'POEBTC': 0.0, 'POWRBTC': 0.0, 'PPTBTC': 0.0, 'QSPBTC': 0.0, 'RCNBTC': 0.0, 'RDNBTC': 0.0, 'REQBTC': 0.0, 'SALTBTC': 0.0, 'SNGLSBTC': 0.0, 'SNMBTC': 0.0, 'SNTBTC': 0.0, 'STORJBTC': 0.0, 'STRATBTC': 0.0, 'SUBBTC': 0.0, 'TNBBTC': 0.0, 'TNTBTC': 0.0, 'TRIGBTC': 0.0, 'TRXBTC': 0.0, 'VENBTC': 0.0, 'VIBBTC': 0.0, 'VIBEBTC': 0.0, 'WABIBTC': 0.0, 'WAVESBTC': 0.0, 'WINGSBTC': 0.0, 'WTCBTC': 0.0, 'XVGBTC': 0.0, 'XZCBTC': 0.0, 'YOYOBTC': 0.0, 'ZRXBTC': 0.0}


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


# EXPLANATION OF THE PARAMETERS

#PERCENT_QUANTITY_TO_SPEND: the amount of the balance calculated to be spent that we can spend (based on the small fee) #todo look more at why this exists
#PERCENT_TO_SPEND: the amount of the balance of bitcoin to spend. Should be calculated by how many bots are made
#MINIMUM_PERCENT_INCREASE: lowest percent increase for a cryptocurrency to be considered in the start of the bot
#MINIMUM_SCORE: the lowest score for a crypto to be addded to the list of scores to be checked for the remaineder of a run
#MINIMUM_MOVING_AVERAGE: the lowest moving average for a crypto score to be considered
#MAX_DECREASE: the maximum allowed decrease over a short (<15m) interval
#MAX_TIME_CYCLE: the maximum time the bot will run for in ticks (they are counted by a incrementing variable)
#MAX_CYCLES: the maximum amount of times the bot will buy and sell
#MAX_PERCENT_CHANGE: the highest % increase and the lowest % decrease a crypto can have over the life of owning it before an auto reevaluation
#NEGATIVE_WEIGHT: weight applied to negative percent price or percent volume change
#CUMULATIVE_PERCENT_CHANGE: the cumulative % change of a crypto's price over the course of owning it
#CUMULATIVE_PERCENT_CHANGE_STORE: the cumulative percent change over the course of owning several cryptos
#SLOT_WEIGHT: weight applied to each slot of the intervals being checked to see if they the crypto was increasing or decreasing
#TIME_INCREASING_MODIFIER: the unweighted time increasing modifier (time increasing is the count of intervals where the price was increasing)
#VOLUME_INCREASING_MODIFIER: the volume increasing modifier (volume increasing is the count of intervals where the volume traded increased)
#PERCENT_BY_HOUR_MODIFIER: the modifier for the total percent change of a crypto over a longer interval (> 1hr)
#VOLUME_PERCENT_BY_HOUR_MODIFIER: the modifier for the volume percent change over a longer interval (> 1hr)
#FLOOR_PRICE_MODIFIER: the lowest % change above the original price the crypto was bought at before the bot auto sells it (calculated later than the other failure conditions to catch a decreasing price)
#MODIFIED_VOLUME_MODIFIER: the cumulative volume change based on the % change by interval scale
#CUMULATIVE_PRICE_MODIFIER: the cumulative price change modifier for the weighted moving average
#PRIMARY_MODIFIED_VOLUME_SCALER: the scaler to make more volume traded have the same sign as the percent change in the price than the amount that is counted as having the opposite sign
#WAIT_FOR_CHECK_FAILURE: the number of ticks before the failure condition is checked (the crypto is decreasing over the past 10 minutes)
#WAIT_FOR_CHECK_TOO_LOW: the number of ticks before ethe program checks to see if a crypto has decreased too low to its starting point
#VARIATION_NUM: number stored for what variation on the bot this is, 0 base
#CLASS_NUM: number stored for the class, 0 means no class, 1 and up are the actual classes
#MINOFFSET: the number of minutes before the beginning of the interval of data that the bot can look back to
#INTERVAL_TO_TEST: the interval over which the bot will be tested (think hour, day, week etc...); used with the crypto evaluator
#MINUTES_IN_PAST: how far back you want the end point of the test to be
#START_MONEY: the amount of money in $ the bot starts with
#END_MONEY: the amount of money in $ the bot ends with

PARAMETERS = {'PERCENT_QUANTITY_TO_SPEND': 0.9, 'PERCENT_TO_SPEND': 1.0, 'MINIMUM_PERCENT_INCREASE': 5.0, 'MINIMUM_SCORE': 0.01, 'MINIMUM_MOVING_AVERAGE': .001, 'MAX_DECREASE': -10.0, 'MAX_TIME_CYCLE': 60.0, 'MAX_CYCLES': 24, 'MAX_PERCENT_CHANGE': 100.0, 'NEGATIVE_WEIGHT': 1.0, 'CUMULATIVE_PERCENT_CHANGE': 0.0, 'CUMULATIVE_PERCENT_CHANGE_STORE': 0.0, 'SLOT_WEIGHT': 1.0, 'TIME_INCREASING_MODIFIER': 1.0, 'VOLUME_INCREASING_MODIFIER': 1.0, 'PERCENT_BY_HOUR_MODIFIER': 1.0, 'VOLUME_PERCENT_BY_HOUR_MODIFIER': 1.0, 'FLOOR_PRICE_MODIFIER': 1.005, 'MODIFIED_VOLUME_MODIFIER': 1.0, 'CUMULATIVE_PRICE_MODIFIER': 1.0, 'PRIMARY_MODIFIED_VOLUME_SCALER': 1.0, 'WAIT_FOR_CHECK_FAILURE': 5.0, 'WAIT_FOR_CHECK_TOO_LOW': 10.0, 'VARIATION_NUMBER': 0.0, 'CLASS_NUM': -1, 'MIN_OFFSET': 120.0, 'INTERVAL_TO_TEST': 1440.0, 'MINUTES_IN_PAST': 0.0, 'START_MONEY': 100, 'END_MONEY': 0}

#get the balance in bitcoins
def getBalance(symbol):
    """
    :param symbol:
    :return:
    """
    timestamp = int(time.time() * 1000)
    # building the request query url plus other parameters(signed)
    headers = {'X-MBX-APIKEY': api_key}
    infoParameter = {'timestamp': timestamp}
    query = urlencode(sorted(infoParameter.items()))
    signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    query += "&signature=" + signature

    # requesting account info to get the balance
    accountInfo = requests.get("https://api.binance.com/api/v3/account?" + query, headers=headers)
    accountInfo = accountInfo.json()["balances"]

    balance = 0

    for val in accountInfo:
        if(val["asset"] == symbol):
            balance = val["free"]

    return balance

#buy the specified crypto currency

def buyBin(symbol):
    """
    :param symbol:
    :return:
    """

    global priceBought

    timestamp = int(time.time() * 1000)
    balance = getBalance('BTC')

    #multiply balance by constant ratio of how much we want to spend
    # and then convert quantity from BTC price to amount of coin
    balancetospend = float(balance) * PARAMETERS['PERCENT_TO_SPEND']
    ratio = getbinanceprice(symbol)

    #store the price the crypto was a bought at for cumulative percent change calculations
    priceBought = ratio


    #mark item as the current crypto being traded and save the buy price at for failure condition
    entry = {symbol:{'buyPrice': ratio, 'timestamp': timestamp}}
    currencyToTrade.clear()
    currencyToTrade.update(entry)
    quantity = balancetospend / float(ratio) * float(PARAMETERS['PERCENT_QUANTITY_TO_SPEND'])

    # set the step size for the given coin
    stepsize = stepsizes[symbol]

    # making the quantity to buy
    print("Balance of {}: {}".format(symbol, balance))
    file.write("Balance of {}: {}\n".format(symbol, balance))
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

    print('Quantity to buy: {} of {}'.format(quantity, symbol))
    file.write('Quantity to buy: {} of {} \n'.format(quantity, symbol))

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


#sell the specified crypto
def sellBin(symbol):
    """
    :param symbol:
    :return:
    """

    #current time in ms
    timestamp = int(time.time() * 1000) - 1000

    #building the request query url plus other parameters(signed)
    headers = {'X-MBX-APIKEY': api_key}
    infoParameter = {'timestamp': timestamp}
    query = urlencode(sorted(infoParameter.items()))
    signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    query += "&signature=" + signature

    #getting the account info
    accountInfo = requests.get("https://api.binance.com/api/v3/account?" + query, headers=headers)


    #getting rid of the 'BTC' part of the crypto asset name
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

    #making the quantity to sell
    print("Balance of (): " + str(balance))
    file.write("Balance of (): " + str(balance) + "\n")
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

    print('Quantity to sell: {} of {}'.format(quantity, symbol))
    file.write('Quantity to sell: {} of {} \n'.format(quantity, symbol))

    #building the sell query string
    sellParameters = {'symbol': symbol, 'side': 'sell', 'type': 'market', 'timestamp': timestamp, 'quantity': quantity}
    query = urlencode(sorted(sellParameters.items()))
    signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    query += "&signature=" + signature

    #actually selling
   # testSell = requests.post("https://api.binance.com/api/v3/order?" + query, headers=headers)
   # print(testSell.text)
   # file.write(testSell.text + "\n")

#get the binance step sizes of each crypto (the step size is the minimum significant digits allowed by binance for crypto to be traded in)
def binStepSize():
    """
    :return:
    """
    #getting the dictionary of a lot of aggregate data for all symbols
    stepsizeinfo = requests.get("https://api.binance.com/api/v1/exchangeInfo")
    bigdata = stepsizeinfo.json()["symbols"]

    #iterating through the dictionary and adding just the stepsizes into our own dictionary
    for i in bigdata:
        symbol = i["symbol"]
        stepsize = i["filters"][1]["stepSize"]
        temp = {symbol: stepsize}
        stepsizes.update(temp)


#todo add in a weight
#calculates the weighted moving average over the specified interval for a crypto currency

def setWeightedMovingAverage(currency, interval, starttime, endtime):
    """
    :param currency:
    :param interval:
    :param starttime:
    :param endtime:
    :return:
    """

    cumulativePrice = 0.0

    parameters = {"symbol": currency, "interval": interval, 'startTime': starttime, 'endTime': endtime}
    data = requests.get("https://api.binance.com/api/v1/klines", params=parameters)
    data = data.json()
    data.reverse()

    slots = getLastSlot(interval, starttime, endtime) + 1

    if data == []:
        return 0

    #adds up the cumulative price changes using each interval
    for value in data:
       startPrice = value[1]
       endPrice = value[4]
       change = calcPercentChange(startPrice, endPrice)

       cumulativePrice += change

    #the scaling of the cumulative price
    cumulativePrice = (cumulativePrice / slots) * PARAMETERS['CUMULATIVE_PRICE_MODIFIER']



    return cumulativePrice

# this function will update the weighted moving average every second the program runs todo
# def updateWeightedMovingAverage(currency, interval, starttime, endtime):


#gets the cumulative volume over a period and scales it based on the currency's price
def getVolume(interval, starttime, endtime, currency):
    """
    :param interval:
    :param starttime:
    :param endtime:
    :param currency:
    :return:
    """

    slots = 0
    volume = 0

    #building the request
    parameters = {"symbol": currency, "interval": interval, 'startTime': starttime, 'endTime': endtime}
    data = requests.get("https://api.binance.com/api/v1/klines", params=parameters)
    data = data.json()
    data.reverse()

    #adds up all the volumes over the interval
    for value in data:
        slots += 1
        volume += int(float(value[5]))

    #scales the volume by the price of the crypto currency
    volume *= float(getbinanceprice(currency))
    return volume


#grabs the list of volumes over the interval and percent changes over the interal
#then interates through and calculates a cumulative volume where the volume is considered negative
#when the percent change was negative and positive when the percent change was positive
def getModifiedVolume(currency):
    """
    :param currency:
    :return:
    """

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


        #NOTE: can change back to normal if this doesnt work
        if(percentChangesList[currentSlot] < 0):

            oldVolume += float(i) * (percentChangeScale) * float(PARAMETERS['NEGATIVE_WEIGHT'])

            oldVolume += -1 * (1/3) * (float(i) * ( ( percentChangeScale)) * float(PARAMETERS['PRIMARY_MODIFIED_VOLUME_SCALER']))

        if(percentChangesList[currentSlot] > 0):

            oldVolume += float(i) * ((percentChangeScale) * float(PARAMETERS['PRIMARY_MODIFIED_VOLUME_SCALER']))

            oldVolume += (-1/3) * (float(i) *( percentChangeScale)) * float(PARAMETERS['NEGATIVE_WEIGHT'])

        currentSlot += 1


    return float(oldVolume)

#get the binance price of the specified currency
def getbinanceprice(currency):
    """
    :param currency:
    :return:
    """
    #getting the aggregate trade data and finding one price to return
    parameters = {'symbol': currency}
    binData = requests.get("https://api.binance.com/api/v3/ticker/price", params= parameters)
    binData = binData.json()
    binPrice = binData['price']
    return binPrice


def resetValues():
    """
    :return:
    """
    #reset the list of parameter value that are calculated below
    for key, value in values.items():
        values[key] = []

    #interval based on this from binance API
    #     m -> minutes;     h -> hours;     d -> days;     w -> weeks;    M -> months
    #  1m  3m   5m  15m  30m  1h 2h 4h 6h 8h  12h  1d   3d  1w   1M
    # method used to update price lists on past hour of trends

#method to iterate through all the cryptos available on binance and store their price changes, percent price changes,
#volume changes, percent volume changes, scores, time increasing, and time decreasing
def updateCrypto(interval, starttime, endtime):
    """
    :param interval:
    :param starttime:
    :param endtime:
    :return:
    """

    resetValues()

    for key,currencyname in priceSymbols.items():
        print(key)
        parameter = {'symbol': currencyname, 'interval': interval, 'startTime': starttime, 'endTime': endtime}
        percentChange = requests.get("https://api.binance.com/api/v1/klines", params=parameter)
        percentChange = percentChange.json()
        percentChange.reverse()

        lastSlot = getLastSlot(interval, starttime, endtime)

        if percentChange == []:
            lastSlot = 0

        #calculate the percent change over the whole hour and store
        openPrice = percentChange[0][1]
        closePrice = percentChange[int(lastSlot)][4]

        pricePercentData[currencyname]['percentbyhour'] = calcPercentChange(openPrice, closePrice)

        # store percent by hour changes to be used later for scaling
        values['PERCENT_BY_HOUR'].append(pricePercentData[currencyname]['percentbyhour'])

        #used to scale the volume
        priceScale = float(getbinanceprice(currencyname))

        #calcualte the percent change in volume over the whole hour and store
        openVolume = float(percentChange[0][5]) * priceScale
        closeVolume = float(percentChange[int(lastSlot)][5]) * priceScale
        volumePercentData[currencyname]['percentbyhour'] = calcPercentChange(openVolume, closeVolume)

        # store the volume change by hour to be used later for scaling
        values['VOLUME_BY_HOUR'].append(volumePercentData[currencyname]['percentbyhour'])

        #calculate the percentage change between the minute intervals and store
        #reset the list of stored percentages so a fresh list is stored
        percentChanges[currencyname][:] = []
        for i in percentChange:
            percentChanges[currencyname].append(calcPercentChange(i[1], i[4]))



        #reset the lists of the volume amounts and volume percent changes
        volumeAmounts[currencyname][:] = []
        volumePercentChanges[currencyname][:] = []

        #grabs and stores the volume from the first two intervals that are skipped in the for loop below
        volumeAmounts[currencyname].append(float(percentChange[0][5]) * priceScale)
        volumeAmounts[currencyname].append(float(percentChange[1][5]) * priceScale)



        #stores the volume percent changes and the volume amounts
        for i in range(2, len(percentChange)):
           volumePercentChanges[currencyname].append(calcPercentChange(float(percentChange[i-1][5]) * priceScale, float(percentChange[i][5]) * priceScale))
           volumeAmounts[currencyname].append(float(percentChange[i][5]) * priceScale)

        #calculate and store the percent time increasing for volume and price percent changes
        pricePercentData[currencyname]['timeIncreasing'] = getTimeIncreasing(0, currencyname)
        pricePercentData[currencyname]['weightedtimeIncreasing'] = getTimeIncreasing(1, currencyname)

        # store the time increasing and weighted time increasing for price data to be used for scaling
        values['TIME_INCREASING'].append(pricePercentData[currencyname]['timeIncreasing'])
        values['WEIGHTED_TIME_INCREASING'].append(pricePercentData[currencyname]['weightedtimeIncreasing'])

        # calcualte and store time increasing for volume and price percent changes
        volumePercentData[currencyname]['timeIncreasing'] = getVolumeTimeIncreasing(0, currencyname)
        volumePercentData[currencyname]['weightedtimeIncreasing'] = getVolumeTimeIncreasing(1, currencyname)

        # store the time increasing and weighted time increasing for volume data to be used for scaling
        values['VOLUME_TIME_INCREASING'].append(volumePercentData[currencyname]['timeIncreasing'])
        values['WEIGHTED_VOLUME_TIME_INCREASING'].append(volumePercentData[currencyname]['weightedtimeIncreasing'])

        modifiedVolume[currencyname] = 0.0
        #get the modified volume changes
        modifiedVolume[currencyname] = getModifiedVolume(currencyname)
        values['MODIFIED_VOLUME'].append(modifiedVolume[currencyname])

        #calcualte a weightedMovingAverage
        endtt = int(time.time() * 1000)
        startt = endtt - intervalTypes['4h']['inMS']
        weightedMovingAverage[currencyname] = setWeightedMovingAverage(currencyname, intervalTypes['1m']['symbol'], startt, endtt)

    setMaxValue()

    resetValues()


    #gets the score for each crypto
    #moved to its own loop so all the values can be properly scaled by the largest value
    for key, currencyname in priceSymbols.items():
        # use the calculations to get a score
        calc_score = getScore(currencyname)
        new_score = {currencyname: calc_score}
        scores.update(new_score)
        values['SCORE'].append(calc_score)

    #add currencies to a list of cryptos to pick from if it meets the minimum score
    for key, value in scores.items():
        if(value > PARAMETERS['MINIMUM_SCORE']):
            entry = {key: value}
            currencyToTrade.update(entry)

    print ("OUR LIST OF CRYPTO: ")
    print(currencyToTrade)
    file.write("OUR LIST OF CRYPTO: ")
    file.write(str(currencyToTrade))

#caclulates and returns the time spent increasing
#weighted = 0 is false, weighted = 1 is true
# TODO update the modulo so that it is a modulo not a multiplcation so that
#patterns are detected
def getTimeIncreasing(isWeighted, currency):
    """
    :param isWeighted:
    :param currency:
    :return:
    """
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
              slots_increasing += 1 * i * float(PARAMETERS['NEGATIVE_WEIGHT'])

            if float(i) > 0.0 and isWeighted == 1:
              slots_increasing+=(1*(slots * float(PARAMETERS['SLOT_WEIGHT']))*i)


            if float(i) < 0.0 and isWeighted == 1:
              slots_increasing += (1*(slots * float(PARAMETERS['SLOT_WEIGHT']))*i * float(PARAMETERS['NEGATIVE_WEIGHT']))



    return (slots_increasing/slots) * PARAMETERS['TIME_INCREASING_MODIFIER']


#caclulates and returns the time spent increasing for volume
#weighted = 0 is false, weighted = 1 is true
def getVolumeTimeIncreasing(isWeighted, currency):
    """
    :param isWeighted:
    :param currency:
    :return:
    """

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


    return (slots_increasing/slots) * float(PARAMETERS['VOLUME_INCREASING_MODIFIER'])

# method to calculate the "score" that crypto get when they are updated by hour
# score is a combination of weighted time increasing and % change over hour.
# for both volume and price
def getScore(symbol):
    """
    :param symbol:
    :return:
    """

    new_score = 0


    #setting up the scaled values for checking
    values['VOLUME_BY_HOUR'].append(volumePercentData[symbol]['percentbyhour'] / maxValues['VOLUME_BY_HOUR'])
    values['PERCENT_BY_HOUR'].append(((pricePercentData[symbol]['percentbyhour']) / maxValues['PERCENT_BY_HOUR']))
    values['TIME_INCREASING'].append(pricePercentData[symbol]['timeIncreasing'] / maxValues['TIME_INCREASING'])
    values['VOLUME_TIME_INCREASING'].append(volumePercentData[symbol]['timeIncreasing'] / maxValues['TIME_INCREASING'])
    values['WEIGHTED_TIME_INCREASING'].append((pricePercentData[symbol]['weightedtimeIncreasing'] / maxValues['WEIGHTED_TIME_INCREASING']))
    values['WEIGHTED_VOLUME_TIME_INCREASING'].append((volumePercentData[symbol]['weightedtimeIncreasing'] / maxValues['WEIGHTED_VOLUME_TIME_INCREASING']))
    values['MODIFIED_VOLUME'].append((modifiedVolume[symbol] / maxValues['MODIFIED_VOLUME']))



    new_score += (volumePercentData[symbol]['percentbyhour']/ maxValues['VOLUME_BY_HOUR']) * PARAMETERS['VOLUME_PERCENT_BY_HOUR_MODIFIER']
    new_score += ((pricePercentData[symbol]['percentbyhour']) / maxValues['PERCENT_BY_HOUR']) * PARAMETERS['PERCENT_BY_HOUR_MODIFIER']
    new_score += (pricePercentData[symbol]['weightedtimeIncreasing'] /maxValues['WEIGHTED_TIME_INCREASING'])
    new_score += (volumePercentData[symbol]['weightedtimeIncreasing'] / maxValues['WEIGHTED_VOLUME_TIME_INCREASING'])
    new_score += (modifiedVolume[symbol] / maxValues['MODIFIED_VOLUME']) * PARAMETERS['MODIFIED_VOLUME_MODIFIER']

    return new_score


#finds the next currency to buy
def priceChecker():
    """
    :return:
    """

    currencyToBuy = ''
    #Compares the two price lists and sets the currencyToBuy to be
    # the coin with the highest score that also is above the minimum moving average
    maxScore = 0
    for key, value in currencyToTrade.items():
        print("The score of {} is {} ".format(key, scores[key]))
        file.write("The score of {} is {} \n".format(key, scores[key]))
        print("The average was " + str(weightedMovingAverage[key]))

        if(maxScore < scores[key] and float(weightedMovingAverage[key]) > float(PARAMETERS['MINIMUM_MOVING_AVERAGE'])):
            maxScore = scores[key]
            print("CURRENT HIGH SCORE: The score of {} is {}".format(key, scores[key]))
            file.write("CURRENT HIGH SCORE: The score of {} is {} \n".format(key, scores[key]))
            currencyToBuy = key

    if currencyToBuy != '':
        print("Coin with the highest score is {} which is {}".format(currencyToBuy, maxScore))
        file.write("Coin with the highest score is {} which is {} \n".format(currencyToBuy, maxScore))

    if currencyToBuy == '':
        print("Did not buy. None qualified")
        file.write("Did not buy. None qualified")

    return currencyToBuy #potential runtime error if all negative todo


#just calculates the percent change between two values
def calcPercentChange(startVal, endVal):
    """
    :param startVal:
    :param endVal:
    :return:
    """

    if(float(startVal) == 0.0):
        return float(endVal) * 100.0

    return (((float(endVal) - float(startVal))/float(startVal) ) * 100)


#checks if the current crypto has been decreasing the past ten minutes
#if yes it forces a new check to see if there is a better crypto
def checkFailureCondition(currency, timesIncreasing):
    """
    :param currency:
    :param timesIncreasing:
    :return:
    """
    print("New Interval")
    file.write("New Interval")

    endTime = int(time.time()) * 1000
    startTime = endTime - (int(intervalTypes['5m']['inMS']) * 2)


    parameter = {'symbol': currency, 'interval': intervalTypes['1m']['symbol'], 'startTime': startTime, 'endTime': endTime}
    percentChange = requests.get("https://api.binance.com/api/v1/klines", params=parameter)
    percentChange = percentChange.json()
    percentChange.reverse()

    #get the starting price of the interval
    startPriceInterval = percentChange[0][1]
    timeIncreasingCounter = 0

    #iterate through the list of percent changes and add up when the percent change was positive
    for i in percentChange:
        startPrice = i[1]
        endPrice = i[4]

        print("Current Crypto: {} Start Price: {} End Price: {}".format(currency, startPrice, endPrice))
        file.write("Current Crypto: {} Start Price: {} End Price: {}\n".format(currency, startPrice, endPrice))
        percentChange = calcPercentChange(startPrice, endPrice)
        if(percentChange > 0):
            timeIncreasingCounter += 1


    intervalPercentChange = calcPercentChange(startPriceInterval, endPrice)
    print("Cumulative percent change over THIS INTERVAL {}".format(intervalPercentChange))
    file.write("Cumulative percent change over THIS INTERVAL {} \n".format(intervalPercentChange))
    print("Times Increasing over the interval: {}".format(timeIncreasingCounter))
    file.write("Times Increasing over the interval: {} \n".format(timeIncreasingCounter))

    if(timeIncreasingCounter <= timesIncreasing):
        print("DECREASED ALL INTERVALS. RESTART")
        file.write("DECREASED ALL INTERVALS. RESTART")
        return 1

    return 0

#checks whether the function has caused too large of negative decrease the specified interval
def checkTooNegative(symbol):
    """
    :param symbol:
    :return:
    """
    startTime = int(time.time()) * 1000 - 60000
    endTime = int(time.time()) * 1000

    parameter = {'symbol': symbol, 'interval': '1m', 'startTime': startTime, 'endTime': endTime}
    percentChange = requests.get("https://api.binance.com/api/v1/klines", params=parameter)
    percentChange = percentChange.json()
    percentChange.reverse()

    if (percentChange == []):
        return 0


    startPrice = percentChange[0][1]
    endPrice = percentChange[0][4]
    percentChange = calcPercentChange(startPrice, endPrice)

    if(percentChange < PARAMETERS['MAX_DECREASE']):
        print("TOO NEGATIVE. RESTART")
        file.write("TOO NEGATIVE. RESTART")
        return 1

    return 0

#checks to see if the currency has increased or decreased more than is allowed
# if yes, then the reevaluation process is restarted
def checkExitCondition(currency):
    """
    :param currency:
    :return:
    """
    global priceBought

    currentPrice= getbinanceprice(currency)

    percentChange = calcPercentChange(priceBought, currentPrice)

    if(percentChange >= PARAMETERS['MAX_PERCENT_CHANGE']):
        print("HIT MAX PERCENT CHANGE")
        return 1

    if(percentChange <= -1 * PARAMETERS['MAX_PERCENT_CHANGE']):
        print("HIT MINIMUM PERCENT CHANGE")
        return 1

    return 0

#checks to see if the current currency is too near to its starting point
def checkTooLow(currency, timesIncreasing):
    """
    :param currency:
    :param timesIncreasing:
    :return:
    """
    global priceBought

    currentPrice = getbinanceprice(currency)
    floorPrice = float(PARAMETERS['FLOOR_PRICE_MODIFIER']) * float(priceBought)
    endtime = int(time.time() * 1000)
    starttime = endtime - intervalTypes['15m']['inMS']

    direction = increasingOrDecreasing(currency, intervalTypes['15m']['symbol'], starttime, endtime)
    allIntervalsDecreasing = checkFailureCondition(currency, timesIncreasing)

    #check to see if the current price is too low, the crypto is decreasing over the past 15 minutes
    #and all the intervals are decreasing
    if(float(currentPrice) < float(floorPrice) and direction == 0 & allIntervalsDecreasing == 1):
        print("WAS TOO LOW")
        return 1

    return 0

#calculates and returns the last slot of an array or list based on the interval, starttime, and endtime
def getLastSlot(interval, starttime, endtime):
    """
    :param interval:
    :param starttime:
    :param endtime:
    :return:
    """
    difference = endtime - starttime
    intervalInMs = intervalTypes[interval]['inMS']

    if(difference == 0):
        return 0

    numIntervals = difference/intervalInMs


    return numIntervals - 1

#returns whether the specified currency is increasing or decreasing over the interval
# 0 means decreasing, 1 means stable or increasing
def increasingOrDecreasing(currency, interval, starttime, endtime):
    """
    :param currency:
    :param interval:
    :param starttime:
    :param endtime:
    :return:
    """

    lastSlot = getLastSlot(interval, starttime, endtime)

    parameter = {'symbol': currency, 'interval': interval, 'startTime': starttime, 'endTime': endtime}
    percentChange = requests.get("https://api.binance.com/api/v1/klines", params=parameter)
    percentChange = percentChange.json()

    if percentChange == []:
        return 0

    #all binance lists come in reverse chronological order so they must be reversed
    percentChange.reverse()

    #grabbing start and end price and calcualting the percent change over the entire period
    startPrice = percentChange[0][1]
    endPrice = percentChange[int(lastSlot)][4]
    calcPChange = calcPercentChange(startPrice, endPrice)

    if(calcPChange >= 0.0):
        return 1

    return 0


# function just resets parameters to the best stored parameters
def resetParameters(paramDict):
    """
    :param paramDict:
    :return:
    """
    valList = []
    count = 0
    file.seek(0)

    for line in file:
        val = line.split(': ')[1]
        trueVal = val.split(',')[0]
        trueVal = float(trueVal)
        valList.append(trueVal)

    for key, value in paramDict.items():
        paramDict[key] = valList[count]
        count += 1

#runs through the values collected and storess the max value
def setMaxValue():
    """
    :return:
    """
    for key, value in values.items():
        currentMaxVal = 0

        for i in values[key]:
            if i > currentMaxVal or currentMaxVal == 0:
                maxValues[key] = i
                currentMaxVal = i

    print("THE VALUES {}".format(values))
    print("THE MAX {}".format(maxValues))

def main():
    global CUMULATIVE_PERCENT_CHANGE
    global initialBalance
    global RESTART
    global RESTART_TN
    global RESTART_LOW
    global EXIT
    global pricesold
    global TESTING

    currentCurrency = ''
    x = 0

    #creates a statistic object to record the different decisions and then analyze them
    cryptoRunStats = CryptoStatAnalysis.CryptoStatsAnalysis(0, 0, 'NT')

    info = requests.get("https://api.binance.com/api/v1/exchangeInfo")
    print(info.text)

    file.write("\n\n\n\n")
    file.write('------------------------------------------------------------------------------------ \n')

    print("Date and Time of Run {}".format(datetime.datetime.now()))
    file.write("Date and Time of Run {} \n".format(datetime.datetime.now()))


    initialBalance = getBalance('BTC')
    if(TESTING == 0):
        resetParameters(PARAMETERS)
    binStepSize()
    while(x < PARAMETERS['MAX_CYCLES'] and EXIT == 0):
        t = 0
        RESTART = 0
        RESTART_LOW = 0
        RESTART_TN = 0

        tiempo = requests.get("https://api.binance.com/api/v1/time")
        tiempo = tiempo.json()
        tiempo = tiempo["serverTime"]
        endTime = tiempo
        startTime = tiempo - 3600000

        #calcualates the scores of the cryptos over the past hour using 5 minute intervals
        updateCrypto(intervalTypes['5m']['symbol'], startTime, endTime)
        print("We back")

        oldCurrency = currentCurrency
        currentCurrency = priceChecker()

        print("Curr currency main " + str(currentCurrency))


        if(oldCurrency != currentCurrency and oldCurrency != '' ):

            pricesold = getbinanceprice(currentCurrency)

            sellBin(oldCurrency)

            print('Price bought: {} Price sold: {} '.format(priceBought, pricesold))
            file.write('Price bought: {} Price sold: {} \n'.format(priceBought, pricesold))

            cumulativePercentChange = calcPercentChange(priceBought, pricesold)
            PARAMETERS['CUMULATIVE_PERCENT_CHANGE'] = cumulativePercentChange
            PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE'] += cumulativePercentChange

            print("FINAL percent change over the life of owning this crypto " + str(PARAMETERS['CUMULATIVE_PERCENT_CHANGE']))
            file.write("FINAL percent change over the life of owning this crypto " + str(PARAMETERS['CUMULATIVE_PERCENT_CHANGE']))

            print("THIS RUN SOLD AT: {}".format(datetime.datetime.time(datetime.datetime.now())))
            file.write("THIS RUN SOLD AT: {} \n".format(datetime.datetime.time(datetime.datetime.now())))



        if(oldCurrency != currentCurrency and currentCurrency != ''):
            buyBin(currentCurrency)
            print("THIS RUN BOUGHT AT: {}".format(datetime.datetime.time(datetime.datetime.now())))
            file.write("THIS RUN BOUGHT AT: {}".format(datetime.datetime.time(datetime.datetime.now())))

        #while statement is more flexible way to wait for a period of time or a restart
        # restart could be caused by a met failure condition or a met sustained one
        while(t < PARAMETERS['MAX_TIME_CYCLE'] and RESTART == 0 and RESTART_TN == 0 and RESTART_LOW == 0 and currentCurrency != ''):
            time.sleep(1)

            if(t % PARAMETERS['WAIT_FOR_CHECK_FAILURE'] == 0 and t != 0):
                RESTART = checkFailureCondition(currentCurrency, 0)

            if(t > PARAMETERS['WAIT_FOR_CHECK_TOO_LOW'] and t % PARAMETERS['WAIT_FOR_CHECK_FAILURE']):
                print("Curr currency " + str(currentCurrency))
                RESTART_LOW = checkTooLow(currentCurrency, 1)

            RESTART_TN = checkTooNegative(currentCurrency)
            t+=1

        if(oldCurrency == currentCurrency and currentCurrency != ''):
            newPrice = getbinanceprice(currentCurrency)
            cumulativePercentChange = calcPercentChange(priceBought, newPrice)
            PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE'] += cumulativePercentChange
            priceBought = newPrice

        #just wait 300 seconds before running through again if no crypto was chosen
        if currentCurrency == '' or (currentCurrency == oldCurrency):
           time.sleep(300)


        if currentCurrency != '':
            EXIT = checkExitCondition(currentCurrency)
        x+=1


    print("Cumualtive percent change over the life of all cryptos owneed so far {}".format(PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE']))
    file.write("Cumualtive percent change over the life of all cryptos owneed so far {} \n".format(PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE']))
    sellBin(currentCurrency)


    file.write('---------------------------||||||||||||||||----------------------------------------' + "\n")
    file.write("\n" + "\n" + "\n")

    file.close()



if __name__ == "__main__":
    main()

