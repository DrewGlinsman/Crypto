# Copyright (c) 2018 A&D
# Auto trading bot that uses parameters sent by CryptoTrainer to test them


import os
import sys
import CryptoStatAnalysis
import datetime
import time
import pathlib
import CryptoStats
import calendar
import pickle

from CryptoTrainer import PARAMETERS, minInDay

try:
    from urlib import urlencode

except ImportError:
    from urllib.parse import urlencode


#todo make a series of functions used that have random variables in them and random variables left out instead of a simple linear score and simple parameter variation
#todo add in a parser for the stdin
#todo add a minimum volume parameter to weed out the cryptos not traded at a high enough rate
#todo add a minimum financial transaction amount per minute that must be occuring (uses the minimum volume and current price of each crypto)

#setup the relative file path
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname + '/', '')

#GLOBAL_VARIABLES

#0 is false, 1 is true
#flags used to exit if different exit conditions are met (set with random params from the parameter set)
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

priceList = []
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
                'ZECBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ADABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ADXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'AIONBTC' : {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'AMBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'APPCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ARKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ARNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ASTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BATBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCPTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BNBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BQXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BRDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BTSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CDTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CMTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CNDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EDOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ELFBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ENGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ENJBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EOSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EVXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'FUELBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'FUNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GASBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GTOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GVTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GXSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'HSRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ICNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ICXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'IOTABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'KMDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'KNCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LENDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LINKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LRCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LSKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LUNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MANABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MCOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MDABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MODBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MTHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MTLBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NAVBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NEBLBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NEOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NULSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OAXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OMGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OSTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'POEBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'POWRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'PPTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'QSPBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'RCNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'RDNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'REQBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SALTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNGLSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNMBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'STORJBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'STRATBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SUBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TNBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TRIGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TRXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VENBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VIBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VIBEBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WABIBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WAVESBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WINGSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WTCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XVGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XZCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'YOYOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ZRXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}}

#stores the calculated weightedMovingAverage
weightedMovingAverage = {'BTCUSDT': [], 'XRPBTC': [],
                'ETHBTC': [], 'BCCBTC': [],
                'LTCBTC': [], 'DASHBTC': [],
                'XMRBTC': [], 'QTUMBTC': [], 'ETCBTC': [],
                'ZECBTC': [], 'ADABTC': [], 'ADXBTC': [], 'AIONBTC' : [], 'AMBBTC': [], 'APPCBTC': [], 'ARKBTC': [], 'ARNBTC': [], 'ASTBTC': [], 'BATBTC': [], 'BCDBTC': [], 'BCPTBTC': [], 'BNBBTC': [], 'BNTBTC': [], 'BQXBTC': [], 'BRDBTC': [], 'BTSBTC': [], 'CDTBTC': [], 'CMTBTC': [], 'CNDBTC': [], 'DGDBTC': [], 'DLTBTC': [], 'DNTBTC': [], 'EDOBTC': [], 'ELFBTC': [], 'ENGBTC': [], 'ENJBTC': [], 'EOSBTC': [], 'EVXBTC': [], 'FUELBTC': [], 'FUNBTC': [], 'GASBTC': [], 'GTOBTC': [], 'GVTBTC': [], 'GXSBTC': [], 'HSRBTC': [], 'ICNBTC': [], 'ICXBTC': [], 'IOTABTC': [], 'KMDBTC': [], 'KNCBTC': [], 'LENDBTC': [], 'LINKBTC': [], 'LRCBTC': [], 'LSKBTC': [], 'LUNBTC': [], 'MANABTC': [], 'MCOBTC': [], 'MDABTC': [], 'MODBTC': [], 'MTHBTC': [], 'MTLBTC': [], 'NAVBTC': [], 'NEBLBTC': [], 'NEOBTC': [], 'NULSBTC': [], 'OAXBTC': [], 'OMGBTC': [], 'OSTBTC': [], 'POEBTC': [], 'POWRBTC': [], 'PPTBTC': [], 'QSPBTC': [], 'RCNBTC': [], 'RDNBTC': [], 'REQBTC': [], 'SALTBTC': [], 'SNGLSBTC': [], 'SNMBTC': [], 'SNTBTC': [], 'STORJBTC': [], 'STRATBTC': [], 'SUBBTC': [], 'TNBBTC': [], 'TNTBTC': [], 'TRIGBTC': [], 'TRXBTC': [], 'VENBTC': [], 'VIBBTC': [], 'VIBEBTC': [], 'WABIBTC': [], 'WAVESBTC': [], 'WINGSBTC': [], 'WTCBTC': [], 'XVGBTC': [], 'XZCBTC': [], 'YOYOBTC': [], 'ZRXBTC': []}



#the modified cumulative volume over a period (a negative percent change will result in the volume change being counted as negative towards the
# cumulative volume stored here
modifiedVolume = {'BTCUSDT': 0.0, 'XRPBTC': 0.0,
                'ETHBTC': 0.0, 'BCCBTC': 0.0,
                'LTCBTC': 0.0, 'DASHBTC': 0.0,
                'XMRBTC': 0.0, 'QTUMBTC': 0.0, 'ETCBTC': 0.0,
                'ZECBTC': 0.0, 'ADABTC': 0.0, 'ADXBTC': 0.0, 'AIONBTC' : 0.0, 'AMBBTC': 0.0, 'APPCBTC': 0.0, 'ARKBTC': 0.0, 'ARNBTC': 0.0, 'ASTBTC': 0.0, 'BATBTC': 0.0, 'BCDBTC': 0.0, 'BCPTBTC': 0.0, 'BNBBTC': 0.0, 'BNTBTC': 0.0, 'BQXBTC': 0.0, 'BRDBTC': 0.0, 'BTSBTC': 0.0, 'CDTBTC': 0.0, 'CMTBTC': 0.0, 'CNDBTC': 0.0, 'DGDBTC': 0.0, 'DLTBTC': 0.0, 'DNTBTC': 0.0, 'EDOBTC': 0.0, 'ELFBTC': 0.0, 'ENGBTC': 0.0, 'ENJBTC': 0.0, 'EOSBTC': 0.0, 'EVXBTC': 0.0, 'FUELBTC': 0.0, 'FUNBTC': 0.0, 'GASBTC': 0.0, 'GTOBTC': 0.0, 'GVTBTC': 0.0, 'GXSBTC': 0.0, 'HSRBTC': 0.0, 'ICNBTC': 0.0, 'ICXBTC': 0.0, 'IOTABTC': 0.0, 'KMDBTC': 0.0, 'KNCBTC': 0.0, 'LENDBTC': 0.0, 'LINKBTC': 0.0, 'LRCBTC': 0.0, 'LSKBTC': 0.0, 'LUNBTC': 0.0, 'MANABTC': 0.0, 'MCOBTC': 0.0, 'MDABTC': 0.0, 'MODBTC': 0.0, 'MTHBTC': 0.0, 'MTLBTC': 0.0, 'NAVBTC': 0.0, 'NEBLBTC': 0.0, 'NEOBTC': 0.0, 'NULSBTC': 0.0, 'OAXBTC': 0.0, 'OMGBTC': 0.0, 'OSTBTC': 0.0, 'POEBTC': 0.0, 'POWRBTC': 0.0, 'PPTBTC': 0.0, 'QSPBTC': 0.0, 'RCNBTC': 0.0, 'RDNBTC': 0.0, 'REQBTC': 0.0, 'SALTBTC': 0.0, 'SNGLSBTC': 0.0, 'SNMBTC': 0.0, 'SNTBTC': 0.0, 'STORJBTC': 0.0, 'STRATBTC': 0.0, 'SUBBTC': 0.0, 'TNBBTC': 0.0, 'TNTBTC': 0.0, 'TRIGBTC': 0.0, 'TRXBTC': 0.0, 'VENBTC': 0.0, 'VIBBTC': 0.0, 'VIBEBTC': 0.0, 'WABIBTC': 0.0, 'WAVESBTC': 0.0, 'WINGSBTC': 0.0, 'WTCBTC': 0.0, 'XVGBTC': 0.0, 'XZCBTC': 0.0, 'YOYOBTC': 0.0, 'ZRXBTC': 0.0}

#stored volume, mean, and score
storedScores = {}

#holds the the other stat items in it
statDict = {}

#the binance intervals, their symbols, and their time in milliseconds
intervalTypes = { '1m': {'symbol': '1m', 'inMS': 60000},  '3m': {'symbol': '3m', 'inMS': 180000}, '5m': {'symbol': '5m', 'inMS': 300000}, '15m': {'symbol': '15m', 'inMS': 900000}, '30m': {'symbol': '30m', 'inMS': 1800000}, '1h': {'symbol': '1h', 'inMS': 3600000}, '2h': {'symbol': '2h', 'inMS': 7200000}, '4h': {'symbol': '4h', 'inMS': 14400000}, '6h': {'symbol': '6h', 'inMS': 21600000}, '8h': {'symbol': '8h', 'inMS': 28800000}, '12h': {'symbol': '12h', 'inMS': 43200000}, '1d': {'symbol': '1d', 'inMS': 86400000}, '3d': {'symbol': '3d', 'inMS': 259200000}, '1w': {'symbol': '1w' , 'inMS': 604800000}, '1M': {'symbol': '1M', 'inMS': 2629746000}}

#the score of each crypto
scores = {}

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
PARAMETERS = {'PERCENT_QUANTITY_TO_SPEND': 0.9, 'PERCENT_TO_SPEND': 1.0, 'MINIMUM_PERCENT_INCREASE': 5.0, 'MINIMUM_SCORE': 0.01, 'MINIMUM_MOVING_AVERAGE': .001, 'MAX_DECREASE': -10.0, 'MAX_TIME_CYCLE': 60.0, 'MAX_CYCLES': 24, 'MAX_PERCENT_CHANGE': 100.0, 'NEGATIVE_WEIGHT': 1.0, 'CUMULATIVE_PERCENT_CHANGE': 0.0, 'CUMULATIVE_PERCENT_CHANGE_STORE': 0.0, 'SLOT_WEIGHT': 1.0, 'TIME_INCREASING_MODIFIER': 1.0, 'VOLUME_INCREASING_MODIFIER': 1.0, 'PERCENT_BY_HOUR_MODIFIER': 1.0, 'VOLUME_PERCENT_BY_HOUR_MODIFIER': 1.0, 'FLOOR_PRICE_MODIFIER': 1.005, 'MODIFIED_VOLUME_MODIFIER': 1.0, 'CUMULATIVE_PRICE_MODIFIER': 1.0, 'PRIMARY_MODIFIED_VOLUME_SCALER': 1.0, 'WAIT_FOR_CHECK_FAILURE': 5.0, 'WAIT_FOR_CHECK_TOO_LOW': 10.0, 'VARIATION_NUMBER': 0.0, 'CLASS_NUM': -1, 'MIN_OFFSET': 120.0, 'INTERVAL_TO_TEST': 1440.0, 'MINUTES_IN_PAST': 0.0, 'START_MONEY': 100, 'END_MONEY': 0}

#number of minutes we want to iterate backwards
startMinute = 0
endMinute = 60
startMinNum = 0
endMinNum = 60
currentMinute = 0

#true price for the crrpto being bought
truePriceBought = 0.0

#the currently owned crypto
owned = 'BTCUSDT'

#the number of buys
numBuys = 0

#the number of sells
numSells = 0

#whether testing or not
testCheck = 0

#percent Changes over all sepearted periods of time
allOwnedCryptoPercentChanges = []

#cryptos seperated by decision into those disregarded, those chosen but not making final cut because of their mean, those selected that have the appropriate mean, and the crypto that is chosen, has the right mean, and is the max
cryptosSeperated = {'Disregarded': [], 'Chosen': [], 'chosenButCut': [], 'chosenNotCut': [], 'theMax': []}


file = ''
picklefile = ''

#todo finish implementing this system of tracking the crypto we currently own
#the crypto we currently own
ownCrypto = 'BTCUSDT'

#dictionaires for the modes this can be run in
modes = {'SoloEvaluator': {'string': 'SoloEvaluator', 'value': 0}, 'SoloTrainer': {'string': 'SoloTrainer', 'value': 1}, 'MultiTrainer': {'string': 'MultiTrainer', 'value': 2}}

#the number for the mode  (default = 0)
mode = modes['SoloEvaluator']['value']

#you can use the words instead of these values
YES = 1
NO = 0

#input values that are stored (other than parameters)
storedInput = {'runTime': -1, 'running': modes['SoloEvaluator']['string'], 'pickleDirec': r'C:\Users\katso\Documents\GitHub\Crypto\\', 'classNum': -1, 'variationNum': -1}

#the interval size plus the offset
realInterval = 0

#the different dictionaries used to store the data for the interval
openPriceData = {}
closePriceData = {}
volumeData = {}
highPriceData = {}
lowPriceData = {}


def buildLogs(timestamp):
    """
    :param timestamp:
    :return:
    """
    global file
    global storedInput


    # Directory path (r makes this a raw string so the backslashes do not cause a compiler issue

    logPaths =  os.path.join(dirname + '/', 'Logs')


    #concatenates with the mode this is running in (solo, training in a class with other variations)
    withMode = logPaths + '/Mode-' + storedInput['running']

    date = datetime.date.today()
    day = date.day
    month = date.month
    year = date.year

    # concatenates the logpath with a date so each analysis log set is in its own file by day
    withDate = withMode + '/Year-' + str(year) + '/Month-' + str(calendar.month_name[month] + '/Day-' + str(day))


    withRunTime = withDate + '/RunTime-' + str(storedInput['runTime'])

    withClass = withRunTime + '/Class-' + str(storedInput['classNum'])

    # concatenates with the variation number
    withVarNum = withClass + '/Variation-' + str(int(storedInput['variationNum']))

    # creates a directory if one does not exist
    pathlib.Path(withVarNum).mkdir(parents=True, exist_ok=True)

    # file name concatentation with runNum
    fileName = "Time=" + str(timestamp) + '_Evaluator.txt'

    # log file name + path
    logCompletePath = os.path.join(withVarNum ,fileName)


    # open a file for appending (a). + creates file if does not exist
    file = open(logCompletePath, "a+")


#reads pickle from a file into the passed parameter dictionary
def readParamPickle(paramDict):
    """
    :param paramDict:
    :return:
    """

    pickleFileName = "param.pkl"
    picklefile = storedInput['pickleDirec'] + pickleFileName

    with open(picklefile, "rb") as pickle_in:
       paramDict = pickle.load(pickle_in)



    return paramDict

#write pickle to a file
def writeParamPickle(paramDict):
    """
    :param paramDict:
    :return:
    """

    pickleFileName = "param.pkl"
    picklefile = storedInput['pickleDirec'] + pickleFileName

    with open(picklefile, "wb") as pickle_out:
        pickle.dump(paramDict, pickle_out)

    return paramDict


#todo add a way to read in the runNumber from the crypto trainer
def readTheInput(timestamp):
    """
    :param timestamp:
    :return:
    """
    global modes
    global priceList
    global storedInput
    global mode
    global PARAMETERS


    #TODO IMPORTANT change variable to 1 anytime you are doing anything other than running just a single evaluator
    noinput = 0


    if noinput == 0:
        # make the max cycles equal to the number of days of the interval in hours
        PARAMETERS['MAX_CYCLES'] = (PARAMETERS['INTERVAL_TO_TEST'] / minInDay) * 24.0
        PARAMETERS['CLASS_NUM'] = -1
        storedInput['runTime'] = timestamp

        return PARAMETERS

    for line in sys.stdin:

        if line != '':
            # split the passed string into a list seperated by spaces
            listSplits = line.split(' ')

            #loops through the different values split from the input and stores them in a dictionary
            count = 0
            for key, value in storedInput.items():
                #when the string for the mode is passed its name is stored in the stored input dictionary and the value is stored as a variable
                if count == 1:
                    storedInput[key] = modes[listSplits[count]]['string']
                    mode = modes[storedInput[key]]['value']
                #todo replace this line with an else and then figure out why the evaluators are only buying once
                    storedInput[key] = listSplits[count]

                count += 1




#get the balance in bitcoins

#buy the specified crypto currency
def buyBin(symbol, currentMinute):
    """
    :param symbol:
    :param currentMinute:
    :return:
    """
    global priceBought
    global truePriceBought
    global owned

    ratio = getbinanceprice(symbol, currentMinute)
    priceBought = ratio
    truePriceBought = ratio
    owned = symbol

    #mark item as the current crypto being traded and save the buy price at for failure condition
    entry = {symbol:{'buyPrice': ratio, 'timestamp': 0}}
    currencyToTrade.clear()
    currencyToTrade.update(entry)

#sell the specified crypto
def sellBin(symbol):
    """
    :param symbol:
    :return:
    """
    return 0



#add in the weight todo
#calculates the weighted moving average over the specified interval for a crypto currency

def setWeightedMovingAverage(currency, startMinute, endMinute):
    """
    :param currency:
    :param startMinute:
    :param endMinute:
    :return:
    """
    global realInterval
    global openPriceData
    global closePriceData

    cumulativePrice = 0.0

    openPriceDataLocal = openPriceData[currency]
    closePriceDataLocal = closePriceData[currency]

    slots = endMinute - startMinute - 1

    if openPriceData == []:
        return 0

    #adds up the cumulative price changes using each interval
    for x in range (startMinute, endMinute):
       startPrice = openPriceDataLocal[x]
       endPrice = closePriceDataLocal[x]
       change = calcPercentChange(startPrice, endPrice)

       cumulativePrice += change

    #the scaling of the cumulative price
    cumulativePrice = (cumulativePrice / slots) * PARAMETERS['CUMULATIVE_PRICE_MODIFIER']



    return cumulativePrice

# this function will update the weighted moving average every second the program runs todo
# def updateWeightedMovingAverage(currency, interval, starttime, endtime):


#gets the cumulative volume over a period and scales it based on the currency's price
def getVolume(currency, currentMinute):
    """
    :param currency:
    :param currentMinute:
    :return:
    """
    global realInterval
    global volumeData

    volume = []
    #building the request
    volumeDataLocal = volumeData[currency]
    #adds up all the volumes over the interval
    for x in volumeDataLocal:
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
    """
    :param currency:
    :return:
    """
    oldVolume = 0
    vols = []
    volList = []
    currentSlot = 0

    percentChangesList = percentChanges[currency]
    volumeAmountList = volumeAmounts[currency]

    #adds up the volume with negative percent changes in price resulting in the volume
    #considered to be mostly 'negative', how much is determined by the magnitude
    #of the percent change in price
    for i in volumeAmountList:

        #makes each volume % change back into a decimal


        percentChangeScale = (percentChangesList[currentSlot])

        if percentChangeScale < 0:
            vols.append(percentChangeScale * volumeAmountList[currentSlot] * PARAMETERS['NEGATIVE_WEIGHT'])
            volList.append({'volumeofslot': volumeAmountList[currentSlot], 'weight': PARAMETERS['NEGATIVE_WEIGHT']})
            oldVolume += percentChangeScale * volumeAmountList[currentSlot] * PARAMETERS['NEGATIVE_WEIGHT']
        #todo the below may have not been there for the last set of tests
        if percentChangeScale >= 0:
            vols.append( percentChangeScale * volumeAmountList[currentSlot])
            volList.append({'volumeofslot': volumeAmountList[currentSlot], 'weight': 'NONE'})
            oldVolume += percentChangeScale * volumeAmountList[currentSlot]



        currentSlot += 1


    return float(oldVolume)

#get the binance price of the specified currency
def getbinanceprice(currency, currentMinute):
    """
    :param currency:
    :param currentMinute:
    :return:
    """
    global realInterval
    global closePriceData

    priceDict = closePriceData
    if priceDict == {} or currency == '':
        return 0.0

    binPrice = priceDict[currency][currentMinute]

    return binPrice


    #interval based on this from binance API
    #     m -> minutes;     h -> hours;     d -> days;     w -> weeks;    M -> months
    #  1m  3m   5m  15m  30m  1h 2h 4h 6h 8h  12h  1d   3d  1w   1M
    # method used to update price lists on past hour of trends

#method to iterate through all the cryptos available on binance and store their price changes, percent price changes,
#volume changes, percent volume changes, scores, time increasing, and time decreasing


def updateCrypto(startMinute, endMinute, currentMinute):
    """
    :param startMinute:
    :param endMinute:
    :param currentMinute:
    :return:
    """
    global realInterval
    global openPriceData
    global closePriceData
    global volumeData

    for key,  currency in priceSymbols.items():


        # Pulling the three dictionaries from the cryptostats class and getting the specific list associated with the current symbol
        openPriceDataLocal = openPriceData[currency]
        closePriceDataLocal = closePriceData[currency]
        volumeDataLocal = getVolume(currency, currentMinute)


        #todo figure out why this and the one below always starts at 0
        # calculate the percent change over the whole hour and store
        openPrice = openPriceDataLocal [startMinute]
        closePriceIndex = endMinute - 1
        closePrice = closePriceDataLocal[closePriceIndex]
        pricePercentData[currency]['percentbyhour'] = calcPercentChange(openPrice, closePrice)

        values['PERCENT_BY_HOUR'].append(pricePercentData[currency]['percentbyhour'])

        #todo figure out if it should have been endMinute - startMinute - 1 or just endMinute - 1
        # calculate the percent change in volume over the whole hour and store
        openVolume = volumeDataLocal[startMinute]
        closeVolumeIndex = endMinute - 1
        closeVolume = volumeDataLocal[closeVolumeIndex]
        volumePercentData[currency]['percentbyhour'] = calcPercentChange(openVolume, closeVolume)

        # test.write("Currency: {} Open Price: {} Close Price: {} Open Volume: {} Close Volume: {} \n".format(value, openPrice, closePrice, openVolume, closeVolume))

        values['VOLUME_BY_HOUR'].append(volumePercentData[currency]['percentbyhour'])

        # iterate through all the open and close prices for the given interval
        percentChanges[currency][:] = []

        for i in range(startMinute, endMinute - 1):
            percentChanges[currency].append(calcPercentChange(openPriceDataLocal[i + 1], closePriceDataLocal[i]))
            i += 1

        pricePercentData[currency]['timeIncreasing'] = getTimeIncreasing(0, currency)
        pricePercentData[currency]['weightedtimeIncreasing'] = getTimeIncreasing(1, currency)

        # reset the lists of the volume amounts and volume percent changes
        volumeAmounts[currency][:] = []
        volumePercentChanges[currency][:] = []

        # calculate and store the percent time increasing for volume and price percent changes
        for w in range(startMinute, endMinute - 1):
            volumePercentChanges[currency].append(calcPercentChange(volumeDataLocal[w - 1], volumeDataLocal[w]))
            volumeAmounts[currency].append(volumeDataLocal[w])

            w += 1

        volumePercentData[currency]['timeIncreasing'] = getVolumeTimeIncreasing(0, currency)
        volumePercentData[currency]['weightedtimeIncreasing'] = getVolumeTimeIncreasing(1, currency)

        # store the time increasing and weighted time increasing for price data to be used for scaling
        values['TIME_INCREASING'].append(pricePercentData[currency]['timeIncreasing'])
        values['WEIGHTED_TIME_INCREASING'].append(pricePercentData[currency]['weightedtimeIncreasing'])



        # store the time increasing and weighted time increasing for volume data to be used for scaling
        values['VOLUME_TIME_INCREASING'].append(volumePercentData[currency]['timeIncreasing'])
        values['WEIGHTED_VOLUME_TIME_INCREASING'].append(volumePercentData[currency]['weightedtimeIncreasing'])


        modifiedVolume[currency] = 0
        # get the modified volume changes
        modifiedVolume[currency] = getModifiedVolume(currency)

        values['MODIFIED_VOLUME'].append(modifiedVolume[currency])

        # calcualte a weightedMovingAverage
        weightedMovingAverage[currency] = setWeightedMovingAverage(currency, startMinute, endMinute)

    setMaxValue()
    resetValues()

    # gets the score for each crypto
    # moved to its own loop so all the values can be properly scaled by the largest value
    for key, currencyname in priceSymbols.items():

        # use the calculations to get a score
        calc_score = getScore(currencyname)
        new_score = {currencyname: calc_score}
        scores.update(new_score)
        storedScores.update({key: new_score})

        # calculate a weightedMovingAverage
        weightedMovingAverage[currencyname] = setWeightedMovingAverage(currencyname, startMinute, endMinute)


    #add cryptos and their scores to dictionary of currencies to trade if they are above the minimum score
    #record which cryptos were not chosen, and which were chosen that had the right score or had the right score and mean
    for key, value in scores.items():
        entry = {key: value}
        if (value > PARAMETERS['MINIMUM_SCORE']):
            currencyToTrade.update(entry)
            cryptosSeperated['Chosen'].append(key)
            if(weightedMovingAverage[key] < PARAMETERS['MINIMUM_MOVING_AVERAGE']):
                cryptosSeperated['chosenButCut'].append(key)
            else:
                cryptosSeperated['chosenNotCut'].append(key)

        else:
            cryptosSeperated['Disregarded'].append(key)


    #file.write("Currrenty to trade: " + str(currencyToTrade))


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

    if (slots == 0.0):
        slots = 1.0

    return (slots_increasing/slots) * PARAMETERS['VOLUME_INCREASING_MODIFIER']

# method to calculate the "score" that crypto get when they are updated by hour
# score is a combination of weighted time increasing and % change over hour.
# for both volume and price
def getScore(symbol):
    """
    :param symbol:
    :return:
    """
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
        file.write("Whoopsie zero by division error!" + str(maxValues)  + '\n')
        for i in values:
            file.write(str(i) + '\n')


    #addingup the parameters to the score variable
    new_score += (volumePercentData[symbol]['percentbyhour'] / maxValues['VOLUME_BY_HOUR']) * PARAMETERS['VOLUME_PERCENT_BY_HOUR_MODIFIER']
    new_score += ((pricePercentData[symbol]['percentbyhour']) / maxValues['PERCENT_BY_HOUR']) * PARAMETERS['PERCENT_BY_HOUR_MODIFIER']


    new_score += (pricePercentData[symbol]['weightedtimeIncreasing'] / maxValues['WEIGHTED_TIME_INCREASING'])

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
        #file.write("The score of " + str(key) +  ' is ' + str(scores[key]) + '\n')

        try:
            if(maxScore < scores[key] and float(weightedMovingAverage[key]) > float(PARAMETERS['MINIMUM_MOVING_AVERAGE'])):
                maxScore = scores[key]
                #file.write('CURRENT HIGH SCORE: The score of ' + str(key) +  ' is ' + str( scores[key]) + '\n')
                currencyToBuy = key

        except KeyError:
            file.write(" LINE 550 key error " + str(key) + " scores[key] " + weightedMovingAverage[key]  + '\n')

    #file.write('Coin with the highest score is ' + str(currencyToBuy) + ' which is ' + str(maxScore) + '\n' )

    cryptosSeperated['theMax'].append(currencyToBuy)
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
def checkFailureCondition(currency, timesIncreasing, startMinute, endMinute):
    """
    :param currency:
    :param timesIncreasing:
    :param startMinute:
    :param endMinute:
    :return:
    """
    global realInterval
    global openPriceData
    global closePriceData

    openPriceDataLocal = openPriceData[currency]
    closePriceDataLocal = closePriceData[currency]

    #get the starting price of the interval
    startPriceInterval = openPriceDataLocal[startMinute]
    timeIncreasingCounter = 0

    #iterate through the list of percent changes and add up when the percent change was positive
    for x in range(startMinute, endMinute):
        startPrice = openPriceDataLocal[x]
        endPrice = closePriceDataLocal[x]
        #file.write("Current Crypto: " + str(currency) + ' Start Price: ' +str(startPrice) + ' End Price: ' + str(endPrice))
        percentChange = calcPercentChange(startPrice, endPrice)
        if(percentChange > 0):
            timeIncreasingCounter += 1


    intervalPercentChange = calcPercentChange(startPriceInterval, endPrice)
    #file.write('Cumulative percent change over THIS INTERVAL ' + str((intervalPercentChange)))
    #file.write("Times Increasing over the interval: " + str(timeIncreasingCounter))

    if(timeIncreasingCounter <= timesIncreasing):
        #file.write("DECREASED ALL INTERVALS. RESTART")
        return 1

    return 0

#checks whether the function has caused too large of negative decrease the specified interval
def checkTooNegative(symbol, currentMinute):
    """
    :param symbol:
    :param currentMinute:
    :return:
    """
    global realInterval
    global openPriceData
    global closePriceData


    openPriceDataLocal = openPriceData[symbol]
    closePriceDataLcoal = closePriceData[symbol]

    startPrice = openPriceDataLocal[currentMinute]
    endPrice = closePriceDataLcoal[currentMinute]
    percentChange = calcPercentChange(startPrice, endPrice)


    #if the percent change is less than the negation of the absolute value of max decrease (ensures it is treated as negative
    if(percentChange < (-1 * abs((PARAMETERS['MAX_DECREASE'])))):
        #file.write("TOO NEGATIVE. RESTART")
        return 1

    return 0

#checks to see if the currency has increased or decreased more than is allowed
# if yes, then the reevaluation process is restarted
def checkExitCondition(currency, currentMinute):
    """
    :param currency:
    :param currentMinute:
    :return:
    """

    global priceBought

    currentPrice = getbinanceprice(currency, currentMinute)

    percentChange = calcPercentChange(priceBought, currentPrice)

    maxPC = PARAMETERS['MAX_PERCENT_CHANGE']

    #chaeck if the max percent change is negative so that the if statements work correctly
    if maxPC < 0:
        multiplyBy = -1
        multiplyBy2 = 1
    if maxPC >= 0:
        multiplyBy = 1
        multiplyBy2 = -1


    if(percentChange > multiplyBy * PARAMETERS['MAX_PERCENT_CHANGE']):
        #file.write("HIT MAX PERCENT CHANGE")
        return 1

    if(percentChange < multiplyBy2 * PARAMETERS['MAX_PERCENT_CHANGE']):
        #file.write("HIT MINIMUM PERCENT CHANGE")
        return 1


    return 0

#checks to see if the current currency is too near to its starting point
def checkTooLow(currency, timesIncreasing, startMinute, endMinute):
    """
    :param currency:
    :param timesIncreasing:
    :param startMinute:
    :param endMinute:
    :return:
    """
    global priceBought

    currentPrice = getbinanceprice(currency, startMinute)
    floorPrice = PARAMETERS['FLOOR_PRICE_MODIFIER'] * float(priceBought)

    #checks to see if the coin was increasing or decreasing over the last 15 minutes. +13 since endMinute is already one greater than start minute and +8 since checkFailureCondition uses 10 minute intervals
    direction = increasingOrDecreasing(currency, startMinute, endMinute+13)
    allIntervalsDecreasing = checkFailureCondition(currency, timesIncreasing, startMinute, endMinute+8)

    #check to see if the current price is too low, the crypto is decreasing over the past 15 minutes
    #and all the intervals are decreasing
    if(float(currentPrice) < float(floorPrice) and direction == 0 & allIntervalsDecreasing == 1):
        #file.write("WAS TOO LOW")
        return 1

    return 0

#returns whether the specified currency is increasing or decreasing over the interval
# 0 means decreasing, 1 means stable or increasing
def increasingOrDecreasing(currency, startMinute, endMinute):
    """
    :param currency:
    :param startMinute:
    :param endMinute:
    :return:
    """
    global realInterval
    global openPriceData
    global closePriceData

    openPriceDataLocal = openPriceData[currency]
    closePriceDataLocal = closePriceData[currency]


    startPrice = openPriceDataLocal[startMinute]
    endPrice = closePriceDataLocal[endMinute]

    calcPChange = calcPercentChange(startPrice, endPrice)

    if(calcPChange >= 0.0):
        return 1

    return 0

#reset the list of parameter values
def resetValues():
    """
    :return:
    """
    #reset the list of parameter value that are calculated below
    for key, value in values.items():
        values[key][:] = []


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

    #file.write("THE VALUES {}".format(values))
    #file.write("THE MAX {}".format(maxValues))

#creates a dictionary with all the different statistic holding dictionaries that are created with each run
def createStatsDict():
    """
    :return:
    """
    statDict.update({'percentChanges': percentChanges})
    statDict.update({'volumePercentChanges': volumePercentChanges})
    statDict.update({'volumeAmounts': volumeAmounts})
    statDict.update({'pricePercentData': pricePercentData})
    statDict.update({'volumePercentData': volumePercentData})
    statDict.update({'weightedMovingAverage': weightedMovingAverage})
    statDict.update({'modifiedVolume': modifiedVolume})
    statDict.update({'storedScores': storedScores})

#sets all the list of how the cryptos were seperated back to being empty
def resetDecisionsStored(dict):
    """
    :param dict:
    :return:
    """
    for key, value in dict.items():

        value[:] = []

#set the parameter dictionary to use string not float by casting the passed dictionary from pickle file
def strToFloat(paramDict):
    """
    :param paramDict:
    :return:
    """
    newDict = PARAMETERS

    for key, value in paramDict.items():
        newDict[key] = float(value)

    return newDict

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
    global numBuys
    global numSells
    global startMinNum
    global endMinNum
    global truePriceBought
    global cryptosSeperated
    global ownCrypto
    global PARAMETERS
    global storedInput
    global realInterval
    global openPriceData
    global closePriceData
    global volumeData
    global highPriceData
    global lowPriceData


    #number of times that the bot chooses not to buy
    totalAbstain = 0

    #get the timestamp for the files for the log and analysis files
    timestamp = int(time.time() * 1000)

    #reads in the input, usually from the cryptotrainer
    readTheInput(timestamp)

    print(storedInput['runTime'])

    #builds a series of log files using the timestamp
    buildLogs(timestamp)

    #read the pickle parameter file and convert all to float and store in the real param dict
    strPARAMS = readParamPickle(PARAMETERS)
    PARAMETERS = strToFloat(strPARAMS)

    #set the real interval to be used for all the data
    realInterval = PARAMETERS['INTERVAL_TO_TEST'] + PARAMETERS['MIN_OFFSET']

    #store the different kinds of data for the interval
    openPriceData = CryptoStats.getOpenPrice(realInterval , PARAMETERS['MINUTES_IN_PAST'], {})
    closePriceData = CryptoStats.getClosePrice(realInterval, PARAMETERS['MINUTES_IN_PAST'], {})
    volumeData = CryptoStats.getVolume(realInterval, PARAMETERS['MINUTES_IN_PAST'], {})
    highPriceData = CryptoStats.getHighPrice(realInterval, PARAMETERS['MINUTES_IN_PAST'], {})
    lowPriceData = CryptoStats.getLowPrice(realInterval, PARAMETERS['MINUTES_IN_PAST'], {})

    #initialize the minutes that will define the period
    startMinute = int(startMinNum + PARAMETERS['MIN_OFFSET'])
    endMinute = int(endMinNum + PARAMETERS['MIN_OFFSET'])
    currentMinute = int(startMinute)

    #creates a statistic object to record the different decisions and then analyze them
    cryptoRunStats = CryptoStatAnalysis.CryptoStatsAnalysis(storedInput['variationNum'], PARAMETERS['CLASS_NUM'], storedInput['running'], startMinute, endMinute, PARAMETERS, timestamp, openPriceData, closePriceData, volumeData, storedInput['runTime'])

    #intitialize the starting currency and the number of cycles the program has run through
    # a cycle is either a period where a crypto was held or where one was bought/sold
    currentCurrency = ''
    cycles = 0


    #initialize the percent change over the whole test and the percent change over the lifetime of owning a crypto
    PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE'] = 0.0
    PARAMETERS['CUMULATIVE_PERCENT_CHANGE'] = 0.0

    #set the date and time at the top of the log file
    file.write("Date and Time of Run " + str(datetime.datetime.now()) + '\n')

    #runs the bot for a set number of cycles or unless the EXIT condition is met (read the function checkExitCondition)
    # cycles is either a period where a crypto is held and ones where they are bought/sold
    while(cycles < PARAMETERS['MAX_CYCLES'] and EXIT == 0):


        #intialize the time the bot will run for
        t = 0

        #whether the bot decided not to buy or sell on this trade cycle
        numAbstain = 0

        RESTART = 0
        RESTART_LOW = 0
        RESTART_TN = 0

        #intialize the checkers that are set whether a buy or sell occured
        didSell = 0
        didBuy = 0

        #reset current minute to be the start minute
        currentMinute = startMinute

        #run update crypto to assign scores and sort through all the cryptos and advance a minute because of how long it takes to run
        updateCrypto(startMinute, endMinute, currentMinute)
        currentMinute += 1


        #reset the old currency to be equal to whatever the current crypto currency is
        if currentCurrency == '':
            oldCurrency = ownCrypto
        else:
            oldCurrency = currentCurrency

        #set the current currency to be whatever the price checker returns
        # can be a nothing string, the same crypto, or a new one
        currentCurrency = priceChecker()


        #sellf the current crypto if you want to buy a new one
        if (oldCurrency != currentCurrency) and (currentCurrency != '') and currentCurrency != ownCrypto:

            #store the price it was sold at
            pricesold = getbinanceprice(oldCurrency, currentMinute)

            #sell the old currency
            sellBin(oldCurrency)

            #if this is the first cycle we do not count the percentChange from 0 to the current price
            if cycles == 0:
                priceBought = pricesold

            #set sell checker
            didSell = 1

            #calculate and store the percent change from when the crypto was bought to when it was sold
            cumulativePercentChange = calcPercentChange(priceBought, pricesold)
            truePercentChange = calcPercentChange(truePriceBought, pricesold)
            PARAMETERS['CUMULATIVE_PERCENT_CHANGE'] = cumulativePercentChange
            PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE'] += cumulativePercentChange


            #writing to the log about when the run sold and what it bought at and what it sold at
            # as well as what was sold and how it changed
            #file.write("THIS RUN SOLD AT: " + str(currentMinute))
            #file.write('Selling:  ' + str(oldCurrency) + ' Price bought: ' + str(priceBought) +  ' Price sold: ' + str(pricesold) + '\n')
            #file.write("FINAL percent change over the life of owning this crypto " + str(truePercentChange))

            #calcualates the length of the list of all the owned cryptos in order and their corresponding lists of percent changesover each crycle
            lenAllOwned = len(allOwnedCryptoPercentChanges)

            #if the currency currency is not the same one at the end of the list then make a new dictionary and append it
            #the new dictionary will be the current currency as the key and then a list of percent changes
            #else you just add a new the new percent change to the end of the list of percent changes over the life of that
            # cycle of owning that cryptocurrency
            if lenAllOwned == 0 or currentCurrency != allOwnedCryptoPercentChanges[lenAllOwned - 1]:
                newDict = {currentCurrency: [cumulativePercentChange]}
                allOwnedCryptoPercentChanges.append(newDict)
            else:
                allOwnedCryptoPercentChanges[lenAllOwned - 1][currentCurrency].append(cumulativePercentChange)



        #buy the new cryptocurrency if there was one selected
        if(oldCurrency != currentCurrency) and (currentCurrency != '') and currentCurrency != ownCrypto:
            buyBin(currentCurrency, currentMinute)
            ownCrypto = currentCurrency
            didBuy = 1

            #more output to files about the buying
            #file.write("THIS RUN BOUGHT AT: " + str(currentMinute))
            #file.write("Buying " + str(currentCurrency) + " at price: " + str(priceBought))



        #if you buy increment the buy counter
        if didBuy == 1:
            numBuys += 1
        if didSell == 1:
            numSells += 1


        #holding of the crypto currency for minutes less than the specied max or until one of the restart conditions is met
        # assuming there is a current currency owned
        while(t < PARAMETERS['MAX_TIME_CYCLE'] and RESTART == 0 and RESTART_TN == 0 and RESTART_LOW == 0 and currentCurrency != ''):
            if(t % PARAMETERS['WAIT_FOR_CHECK_FAILURE'] == 0 and t != 0):
                RESTART = checkFailureCondition(currentCurrency, 0, currentMinute, currentMinute+9)

            if(t > PARAMETERS['WAIT_FOR_CHECK_TOO_LOW'] and t % PARAMETERS['WAIT_FOR_CHECK_FAILURE']):
                RESTART_LOW = checkTooLow(currentCurrency, 0, currentMinute, currentMinute+1)

            RESTART_TN = checkTooNegative(currentCurrency, currentMinute)

            #advance the time and currency minute
            t+=1
            currentMinute += 1



        #check the exit immediately condition
        if currentCurrency != '' and currentMinute < realInterval:
            EXIT = checkExitCondition(currentCurrency, currentMinute)

        #if you kept the same crypto as the last cycle stole the percent chnage you have gotten from the last cycle of holding the crypto or from when it was bought
        if(oldCurrency == currentCurrency and currentCurrency != '' or EXIT == 1):

            #get the new price bought and calculate a percent change over this interval of holding the cyrpto
            newPrice = getbinanceprice(currentCurrency, currentMinute)
            cumulativePercentChange = calcPercentChange(priceBought, newPrice)

            #adds the percent change to the list of all the crypto currencies that have been owned over this run
            #more detail in similar code above
            lenAllOwned = len(allOwnedCryptoPercentChanges)

            if lenAllOwned == 0 or currentCurrency not in allOwnedCryptoPercentChanges[lenAllOwned - 1]:
                newDict = {currentCurrency: [cumulativePercentChange]}
                allOwnedCryptoPercentChanges.append(newDict)
            else:
                allOwnedCryptoPercentChanges[lenAllOwned - 1][currentCurrency].append(cumulativePercentChange)


            PARAMETERS['CUMULATIVE_PERCENT_CHANGE'] = cumulativePercentChange
            PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE'] += cumulativePercentChange

            #set the price bought to the new price found for the interval
            priceBought = newPrice

        #keeps tally of the number of times we have not bought total and whether we did or did not buy now
        if oldCurrency == ownCrypto and oldCurrency != '':
            numAbstain = 1
            totalAbstain += 1

        #if no crypto was chosen you wait 5 minutes and start again
        if currentCurrency == '':
            timeHeld = currentMinute - startMinute
            temp = startMinute
            startMinute += 5 + (currentMinute - startMinute)
            endMinute += 5 + (currentMinute - temp)

        #otherwise you reset the current minute and endminute
        else:
            timeHeld = currentMinute - startMinute
            temp = startMinute
            startMinute += (currentMinute - startMinute)
            endMinute += (currentMinute - temp)

        #make a new crypto stats snapshot for analysis of the decision making process
        # startMinute is misleading here. it will be equal to the start of the next cycle not the one that we just walked through
        #file.write("CRYPTOS SEPEARTED " + str(cryptosSeperated))
        #file.write("NUM ABSTAIN "  + str(numAbstain) + '\n')
        #file.write('Did buy ' + str(didBuy) + '\n')
        #file.write('Did sell ' + str(didSell) + '\n')
        #file.write('Bought '+ str(currentCurrency) + '\n')
        #file.write('Sold ' + str(oldCurrency) + '\n')
        #file.write('Own ' + str(ownCrypto) + '\n')
        cryptoRunStats.newStats(statDict, startMinute, didBuy, didSell, currentCurrency, oldCurrency, cryptosSeperated, cycles, timeHeld, numAbstain, owned)
        resetDecisionsStored(cryptosSeperated)



        cycles += 1

    #print to file the final percent changes over the run
    #file.write("Cumulative percent change over the life of all cryptos owneed so far " + str(PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE']))

    #sell if there is a crypto left and increment numSells
    sellBin(currentCurrency)
    numSells += 1


    #set variables of the crypto stat analysis object
    cryptoRunStats.setVal(numBuys, 0)
    cryptoRunStats.setVal(numSells, 1)
    #file.write("NUM SELLS  " + str(numSells)+ '\n')
    cryptoRunStats.setVal(allOwnedCryptoPercentChanges, 2)

    #has the bot do any final calculations
    PARAMETERS['END_MONEY'] = cryptoRunStats.finalCalculations()
    print("FINAL MONEY " + str(PARAMETERS['END_MONEY']))
    #write the analysis to the file
    cryptoRunStats.writeToFile()

    #write back to the param pickle file
    writeParamPickle(PARAMETERS)

    #special print statement used to get the parameters back
    print("LINEBEGIN" + str(PARAMETERS) + "DONEEND")


    file.close()
if __name__ == "__main__":
    main()
