# Copyright (c) 2018 A&D
# Auto trading bot that uses parameters sent by CryptoTrainer to test them

import requests
import hmac
import hashlib
import time
import math
import datetime
import os.path
import CryptoStats
from multiprocessing import Pool
from PrivateData import api_key, secret_key
from CryptoTrainer import PARAMETERS
from CryptoStats import getOpenPrice, getClosePrice, getVolume
try:
    from urlib import urlencode

except ImportError:
    from urllib.parse import urlencode


#todo find a way to get the parameters specific to this run from CrytpoTrainer
#todo add function to pull data from text files by day into data structures here

#Directory path (r makes this a raw string so the backslashes do not cause a compiler issue
#logPaths = r'C:\Users\katso\Documents\GitHub\Crypto\Logs'
drewlogPath = r'C:\Users\DrewG\Documents\GitHub\Crypto\Logs'

#log file name + path
#logCompletePath = os.path.join(logPaths, "log.txt")
drewlogCompletePath = os.path.join(drewlogPath, "log.txt")
testlogPath = os.path.join(drewlogPath, "testlog.txt")
#open a file for appending (a). + creates file if does not exist
file = open(drewlogCompletePath, "a+")
test = open(testlogPath, "w")

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
modifiedVolume = {'BTCUSDT': [], 'XRPBTC': [],
                'ETHBTC': [], 'BCCBTC': [],
                'LTCBTC': [], 'DASHBTC': [],
                'XMRBTC': [], 'QTUMBTC': [], 'ETCBTC': [],
                'ZECBTC': [], 'ADABTC': [], 'ADXBTC': [], 'AIONBTC' : [], 'AMBBTC': [], 'APPCBTC': [], 'ARKBTC': [], 'ARNBTC': [], 'ASTBTC': [], 'BATBTC': [], 'BCDBTC': [], 'BCPTBTC': [], 'BNBBTC': [], 'BNTBTC': [], 'BQXBTC': [], 'BRDBTC': [], 'BTSBTC': [], 'CDTBTC': [], 'CMTBTC': [], 'CNDBTC': [], 'CTRBTC': [], 'DGDBTC': [], 'DLTBTC': [], 'DNTBTC': [], 'EDOBTC': [], 'ELFBTC': [], 'ENGBTC': [], 'ENJBTC': [], 'EOSBTC': [], 'EVXBTC': [], 'FUELBTC': [], 'FUNBTC': [], 'GASBTC': [], 'GTOBTC': [], 'GVTBTC': [], 'GXSBTC': [], 'HSRBTC': [], 'ICNBTC': [], 'ICXBTC': [], 'IOTABTC': [], 'KMDBTC': [], 'KNCBTC': [], 'LENDBTC': [], 'LINKBTC': [], 'LRCBTC': [], 'LSKBTC': [], 'LUNBTC': [], 'MANABTC': [], 'MCOBTC': [], 'MDABTC': [], 'MODBTC': [], 'MTHBTC': [], 'MTLBTC': [], 'NAVBTC': [], 'NEBLBTC': [], 'NEOBTC': [], 'NULSBTC': [], 'OAXBTC': [], 'OMGBTC': [], 'OSTBTC': [], 'POEBTC': [], 'POWRBTC': [], 'PPTBTC': [], 'QSPBTC': [], 'RCNBTC': [], 'RDNBTC': [], 'REQBTC': [], 'SALTBTC': [], 'SNGLSBTC': [], 'SNMBTC': [], 'SNTBTC': [], 'STORJBTC': [], 'STRATBTC': [], 'SUBBTC': [], 'TNBBTC': [], 'TNTBTC': [], 'TRIGBTC': [], 'TRXBTC': [], 'VENBTC': [], 'VIBBTC': [], 'VIBEBTC': [], 'WABIBTC': [], 'WAVESBTC': [], 'WINGSBTC': [], 'WTCBTC': [], 'XVGBTC': [], 'XZCBTC': [], 'YOYOBTC': [], 'ZRXBTC': []}


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

#number of minutes we want to iterate backwards
minutesBack = 0

#get the balance in bitcoins
def getBalance(symbol):
    '''
    timestamp = int(time.time() * 1000) - 2000
    # building the request query url plus other parameters(signed)
    headers = {'X-MBX-APIKEY': api_key}
    infoParameter = {'timestamp': timestamp}
    query = urlencode(sorted(infoParameter.items()))
    signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    query += "&signature=" + signature

    # requesting account info to get the balance
    accountInfo = requests.get("https://api.binance.com/api/v3/account?" + query, headers=headers)
    #print(str(accountInfo.text))
    accountInfo = accountInfo.json()["balances"]

    balance = 0

    for val in accountInfo:
        if(val["asset"] == symbol):
            balance = val["free"]

    return balance
    '''
#buy the specified crypto currency
def buyBin(symbol):
    global priceBought
    '''
    timestamp = int(time.time() * 1000)
    balance = getBalance('BTC')
    
    #multiply balance by constant ratio of how much we want to spend
    # and then convert quantity from BTC price to amount of coin
    balancetospend = float(balance) * PARAMETERS['PERCENT_TO_SPEND']
    ratio = getbinanceprice(symbol)

    #store the price the crypto was a bought at for cumulative percent change calculations
    priceBought = ratio
    '''

    #mark item as the current crypto being traded and save the buy price at for failure condition
    entry = {symbol:{'buyPrice': ratio, 'timestamp': timestamp}}
    currencyToTrade.clear()
    currencyToTrade.update(entry)
    '''
    
    quantity = balancetospend / float(ratio) * PARAMETERS['PERCENT_QUANTITY_TO_SPEND']
    
    
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
    '''

#sell the specified crypto
def sellBin(symbol):
    '''
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
    '''
    #building the sell query string
    #sellParameters = {'symbol': symbol, 'side': 'sell', 'type': 'market', 'timestamp': timestamp, 'quantity': quantity}
    #query = urlencode(sorted(sellParameters.items()))
    #signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    q#uery += "&signature=" + signature

    #actually selling
   # testSell = requests.post("https://api.binance.com/api/v3/order?" + query, headers=headers)
   # print(testSell.text)
   # file.write(testSell.text + "\n")

#get the binance step sizes of each crypto (the step size is the minimum significant digits allowed by binance for crypto to be traded in)
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


#add in the weight todo

#calculates the weighted moving average over the specified interval for a crypto currency

def setWeightedMovingAverage(currency, minutesBack):
    cumulativePrice = 0.0

    openPriceData = CryptoStats.getOpenPrice[currency]
    closePriceData = CryptoStats.getClosePrice[currency]

    slots = getLastSlot(interval, starttime, endtime) + 1

    if data == []:
        return 0

    #adds up the cumulative price changes using each interval
    for x in range (0, minutesBack-1):
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
def getVolume(currency, minutesBack):
    slots = 0
    volume = 0

    #building the request
    data = CryptoStats.getVolume()[currency]
    #adds up all the volumes over the interval
    for x in range (0, minutesBack):
        slots += 1
        volume += int(float(data[x]))

    #scales the volume by the price of the crypto currency
    volume *= float(getbinanceprice(currency))
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

        #NOTE: can change back to normal if this doesnt work
        if(percentChangesList[currentSlot] < 0):
            oldVolume += float(i) * (percentChangeScale) * PARAMETERS['NEGATIVE_WEIGHT']
            oldVolume += float(i) * (-1 * percentChangeScale) * PARAMETERS['PRIMARY_MODIFIED_VOLUME_SCALER']
        if(percentChangesList[currentSlot] > 0):
            oldVolume += float(i) * (percentChangeScale * PARAMETERS['PRIMARY_MODIFIED_VOLUME_SCALER'])
            oldVolume += float(i) * -1 *(percentChangeScale) * PARAMETERS['NEGATIVE_WEIGHT']
        currentSlot += 1


    return float(oldVolume)

#get the binance price of the specified currency
def getbinanceprice(currency):

    priceDict = CryptoStats.getClosePrice()
    return priceDict[currency][0]

    #interval based on this from binance API
    #     m -> minutes;     h -> hours;     d -> days;     w -> weeks;    M -> months
    #  1m  3m   5m  15m  30m  1h 2h 4h 6h 8h  12h  1d   3d  1w   1M
    # method used to update price lists on past hour of trends

#method to iterate through all the cryptos available on binance and store their price changes, percent price changes,
#volume changes, percent volume changes, scores, time increasing, and time decreasing
def updateCrypto(minutesBack):

    for key,value in priceSymbols.items():

        closeVolumeIndex = minutesBack - 1

        # Pulling the three dictionaries from the cryptostats class and getting the specific list associated with the current symbol
        openPriceData = CryptoStats.getOpenPrice()[value]
        closePriceData = CryptoStats.getClosePrice()[value]
        volumeData = CryptoStats.getVolume()[value]

        # calculate the percent change over the whole hour and store
        openPrice = openPriceData[0]
        closePrice = closePriceData[0]
        pricePercentData[value]['percentbyhour'] = calcPercentChange(openPrice, closePrice)

        # calculate the percent change in volume over the whole hour and store
        openVolume = volumeData[0]
        closeVolume = volumeData[closeVolumeIndex]
        volumePercentData[value]['percentbyhour'] = calcPercentChange(openVolume, closeVolume)

        # test.write("Currency: {} Open Price: {} Close Price: {} Open Volume: {} Close Volume: {} \n".format(value, openPrice, closePrice, openVolume, closeVolume))

        # iterate through all the open and close prices for the given interval
        percentChanges[value] = []
        i = 0
        while (i < minutesBack):
            percentChanges[value].append(calcPercentChange(openPriceData[i], closePriceData[i]))
            i += 1
        print("Percent Changes Dictionary: {} Length of Dictionary: {}".format(percentChanges[value],
                                                                               len(percentChanges[value])))
        # reset the lists of the volume amounts and volume percent changes
        volumeAmounts[value] = []
        volumePercentChanges[value] = []

        volumeAmounts[value].append(volumeData[0])

        for i in range(1, minutesBack):
            volumePercentChanges[value].append(calcPercentChange(volumeData[i-1], volumeData[i]))
            volumeAmounts[value].append(volumeData[i])

         # calculate and store the percent time increasing for volume and price percent changes
        pricePercentData[value]['timeIncreasing'] = getTimeIncreasing(0, value)
        pricePercentData[value]['weightedtimeIncreasing'] = getTimeIncreasing(1, value)

        volumePercentData[value]['timeIncreasing'] = getVolumeTimeIncreasing(0, value)
        volumePercentData[value]['weightedtimeIncreasing'] = getVolumeTimeIncreasing(1, value)

        modifiedVolume[value] = []
        # get the modified volume changes
        modifiedVolume[value] = getModifiedVolume(value)

        # use the calculations to get a score
        calc_score = getScore(value)
        new_score = {value: calc_score}
        scores.update(new_score)

        # calcualte a weightedMovingAverage
        weightedMovingAverage[value] = setWeightedMovingAverage(value, minutesBack)

    for key, value in scores.items():
        if (value > PARAMETERS['MINIMUM_SCORE']):
            entry = {key: value}
            currencyToTrade.update(entry)

    print("OUR LIST OF CRYPTO: ")
    print(currencyToTrade)
    file.write("OUR LIST OF CRYPTO: ")
    file.write(str(currencyToTrade))
    test.write("Volume Amount Dict: {} Volume Percent Dict: {}".format(volumeAmounts, volumePercentChanges))


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


    return (slots_increasing/slots) * PARAMETERS['VOLUME_INCREASING_MODIFIER']

# method to calculate the "score" that crypto get when they are updated by hour
# score is a combination of weighted time increasing and % change over hour.
# for both volume and price
def getScore(symbol):
    new_score = 0

    new_score += (volumePercentData[symbol]['percentbyhour'] * PARAMETERS['VOLUME_PERCENT_BY_HOUR_MODIFIER'])
    new_score += pricePercentData[symbol]['percentbyhour'] * PARAMETERS['PERCENT_BY_HOUR_MODIFIER']

    new_score += pricePercentData[symbol]['weightedtimeIncreasing']

    new_score += volumePercentData[symbol]['weightedtimeIncreasing']
    new_score += modifiedVolume[symbol] * PARAMETERS['PRIMARY_MODIFIED_VOLUME_SCALER']

    return new_score


#finds the next currency to buy
def priceChecker():

    #Compares the two price lists and sets the currencyToBuy to be
    # the coin with the highest score that also is above the minimum moving average
    maxScore = 0
    for key, value in currencyToTrade.items():
        print("The score of {} is {} ".format(key, scores[key]))
        file.write("The score of {} is {} \n".format(key, scores[key]))

        if(maxScore < scores[key] and float(weightedMovingAverage[key]) > float(PARAMETERS['MINIMUM_MOVING_AVERAGE'])):
            maxScore = scores[key]
            print("CURRENT HIGH SCORE: The score of {} is {}".format(key, scores[key]))
            file.write("CURRENT HIGH SCORE: The score of {} is {} \n".format(key, scores[key]))
            currencyToBuy = key

    print("Coin with the highest score is {} which is {}".format(currencyToBuy, maxScore))
    file.write("Coin with the highest score is {} which is {} \n".format(currencyToBuy, maxScore))

    return currencyToBuy #potential runtime error if all negative todo


#just calculates the percent change between two values
def calcPercentChange(startVal, endVal):
    if(float(startVal) == 0.0):
        return float(endVal) * 100.0

    return (((float(endVal) - float(startVal))/float(startVal) ) * 100)


#checks if the current crypto has been decreasing the past ten minutes
#if yes it forces a new check to see if there is a better crypto
def checkFailureCondition(currency, timesIncreasing, minutesBack):

    print("New Interval")
    file.write("New Interval")

    openPriceData = CryptoStats.getOpenPrice()[currency]
    closePriceData = CryptoStats.getClosePrice()[currency]

    #get the starting price of the interval
    startPriceInterval = percentChange[0][1]
    timeIncreasingCounter = 0

    #iterate through the list of percent changes and add up when the percent change was positive
    for x in range(0, minutesBack):
        startPrice = openPriceData[x]
        endPrice = closePriceData[x]
        print("Current Crypto: {} Start Price: {} End Price: ".format(currency, startPrice, endPrice))
        file.write("Current Crypto: {} Start Price: {} End Price: \n".format(currency, startPrice, endPrice))
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

    openPriceData = CryptoStats.getOpenPrice()[symbol]
    closePriceData = CryptoStats.getClosePrice()[symbol]

    if (percentChange == []):
        return 0

    startPrice = openPriceData[0]
    endPrice = closePriceData[0]
    percentChange = calcPercentChange(startPrice, endPrice)

    if(percentChange < PARAMETERS['MAX_DECREASE']):
        print("TOO NEGATIVE. RESTART")
        file.write("TOO NEGATIVE. RESTART")
        return 1

    return 0

#checks to see if the currency has increased or decreased more than is allowed
# if yes, then the reevaluation process is restarted
def checkExitCondition(currency):

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
    global priceBought

    currentPrice = getbinanceprice(currency)
    floorPrice = PARAMETERS['FLOOR_PRICE_MODIFIER'] * priceBought
    endtime = int(time.time() * 1000)
    starttime = endtime - intervalTypes['15m']['inMS']

    direction = increasingOrDecreasing(currency, intervalTypes['15m']['symbol'], starttime, endtime)
    allIntervalsDecreasing = checkFailureCondition(currency, timesIncreasing, minutesBack)

    #check to see if the current price is too low, the crypto is decreasing over the past 15 minutes
    #and all the intervals are decreasing
    if(float(currentPrice) < float(floorPrice) and direction == 0 & allIntervalsDecreasing == 1):
        print("WAS TOO LOW")
        return 1

    return 0

#calculates and returns the last slot of an array or list based on the interval, starttime, and endtime
def getLastSlot(interval, starttime, endtime):
    difference = endtime - starttime
    intervalInMs = intervalTypes[interval]['inMS']

    if(difference == 0):
        return 0

    numIntervals = difference/intervalInMs


    return numIntervals - 1

#returns whether the specified currency is increasing or decreasing over the interval
# 0 means decreasing, 1 means stable or increasing
def increasingOrDecreasing(currency):

    openPriceData = CryptoStats.getOpenPrice()[currency]
    closePriceData = CryptoStats.getClosePrice()[currency]

    if percentChange == []:
        return 0

    startPrice = openPriceData[0]
    endPrice = closePriceData[0]

    calcPChange = calcPercentChange(startPrice, endPrice)

    if(calcPChange >= 0.0):
        return 1

    return 0


def main():
    global CUMULATIVE_PERCENT_CHANGE
    global initialBalance
    global RESTART
    global RESTART_TN
    global RESTART_LOW
    global EXIT
    global pricesold
    global minutesBack
    minutesBack = 30
    currentCurrency = ''
    x = 0

    updateCrypto(minutesBack)
    '''
    file.write("\n\n\n\n")
    file.write('------------------------------------------------------------------------------------ \n')

    print("Date and Time of Run {}".format(datetime.datetime.now()))
    file.write("Date and Time of Run {} \n".format(datetime.datetime.now()))


    initialBalance = getBalance('BTC')

    binStepSize()
    while(x < PARAMETERS['MAX_CYCLES'] and EXIT == 0):
        t = 0
        RESTART = 0
        RESTART_LOW = 0
        RESTART_TN = 0
        endTime = int(time.time() * 1000)
        startTime = endTime - 3600000

        updateCrypto(minutesBack)


        oldCurrency = currentCurrency
        currentCurrency = priceChecker()


        if(oldCurrency != currentCurrency and oldCurrency != ''):
            sellBin(oldCurrency)
            print("THIS RUN SOLD AT: {}".format(datetime.datetime.time(datetime.datetime.now())))
            file.write("THIS RUN SOLD AT: {} \n".format(datetime.datetime.time(datetime.datetime.now())))

        if(oldCurrency != currentCurrency):
            buyBin(currentCurrency)
            print("THIS RUN BOUGHT AT: {}".format(datetime.datetime.time(datetime.datetime.now())))
            file.write("THIS RUN BOUGHT AT: {}".format(datetime.datetime.time(datetime.datetime.now())))

        #while statement is more flexible way to wait for a period of time or a restart
        # restart could be caused by a met failure condition or a met sustained one
        while(t < PARAMETERS['MAX_TIME_CYCLE'] and PARAMETERS['RESTART'] == 0 and PARAMETERS['RESTART_TN'] == 0 and PARAMETERS['RESTART_LOW'] == 0):
            time.sleep(1)

            if(t % PARAMETERS['WAIT_FOR_CHECK_FAILURE'] == 0 and t != 0):
                RESTART = checkFailureCondition(currentCurrency, 0, minutesBack)

            if(t > PARAMETERS['WAIT_FOR_CHECK_TOO_LOW'] and t % PARAMETERS['WAIT_FOR_CHECK_FAILURE']):
                RESTART_LOW = checkTooLow(currentCurrency, 1)

            RESTART_TN = checkTooNegative(currentCurrency)
            t+=1


        pricesold = getbinanceprice(currentCurrency)
        print('Price bought: {} Price sold: {} '.format(priceBought, pricesold))
        file.write('Price bought: {} Price sold: {} \n'.format(priceBought, pricesold))

        cumulativePercentChange = calcPercentChange(priceBought, pricesold)
        PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE'] += cumulativePercentChange
        print("FINAL percent change over the life of owning this crypto " + str(PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE']))
        file.write("FINAL percent change over the life of owning this crypto " + str(PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE']))


        EXIT = checkExitCondition(currentCurrency)
        x+=1

    print("Cumualtive percent change over the life of all cryptos owneed so far {}".format(PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE']))
    file.write("Cumualtive percent change over the life of all cryptos owneed so far {} \n".format(PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE']))
    sellBin(currentCurrency)


    file.write('---------------------------||||||||||||||||----------------------------------------' + "\n")
    file.write("\n" + "\n" + "\n")

    file.close()
    '''
if __name__ == "__main__":
    main()
