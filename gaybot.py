import requests
import hmac
import hashlib
import time
import math
import datetime
import os.path

from multiprocessing import Pool

try:
    from urlib import urlencode

except ImportError:
    from urllib.parse import urlencode


#Directory path (r makes this a raw string so the backslashes do not cause a compiler issue
logPaths = r'C:\Users\katso\Desktop\CryptoBot\Crypto-master\Logs'

#log file name + path
logCompletePath = os.path.join(logPaths, "log.txt")

#open a file for appending (a). + creates file if does not exist
file = open(logCompletePath, "a+")




priceSymbols = {'bitcoin': 'BTCUSDT', 'ripple': "XRPBTC",
                'ethereum': 'ETHBTC', 'BCC': 'BCCBTC',
                'LTC': 'LTCBTC', 'Dash': 'DASHBTC',
                'Monero': 'XMRBTC', 'Qtum': 'QTUMBTC', 'ETC': 'ETCBTC',
                'Zcash': 'ZECBTC', 'ADA': 'ADABTC', 'ADX': 'ADXBTC', 'AION' : 'AIONBTC', 'AMB': 'AMBBTC', 'APPC': 'APPCBTC', 'ARK': 'ARKBTC', 'ARN': 'ARNBTC', 'AST': 'ASTBTC', 'BAT': 'BATBTC', 'BCD': 'BCDBTC', 'BCPT': 'BCPTBTC', 'BNB': 'BNBBTC', 'BNT': 'BNTBTC', 'BQX': 'BQXBTC', 'BRD': 'BRDBTC', 'BTS': 'BTSBTC', 'CDT': 'CDTBTC', 'CMT': 'CMTBTC', 'CND': 'CNDBTC', 'CTR':'CTRBTC', 'DGD': 'DGDBTC', 'DLT': 'DLTBTC', 'DNT': 'DNTBTC', 'EDO': 'EDOBTC', 'ELF': 'ELFBTC', 'ENG': 'ENGBTC', 'ENJ': 'ENJBTC', 'EOS': 'EOSBTC', 'EVX': 'EVXBTC', 'FUEL': 'FUELBTC', 'FUN': 'FUNBTC', 'GAS': 'GASBTC', 'GTO': 'GTOBTC', 'GVT': 'GVTBTC', 'GXS': 'GXSBTC', 'HSR': 'HSRBTC', 'ICN': 'ICNBTC', 'ICX': 'ICXBTC', 'IOTA': "IOTABTC", 'KMD': 'KMDBTC', 'KNC': 'KNCBTC', 'LEND': 'LENDBTC', 'LINK':'LINKBTC', 'LRC':'LRCBTC', 'LSK':'LSKBTC', 'LUN': 'LUNBTC', 'MANA': 'MANABTC', 'MCO': 'MCOBTC', 'MDA': 'MDABTC', 'MOD': 'MODBTC', 'MTH': 'MTHBTC', 'MTL': 'MTLBTC', 'NAV': 'NAVBTC', 'NEBL': 'NEBLBTC', 'NEO': 'NEOBTC', 'NULS': 'NULSBTC', 'OAX': 'OAXBTC', 'OMG': 'OMGBTC', 'OST': 'OSTBTC', 'POE': 'POEBTC', 'POWR': 'POWRBTC', 'PPT': 'PPTBTC', 'QSP': 'QSPBTC', 'RCN': 'RCNBTC', 'RDN': 'RDNBTC', 'REQ': 'REQBTC', 'SALT': 'SALTBTC', 'SNGLS': 'SNGLSBTC', 'SNM': 'SNMBTC', 'SNT': 'SNTBTC', 'STORJ': 'STORJBTC', 'STRAT': 'STRATBTC', 'SUB': 'SUBBTC', 'TNB': 'TNBBTC', 'TNT': 'TNTBTC', 'TRIG': 'TRIGBTC', 'TRX': 'TRXBTC', 'VEN': 'VENBTC', 'VIB': 'VIBBTC', 'VIBE': 'VIBEBTC', 'WABI': 'WABIBTC', 'WAVES': 'WAVESBTC', 'WINGS': 'WINGSBTC', 'WTC': 'WTCBTC', 'XVG': 'XVGBTC', 'XZC': 'XZCBTC', 'YOYO': 'YOYOBTC', 'ZRX': 'ZRXBTC'}

api_key = '7WzDy6Hw7HBozQiR1UEpWMgdpzAKQ3ZUSBX6QMra723KO4ot6iAQykbqtqM4hL7Y'

secret_key = 'cHFo1FUc4zRgydNpTDip51S2s12yd7SKe65LS96AgrUxfm8B5Q7HgQcJghitSlNo'

percent_to_spend = 1  # CHANGE TO 0.5

minTransactionAmount = {'BTC': 0.003, 'ETH': 0.01, 'Dash': 0.01, 'LTC': 0.01, 'ETC': 0.01, 'XRP': 21, 'BCH': 0.005,
                        'XMR': 0.1, 'ZEC': 0.01, 'QTUM': 0.1}

#dictionary with lists that will hold the % changes for each crypto calculated from the klines data
percentChanges = {'BTCUSDT': [], 'XRPBTC': [],
                'ETHBTC': [], 'BCCBTC': [],
                'LTCBTC': [], 'DASHBTC': [],
                'XMRBTC': [], 'QTUMBTC': [], 'ETCBTC': [],
                'ZECBTC': [], 'ADABTC': [], 'ADXBTC': [], 'AIONBTC' : [], 'AMBBTC': [], 'APPCBTC': [], 'ARKBTC': [], 'ARNBTC': [], 'ASTBTC': [], 'BATBTC': [], 'BCDBTC': [], 'BCPTBTC': [], 'BNBBTC': [], 'BNTBTC': [], 'BQXBTC': [], 'BRDBTC': [], 'BTSBTC': [], 'CDTBTC': [], 'CMTBTC': [], 'CNDBTC': [], 'CTRBTC': [], 'DGDBTC': [], 'DLTBTC': [], 'DNTBTC': [], 'EDOBTC': [], 'ELFBTC': [], 'ENGBTC': [], 'ENJBTC': [], 'EOSBTC': [], 'EVXBTC': [], 'FUELBTC': [], 'FUNBTC': [], 'GASBTC': [], 'GTOBTC': [], 'GVTBTC': [], 'GXSBTC': [], 'HSRBTC': [], 'ICNBTC': [], 'ICXBTC': [], 'IOTABTC': [], 'KMDBTC': [], 'KNCBTC': [], 'LENDBTC': [], 'LINKBTC': [], 'LRCBTC': [], 'LSKBTC': [], 'LUNBTC': [], 'MANABTC': [], 'MCOBTC': [], 'MDABTC': [], 'MODBTC': [], 'MTHBTC': [], 'MTLBTC': [], 'NAVBTC': [], 'NEBLBTC': [], 'NEOBTC': [], 'NULSBTC': [], 'OAXBTC': [], 'OMGBTC': [], 'OSTBTC': [], 'POEBTC': [], 'POWRBTC': [], 'PPTBTC': [], 'QSPBTC': [], 'RCNBTC': [], 'RDNBTC': [], 'REQBTC': [], 'SALTBTC': [], 'SNGLSBTC': [], 'SNMBTC': [], 'SNTBTC': [], 'STORJBTC': [], 'STRATBTC': [], 'SUBBTC': [], 'TNBBTC': [], 'TNTBTC': [], 'TRIGBTC': [], 'TRXBTC': [], 'VENBTC': [], 'VIBBTC': [], 'VIBEBTC': [], 'WABIBTC': [], 'WAVESBTC': [], 'WINGSBTC': [], 'WTCBTC': [], 'XVGBTC': [], 'XZCBTC': [], 'YOYOBTC': [], 'ZRXBTC': []}

volumePercentChanges = {'BTCUSDT': [], 'XRPBTC': [],
                'ETHBTC': [], 'BCCBTC': [],
                'LTCBTC': [], 'DASHBTC': [],
                'XMRBTC': [], 'QTUMBTC': [], 'ETCBTC': [],
                'ZECBTC': [], 'ADABTC': [], 'ADXBTC': [], 'AIONBTC' : [], 'AMBBTC': [], 'APPCBTC': [], 'ARKBTC': [], 'ARNBTC': [], 'ASTBTC': [], 'BATBTC': [], 'BCDBTC': [], 'BCPTBTC': [], 'BNBBTC': [], 'BNTBTC': [], 'BQXBTC': [], 'BRDBTC': [], 'BTSBTC': [], 'CDTBTC': [], 'CMTBTC': [], 'CNDBTC': [], 'CTRBTC': [], 'DGDBTC': [], 'DLTBTC': [], 'DNTBTC': [], 'EDOBTC': [], 'ELFBTC': [], 'ENGBTC': [], 'ENJBTC': [], 'EOSBTC': [], 'EVXBTC': [], 'FUELBTC': [], 'FUNBTC': [], 'GASBTC': [], 'GTOBTC': [], 'GVTBTC': [], 'GXSBTC': [], 'HSRBTC': [], 'ICNBTC': [], 'ICXBTC': [], 'IOTABTC': [], 'KMDBTC': [], 'KNCBTC': [], 'LENDBTC': [], 'LINKBTC': [], 'LRCBTC': [], 'LSKBTC': [], 'LUNBTC': [], 'MANABTC': [], 'MCOBTC': [], 'MDABTC': [], 'MODBTC': [], 'MTHBTC': [], 'MTLBTC': [], 'NAVBTC': [], 'NEBLBTC': [], 'NEOBTC': [], 'NULSBTC': [], 'OAXBTC': [], 'OMGBTC': [], 'OSTBTC': [], 'POEBTC': [], 'POWRBTC': [], 'PPTBTC': [], 'QSPBTC': [], 'RCNBTC': [], 'RDNBTC': [], 'REQBTC': [], 'SALTBTC': [], 'SNGLSBTC': [], 'SNMBTC': [], 'SNTBTC': [], 'STORJBTC': [], 'STRATBTC': [], 'SUBBTC': [], 'TNBBTC': [], 'TNTBTC': [], 'TRIGBTC': [], 'TRXBTC': [], 'VENBTC': [], 'VIBBTC': [], 'VIBEBTC': [], 'WABIBTC': [], 'WAVESBTC': [], 'WINGSBTC': [], 'WTCBTC': [], 'XVGBTC': [], 'XZCBTC': [], 'YOYOBTC': [], 'ZRXBTC': []}


#holds lists of volumes over an interval for each crypto calculated
volumeAmounts = {'BTCUSDT': [], 'XRPBTC': [],
                'ETHBTC': [], 'BCCBTC': [],
                'LTCBTC': [], 'DASHBTC': [],
                'XMRBTC': [], 'QTUMBTC': [], 'ETCBTC': [],
                'ZECBTC': [], 'ADABTC': [], 'ADXBTC': [], 'AIONBTC' : [], 'AMBBTC': [], 'APPCBTC': [], 'ARKBTC': [], 'ARNBTC': [], 'ASTBTC': [], 'BATBTC': [], 'BCDBTC': [], 'BCPTBTC': [], 'BNBBTC': [], 'BNTBTC': [], 'BQXBTC': [], 'BRDBTC': [], 'BTSBTC': [], 'CDTBTC': [], 'CMTBTC': [], 'CNDBTC': [], 'CTRBTC': [], 'DGDBTC': [], 'DLTBTC': [], 'DNTBTC': [], 'EDOBTC': [], 'ELFBTC': [], 'ENGBTC': [], 'ENJBTC': [], 'EOSBTC': [], 'EVXBTC': [], 'FUELBTC': [], 'FUNBTC': [], 'GASBTC': [], 'GTOBTC': [], 'GVTBTC': [], 'GXSBTC': [], 'HSRBTC': [], 'ICNBTC': [], 'ICXBTC': [], 'IOTABTC': [], 'KMDBTC': [], 'KNCBTC': [], 'LENDBTC': [], 'LINKBTC': [], 'LRCBTC': [], 'LSKBTC': [], 'LUNBTC': [], 'MANABTC': [], 'MCOBTC': [], 'MDABTC': [], 'MODBTC': [], 'MTHBTC': [], 'MTLBTC': [], 'NAVBTC': [], 'NEBLBTC': [], 'NEOBTC': [], 'NULSBTC': [], 'OAXBTC': [], 'OMGBTC': [], 'OSTBTC': [], 'POEBTC': [], 'POWRBTC': [], 'PPTBTC': [], 'QSPBTC': [], 'RCNBTC': [], 'RDNBTC': [], 'REQBTC': [], 'SALTBTC': [], 'SNGLSBTC': [], 'SNMBTC': [], 'SNTBTC': [], 'STORJBTC': [], 'STRATBTC': [], 'SUBBTC': [], 'TNBBTC': [], 'TNTBTC': [], 'TRIGBTC': [], 'TRXBTC': [], 'VENBTC': [], 'VIBBTC': [], 'VIBEBTC': [], 'WABIBTC': [], 'WAVESBTC': [], 'WINGSBTC': [], 'WTCBTC': [], 'XVGBTC': [], 'XZCBTC': [], 'YOYOBTC': [], 'ZRXBTC': []}


#special dictionary, houses the % change by hour, the % time spent increasing, and the % of time increasing (weighted)
pricePercentData = {'BTCUSDT': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XRPBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'ETHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'LTCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DASHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'XMRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'QTUMBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ETCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'ZECBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ADABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ADXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'AIONBTC' : {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'AMBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'APPCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ARKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ARNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ASTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BATBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCPTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BNBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BQXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BRDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BTSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CDTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CMTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CNDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CTRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DGDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DLTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EDOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ELFBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ENGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ENJBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EOSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EVXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'FUELBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'FUNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GASBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GTOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GVTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GXSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'HSRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ICNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ICXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'IOTABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'KMDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'KNCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LENDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LINKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LRCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LSKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LUNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MANABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MCOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MDABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MODBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MTHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MTLBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NAVBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NEBLBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NEOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NULSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OAXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OMGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OSTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'POEBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'POWRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'PPTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'QSPBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'RCNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'RDNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'REQBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SALTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNGLSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNMBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'STORJBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'STRATBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SUBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TNBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TRIGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TRXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VENBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VIBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VIBEBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WABIBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WAVESBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WINGSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WTCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XVGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XZCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'YOYOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ZRXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}}

volumePercentData = {'BTCUSDT': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XRPBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'ETHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'LTCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DASHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'XMRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'QTUMBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ETCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0},
                'ZECBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ADABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ADXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'AIONBTC' : {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'AMBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'APPCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ARKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ARNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ASTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BATBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BCPTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BNBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BQXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BRDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'BTSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CDTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CMTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CNDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'CTRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DGDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DLTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'DNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EDOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ELFBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ENGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ENJBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EOSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'EVXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'FUELBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'FUNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GASBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GTOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GVTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'GXSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'HSRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ICNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ICXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'IOTABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'KMDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'KNCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LENDBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LINKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LRCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LSKBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'LUNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MANABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MCOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MDABTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MODBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MTHBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'MTLBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NAVBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NEBLBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NEOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'NULSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OAXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OMGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'OSTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'POEBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'POWRBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'PPTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'QSPBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'RCNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'RDNBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'REQBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SALTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNGLSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNMBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'STORJBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'STRATBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'SUBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TNBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TNTBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TRIGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'TRXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VENBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VIBBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'VIBEBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WABIBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WAVESBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WINGSBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'WTCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XVGBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'XZCBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'YOYOBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}, 'ZRXBTC': {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}}

#stores the calculated weightedMovingAverage

weightedMovingAverage = {'BTCUSDT': [], 'XRPBTC': [],
                'ETHBTC': [], 'BCCBTC': [],
                'LTCBTC': [], 'DASHBTC': [],
                'XMRBTC': [], 'QTUMBTC': [], 'ETCBTC': [],
                'ZECBTC': [], 'ADABTC': [], 'ADXBTC': [], 'AIONBTC' : [], 'AMBBTC': [], 'APPCBTC': [], 'ARKBTC': [], 'ARNBTC': [], 'ASTBTC': [], 'BATBTC': [], 'BCDBTC': [], 'BCPTBTC': [], 'BNBBTC': [], 'BNTBTC': [], 'BQXBTC': [], 'BRDBTC': [], 'BTSBTC': [], 'CDTBTC': [], 'CMTBTC': [], 'CNDBTC': [], 'CTRBTC': [], 'DGDBTC': [], 'DLTBTC': [], 'DNTBTC': [], 'EDOBTC': [], 'ELFBTC': [], 'ENGBTC': [], 'ENJBTC': [], 'EOSBTC': [], 'EVXBTC': [], 'FUELBTC': [], 'FUNBTC': [], 'GASBTC': [], 'GTOBTC': [], 'GVTBTC': [], 'GXSBTC': [], 'HSRBTC': [], 'ICNBTC': [], 'ICXBTC': [], 'IOTABTC': [], 'KMDBTC': [], 'KNCBTC': [], 'LENDBTC': [], 'LINKBTC': [], 'LRCBTC': [], 'LSKBTC': [], 'LUNBTC': [], 'MANABTC': [], 'MCOBTC': [], 'MDABTC': [], 'MODBTC': [], 'MTHBTC': [], 'MTLBTC': [], 'NAVBTC': [], 'NEBLBTC': [], 'NEOBTC': [], 'NULSBTC': [], 'OAXBTC': [], 'OMGBTC': [], 'OSTBTC': [], 'POEBTC': [], 'POWRBTC': [], 'PPTBTC': [], 'QSPBTC': [], 'RCNBTC': [], 'RDNBTC': [], 'REQBTC': [], 'SALTBTC': [], 'SNGLSBTC': [], 'SNMBTC': [], 'SNTBTC': [], 'STORJBTC': [], 'STRATBTC': [], 'SUBBTC': [], 'TNBBTC': [], 'TNTBTC': [], 'TRIGBTC': [], 'TRXBTC': [], 'VENBTC': [], 'VIBBTC': [], 'VIBEBTC': [], 'WABIBTC': [], 'WAVESBTC': [], 'WINGSBTC': [], 'WTCBTC': [], 'XVGBTC': [], 'XZCBTC': [], 'YOYOBTC': [], 'ZRXBTC': []}



#dictionary holds the modified cumulative volume over a period (i.e percent changes change the sign of the volume)

modifiedVolume = {'BTCUSDT': [], 'XRPBTC': [],
                'ETHBTC': [], 'BCCBTC': [],
                'LTCBTC': [], 'DASHBTC': [],
                'XMRBTC': [], 'QTUMBTC': [], 'ETCBTC': [],
                'ZECBTC': [], 'ADABTC': [], 'ADXBTC': [], 'AIONBTC' : [], 'AMBBTC': [], 'APPCBTC': [], 'ARKBTC': [], 'ARNBTC': [], 'ASTBTC': [], 'BATBTC': [], 'BCDBTC': [], 'BCPTBTC': [], 'BNBBTC': [], 'BNTBTC': [], 'BQXBTC': [], 'BRDBTC': [], 'BTSBTC': [], 'CDTBTC': [], 'CMTBTC': [], 'CNDBTC': [], 'CTRBTC': [], 'DGDBTC': [], 'DLTBTC': [], 'DNTBTC': [], 'EDOBTC': [], 'ELFBTC': [], 'ENGBTC': [], 'ENJBTC': [], 'EOSBTC': [], 'EVXBTC': [], 'FUELBTC': [], 'FUNBTC': [], 'GASBTC': [], 'GTOBTC': [], 'GVTBTC': [], 'GXSBTC': [], 'HSRBTC': [], 'ICNBTC': [], 'ICXBTC': [], 'IOTABTC': [], 'KMDBTC': [], 'KNCBTC': [], 'LENDBTC': [], 'LINKBTC': [], 'LRCBTC': [], 'LSKBTC': [], 'LUNBTC': [], 'MANABTC': [], 'MCOBTC': [], 'MDABTC': [], 'MODBTC': [], 'MTHBTC': [], 'MTLBTC': [], 'NAVBTC': [], 'NEBLBTC': [], 'NEOBTC': [], 'NULSBTC': [], 'OAXBTC': [], 'OMGBTC': [], 'OSTBTC': [], 'POEBTC': [], 'POWRBTC': [], 'PPTBTC': [], 'QSPBTC': [], 'RCNBTC': [], 'RDNBTC': [], 'REQBTC': [], 'SALTBTC': [], 'SNGLSBTC': [], 'SNMBTC': [], 'SNTBTC': [], 'STORJBTC': [], 'STRATBTC': [], 'SUBBTC': [], 'TNBBTC': [], 'TNTBTC': [], 'TRIGBTC': [], 'TRXBTC': [], 'VENBTC': [], 'VIBBTC': [], 'VIBEBTC': [], 'WABIBTC': [], 'WAVESBTC': [], 'WINGSBTC': [], 'WTCBTC': [], 'XVGBTC': [], 'XZCBTC': [], 'YOYOBTC': [], 'ZRXBTC': []}


#dictionary to hold the intervals, their symbols, and their time in milliseconds

intervalTypes = { '1m': {'symbol': '1m', 'inMS': 60000},  '3m': {'symbol': '3m', 'inMS': 180000}, '5m': {'symbol': '5m', 'inMS': 300000}, '15m': {'symbol': '15m', 'inMS': 900000}, '30m': {'symbol': '30m', 'inMS': 1800000}, '1h': {'symbol': '1h', 'inMS': 3600000}, '2h': {'symbol': '2h', 'inMS': 7200000}, '4h': {'symbol': '4h', 'inMS': 14400000}, '6h': {'symbol': '6h', 'inMS': 21600000}, '8h': {'symbol': '8h', 'inMS': 28800000}, '12h': {'symbol': '12h', 'inMS': 43200000}, '1d': {'symbol': '1d', 'inMS': 86400000}, '3d': {'symbol': '3d', 'inMS': 259200000}, '1w': {'symbol': '1w' , 'inMS': 604800000}, '1M': {'symbol': '1M', 'inMS': 2629746000}}

#dictionary just to hold the scores calculated for each crypto
scores =  {}

stepsizes = {}

currentCrypto = {}

currencyToTrade = {}

priceList = {}

oldCurrency = ''

currentCurrency = ''

initialBalance = 0.0

currentBalance = 0.0

minimumPercentIncrease = 5.0

zeroCounter = 0

minimumScore = 1.0

minimumCumulativeMovingAverage = 0.6

#the maximum percentage decrease over 1 minute period allowed

MAX_DECREASE = -10

#number in seconds that determines the maximum time a crypto will be held without checkin for a potential switch
MAX_TIME_CYCLE = 3600

#number of cycles run with each run of this bot
MAX_CYCLES = 24

#max percent change before the bot sells and exits
MAX_PERCENT_CHANGE = 15

#weight to make negative numbers worse than positive.
NEGATIVE_WEIGHT = 1.5 #best run had this at 1.3


#0 is false, 1 is true
RESTART = 0
RESTART_TN = 0
RESTART_LOW = 0
EXIT = 0

#calculated cumulative percentChange with the current crypto
cumulativePercentChange = 0.0

#calcaulated cumulative percentChange with the whole run
cumulativePercentChangeStore = 0.0

#price each crypto is bought at
priceBought = 0.0

#scale of the balance quantity to spend
PERCENT_QUANTITY_TO_SPEND = .9

#weight applied to each slot for both periods increasing and periods of increasing volume.
SLOT_WEIGHT = .1

#weights applied to change value of the calculated values
TIME_INCREASING_MODIFIER = 10

VOLUME_INCREASING_MODIFIER = .01

PERCENT_BY_HOUR_MODIFIER = 1

VOLUME_PERCENT_BY_HOUR_MODIFIER = 0.1 #best run had this at .1


MODIFIED_VOLUME_MODIFIER = 0 #best run had this at 0

#modifier for the lowest the price can be before it is sold

FLOOR_PRICE_MODIFIER = 1.005

#time waiting fields
WAIT_FOR_CHECK_FAILURE = 300

WAIT_FOR_CHECK_TOO_LOW = 600


def getBalance(symbol):
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

def buyBin(symbol):
    global priceBought

    timestamp = int(time.time() * 1000)
    balance = getBalance('BTC')

    #multiply balance by constant ratio of how much we want to spend
    # and then convert quantity from BTC price to amount of coin
    balancetospend = float(balance) * percent_to_spend
    ratio = getbinanceprice(symbol)

    priceBought = ratio


    #mark item as the current crypto being traded and save the buy price at for failure condition
    entry = {symbol:{'buyPrice': ratio, 'timestamp': timestamp}}
    currentCrypto.clear()
    currentCrypto.update(entry)
    quantity = balancetospend / float(ratio) * PERCENT_QUANTITY_TO_SPEND

    # set the step size for the given coin
    stepsize = stepsizes[symbol]
    print("Stepsize of " + symbol + " is " + stepsize + "\n")
    file.write("Stepsize of " + symbol + " is " + stepsize + "\n")
    # making the quantity to buy
    print("Balance: " + str(balance))
    file.write("Balance: " + str(balance) + "\n")
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

    print('Quantity to buy: ' + str(quantity) + 'of' + symbol)
    file.write('Quantity to buy: ' + str(quantity) + 'of' + symbol + "\n")

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


def sellBin(symbol):
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


    #getting rid of the BTC part of the crypto asset name
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
    print("Stepsize of " + symbol + " is " + stepsize)
    file.write("Stepsize of " + str(symbol) + " is " + str(stepsize) + "\n")
    #making the quantity to sell
    print("Balance: " + str(balance))
    file.write("Balance: " + str(balance) + "\n")
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

    print('Quantity to sell: ' + str(quantity) + ' of ' + symbol + ' with stepsize ' + stepsize)
    file.write('Quantity to sell: ' + str(quantity) + ' of ' + symbol + ' with stepsize ' + stepsize + "\n")

    #building the sell query string
    sellParameters = {'symbol': symbol, 'side': 'sell', 'type': 'market', 'timestamp': timestamp, 'quantity': quantity}
    query = urlencode(sorted(sellParameters.items()))
    signature = hmac.new(secret_key.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    query += "&signature=" + signature

    #actually selling
   # testSell = requests.post("https://api.binance.com/api/v3/order?" + query, headers=headers)
   # print(testSell.text)
   # file.write(testSell.text + "\n")


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
        if(float(stepsize) != 1 and float(stepsize) != 0.1 and float(stepsize) != 0.01 and float(stepsize) != 0.001 and 'BTC' in symbol and 'USDT' not in symbol):
            print(str(symbol) + " stepsize: " + stepsize)
            file.write(str(symbol) + " stepsize: " + stepsize + "\n")

#calculates the cumulative moving average over the specified interval for a crypto currency
def setWeightedMovingAverage(currency, interval, starttime, endtime):
    parameters = {"symbol": currency, "interval": interval, 'startTime': starttime, 'endTime': endtime}
    data = requests.get("https://api.binance.com/api/v1/klines", params=parameters)
    data = data.json()

    slots = getLastSlot(interval, starttime, endtime) + 1
    cumulativePrice = 0.0

    if data == []:
        return 0

    for value in data:
       startPrice = value[1]
       endPrice = value[4]
       change = calcPercentChange(startPrice, endPrice)

       cumulativePrice += change


    cumulativePrice = (cumulativePrice / slots) * 100

    print("For " + str(currency) + " the average was " + str(cumulativePrice))

    return cumulativePrice


#gets the cumulative volume over a period and scales it based on the currency's price
def getVolume(interval, starttime, endtime, currency):
    parameters = {"symbol": currency, "interval": interval, 'startTime': starttime, 'endTime': endtime}
    data = requests.get("https://api.binance.com/api/v1/klines", params=parameters)
    data = data.json()
    slots = 0
    volume = 0

    for value in data:
        slots += 1
        fuckthis = float(value[5])
        fuckthis = int(fuckthis)
        volume += fuckthis
    volume *= float(getbinanceprice(currency))
    return volume


#grabs the list of volumes over the interval and percent changes over the interal
#then interates through and calculates a cumulative volume where the volume is considered negative
#when the percent change was negative and positive when the percent change was positive
def getModifiedVolume(currency):
    oldVolume = 0
    percentChangesList = percentChanges[currency]
    volumeAmountList = volumeAmounts[currency]
    currentSlot = 0
    volumeModifier = getbinanceprice(currency)

    for i in volumeAmountList:
        percentChangeScale = (percentChangesList[currentSlot] / 100)

        #NOTE: can change back to normal if this doesnt work
        if(percentChangesList[currentSlot] < 0):
            oldVolume += float(i) * -1 * (1 + percentChangeScale) * NEGATIVE_WEIGHT
            oldVolume += float(i) * (-1 * percentChangeScale)
        if(percentChangesList[currentSlot] > 0):
            oldVolume += float(i) * (1 - percentChangeScale)
            oldVolume += float(i) * -1 *(percentChangeScale) * NEGATIVE_WEIGHT
        currentSlot += 1

    #print("For crypto "  + str(currency))
    #print ("Volume before modification " + str(oldVolume))
    #print ("Volume after modification " + str(float(oldVolume) * float(volumeModifier)))
    return float(oldVolume) # * float(volumeModifier)


def getbinanceprice(currency):
    #getting the aggregate trade data and finding one price to return
    binData = requests.get("https://api.binance.com/api/v1/ticker/allPrices")
    binData = binData.json()
    for value in binData:
        if(value["symbol"] == currency):
            binPrice = value["price"]

            break;
    print("Price: " + str(binPrice))


    return binPrice

def pickCrypto():
    #iterates through our dictionary of every price symbol and find the percent change through api
    startTime = int(time.time()*1000)
    for key, value in priceSymbols.items():
        parameter = {'symbol': value}
        percentChange = requests.get("https://api.binance.com/api/v1/ticker/24hr", params=parameter)
        percentChange = percentChange.json()["priceChangePercent"]

        #checks to see if the percent change is above a threshold

        if (float(percentChange) >= float(minimumPercentIncrease)):
            entry = {value: percentChange}
            currencyToTrade.update(entry)
    endTime = int(time.time()*1000)
    realTime = startTime - endTime
    print(str(realTime))


    #interval based on this from binance API
    #     m -> minutes;     h -> hours;     d -> days;     w -> weeks;    M -> months
    #  1m  3m   5m  15m  30m  1h 2h 4h 6h 8h  12h  1d   3d  1w   1M
    # method used to update price lists on past hour of trends

def updateCrypto(interval, starttime, endtime):

    for key,value in priceSymbols.items():
        parameter = {'symbol': value, 'interval': interval, 'startTime': starttime, 'endTime': endtime}
        percentChange = requests.get("https://api.binance.com/api/v1/klines", params=parameter)
        percentChange = percentChange.json()

        lastSlot = getLastSlot(interval, starttime, endtime)

        if percentChange == []:
            lastSlot = 0
        counter = 0

        for i in percentChange:
            counter+=1
        if counter != (int(lastSlot) + 1):
            print("Last Slot is: " + str(lastSlot))
            print("Counter " + str(counter))

        #calculate the percent change over the whole hour and store
        openPrice = percentChange[0][1]
        closePrice = percentChange[int(lastSlot)][4]
        pricePercentData[value]['percentbyhour'] = calcPercentChange(openPrice, closePrice)
        print('{} open {} close {} % change {}'.format(value, openPrice, closePrice, pricePercentData[value]['percentbyhour']))
        openVolume = percentChange[0][5]
        closeVolume = percentChange[int(lastSlot)][5]
        volumePercentData[value]['percentbyhour'] = calcPercentChange(openVolume, closeVolume)
        #print(value + " volume % " + str(volumePercentData[value]['percentbyhour']))
        #calculate the percentage change between the minute intervals and store
        #reset the list of stored percentages so a fresh list is stored
        percentChanges[value] = []
        for i in percentChange:
            percentChanges[value].append(calcPercentChange(i[1], i[4]))
        #print(str(value) + ' % percent changes ' + str(percentChanges[value]))


        volumeAmounts[value] = []
        volumePercentChanges[value] = []
        #grabs and stores the volume from the first two intervals that are skipped in the for loop below
        volumeAmounts[value].append(percentChange[0][5])
        volumeAmounts[value].append(percentChange[1][5])




        for i in range(2, len(percentChange)):
           # print("Old Volume: " + percentChange[i-1][5] + " New Volume: " + percentChange[i][5])
           #print("CURRENT PERCENT CHANGE: " + str(calcPercentChange(percentChange[i-1][5],percentChange[i][5])) + "START VOLUME: " + str(percentChange[i-1][5]) + " END VOLUME: " + str(percentChange[i][5]))
           volumePercentChanges[value].append(calcPercentChange(percentChange[i-1][5], percentChange[i][5]))
           volumeAmounts[value].append(percentChange[i][5])

        #print(" LENGTH OF PERCENT CHANGES " + str(len(percentChanges)) + ' LENGTH OF VOLUME AMOUNTS ' + str(len(volumeAmounts)))

        #calculate and store the % time increasing for volume and percent
        pricePercentData[value]['timeIncreasing'] = getTimeIncreasing(0, value)
        pricePercentData[value]['weightedtimeIncreasing'] = getTimeIncreasing(1, value)

        volumePercentData[value]['timeIncreasing'] = getVolumeTimeIncreasing(0, value)
        volumePercentData[value]['weightedtimeIncreasing'] = getVolumeTimeIncreasing(1, value)

        modifiedVolume[value] = []
        #get the modified volume changes
        modifiedVolume[value] = getModifiedVolume(value)
       # print(value + " modified volume" + str(modifiedVolume[value]))

        #print(str(value))
        #print("Volume Time Increasing: " + str(volumePercentData[value]["timeIncreasing"]))
        #print("Weighted Volume Time Increasing: " + str(volumePercentData[value]["timeIncreasing"]))
       # print("Percent Change by hour: " + str(volumePercentData[value]['percentbyhour']))
        #print (str(value) + ' % time increasing ' + str(pricePercentData[value]['timeIncreasing']))
       # print(str(value) + ' % time increasing weighted ' + str(pricePercentData[value]['weightedtimeIncreasing']))

        #use the calculations to get a score
        calc_score = getScore(value)
        new_score = {value: calc_score}
        scores.update(new_score)

        endtt = int(time.time() * 1000)
        startt = endtt - intervalTypes['4h']['inMS']
        weightedMovingAverage[value] = setWeightedMovingAverage(value, intervalTypes['1m']['symbol'], startt, endtt)

   # print("HERE ARE THE MODIFIED VOLUMES" + str(modifiedVolume))

    for key, value in scores.items():
        if(value > minimumScore):
            entry = {key: value}
            currencyToTrade.update(entry)

    print ("OUR LIST OF CRYPTO")
    print(currencyToTrade)
    file.write("OUR LIST OF CRYPTO")
    file.write(str(currencyToTrade))

#caclulates and returns the time spent increasing
#weighted = 0 is false, weighted = 1 is true
def getTimeIncreasing(isWeighted, currency):

    list = percentChanges[currency]
    slots = 0.0
    slots_increasing = 0.0
    positiveCounter = 0
    negativeCounter = 0
    for i in list:
            slots+=1

            #the two if statements only differ in that the second one
            #caclcualtes slots_increasing using a weight
            #that casues positive increases early in the hour to matter less
            #than increases later in the hour

            if float(i) > 0.0 and isWeighted == 0:
              slots_increasing+=1*i
              positiveCounter+=1

            if float(i) < 0.0 and isWeighted == 0:
              slots_increasing += 1 * i * NEGATIVE_WEIGHT
              negativeCounter+=1
            if float(i) > 0.0 and isWeighted == 1:
              slots_increasing+=(1*(slots*SLOT_WEIGHT)*i)
              positiveCounter+=1

            if float(i) < 0.0 and isWeighted == 1:
              slots_increasing += (1*(slots*SLOT_WEIGHT)*i * NEGATIVE_WEIGHT)
              negativeCounter+=1


    return (slots_increasing/slots) * TIME_INCREASING_MODIFIER


#caclulates and returns the time spent increasing for volume
#weighted = 0 is false, weighted = 1 is true
def getVolumeTimeIncreasing(isWeighted, currency):

    list = volumePercentChanges[currency]
    slots = 0.0
    slots_increasing = 0.0
    positiveCounter = 0
    negativeCounter = 0
    for i in list:
            slots+=1

            #the two if statements only differ in that the second one
            #caclcualtes slots_increasing using a weight
            #that casues positive increases early in the hour to matter less
            #than increases later in the hour

            if float(i) > 0.0 and isWeighted == 0:
              slots_increasing+=1*i
              positiveCounter+=1

            if float(i) < 0.0 and isWeighted == 0:
              slots_increasing += 1 * i * NEGATIVE_WEIGHT
              negativeCounter+=1
            if float(i) > 0.0 and isWeighted == 1:
              slots_increasing+=(1*(slots*SLOT_WEIGHT)*i)
              positiveCounter+=1

            if float(i) < 0.0 and isWeighted == 1:
              slots_increasing += (1*(slots*SLOT_WEIGHT)*i * NEGATIVE_WEIGHT)
              negativeCounter+=1


    return (slots_increasing/slots) * VOLUME_INCREASING_MODIFIER

# method to calculate the "score" that crypto get when they are updated by hour
# score is a combination of weighted time increasing and %change over hour.
#calculation should have more factors added
def getScore(symbol):
    new_score = 0

    new_score += (volumePercentData[symbol]['percentbyhour'] * VOLUME_PERCENT_BY_HOUR_MODIFIER)
    new_score += pricePercentData[symbol]['percentbyhour'] * PERCENT_BY_HOUR_MODIFIER

    m = new_score * pricePercentData[symbol]['weightedtimeIncreasing']
    w = new_score + pricePercentData[symbol]['weightedtimeIncreasing']
    c = new_score * pricePercentData[symbol]['timeIncreasing']
    e = new_score + pricePercentData[symbol]['timeIncreasing']
    #print(symbol + ": (BEFORE VOLUME) " + str(w) + " Absolute increasing weight: " + str(e))

    w += volumePercentData[symbol]['weightedtimeIncreasing']
    e += volumePercentData[symbol]['timeIncreasing']
    #print(symbol + ": " + str(w) + " Absolute increasing weight: " + str(e))

    w += modifiedVolume[symbol] * MODIFIED_VOLUME_MODIFIER

    return w



def priceChecker():

    #Compares the two price lists and sets the currencyToBuy to be
    # the coin with the highest score
    maxScore = 0 #moved out of for loop
    for key, value in currencyToTrade.items():
        print("The score of " + key + " is " + str(scores[key]))
        file.write("The score of " + key + " is " + str(scores[key]) + "\n")
        if(maxScore < scores[key] and float(weightedMovingAverage[key]) > float(minimumCumulativeMovingAverage)):
            maxScore = scores[key]
            print("CURRENT HIGH SCORE: The score of " + key + " is " + str(scores[key]))
            file.write("CURRENT HIGH SCORE: The score of " + key + " is " + str(scores[key]) + "\n")
            currencyToBuy = key

    print("Coin with the highest score is " + currencyToBuy + " which is " + str(maxScore))
    file.write("Coin with the highest score is " + currencyToBuy + " which is " + str(maxScore) + "\n")
    return currencyToBuy #potential runtime error if all negative todo


#just calculates the percent change between two values
def calcPercentChange(startVal, endVal):
    if(float(startVal) == 0.0):
        print('ITS ZERO' + str(startVal))
        return float(endVal) * 100.0
    return (((float(endVal) - float(startVal))/float(startVal) ) * 100)


#checks if the current crypto has been decreasing the past five minutes
#if yes it forces a new check to see if there is a better crypto
def checkFailureCondition(currency, timesIncreasing):
    startPriceInterval = 0


    print("New Interval")
    file.write("New Interval")
    #price = getbinanceprice(currency)
    #change = calcPercentChange(currentCrypto[currency]['buyPrice'], price)

    startTime = int(time.time()*1000) - (int(intervalTypes['5m']['inMS']) * 2)
    endTime = int(time.time())*1000

    parameter = {'symbol': currency, 'interval': intervalTypes['1m']['symbol'], 'startTime': startTime, 'endTime': endTime}
    percentChange = requests.get("https://api.binance.com/api/v1/klines", params=parameter)
    percentChange = percentChange.json()

    startPriceInterval = percentChange[0][1]
    timeIncreasingCounter = 0

    for i in percentChange:
        startPrice = i[1]
        endPrice = i[4]
        print("Current Crypto: " + currency + " Start Price: " + str(startPrice) + " End Price: " + str(endPrice))
        file.write("Current Crypto: " + currency + " Start Price: " + str(startPrice) + " End Price: " + str(endPrice))
        percentChange = calcPercentChange(startPrice, endPrice)
        if(percentChange > 0):
            timeIncreasingCounter += 1

    cumulativePercentChange = calcPercentChange(startPriceInterval, endPrice)
    print("Cumulative percent change over THIS INTERVAL " + str(cumulativePercentChange))
    file.write("Cumulative percent change over THIS INTERVAL " + str(cumulativePercentChange))

    print("Times Increasing over the interval: " + str(timeIncreasingCounter))
    file.write("Times Increasing over the interval: " + str(timeIncreasingCounter) + "\n")
    if(timeIncreasingCounter <= timesIncreasing):
        print("DECREASED ALL INTERVALS. RESTART")
        file.write("DECREASED ALL INTERVALS. RESTART")
        return 1

    return 0

#checks whether the function has caused too large of negative decrease the specified interval
def checkTooNegative(symbol):
    startTime = int(time.time()) * 1000 - 60000
    endTime = int(time.time()) * 1000

    parameter = {'symbol': symbol, 'interval': '1m', 'startTime': startTime, 'endTime': endTime}
    percentChange = requests.get("https://api.binance.com/api/v1/klines", params=parameter)
    percentChange = percentChange.json()

    if (percentChange == []):
        return 0


    startPrice = percentChange[0][1]
    endPrice = percentChange[0][4]
    percentChange = calcPercentChange(startPrice, endPrice)

    if(percentChange < MAX_DECREASE):
        print("TOO NEGATIVE. RESTART")
        file.write("TOO NEGATIVE. RESTART")
        return 1

    return 0

def checkExitCondition(currency):
    global priceBought
    currentPrice= getbinanceprice(currency)


    percentChange = calcPercentChange(priceBought, currentPrice)

    if(percentChange >= MAX_PERCENT_CHANGE):
        print("HIT MAX PERCENT CHANGE")
        return 1

    if(percentChange <= -1 * MAX_PERCENT_CHANGE):
        print("HIT MINIMUM PERCENT CHANGE")
        return 1

    return 0

#checks to see if the current currency is too near to its starting point
def checkTooLow(currency, timesIncreasing):
    currentPrice = getbinanceprice(currency)
    floorPrice = FLOOR_PRICE_MODIFIER * 10
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
    difference = endtime - starttime
    intervalInMs = intervalTypes[interval]['inMS']


    numIntervals = difference/intervalInMs


    return numIntervals - 1

#returns whether the specified currency is increasing or decreasing over the interval
# 0 means decreasing, 1 means stable or increasing
def increasingOrDecreasing(currency, interval, starttime, endtime):

    lastSlot = getLastSlot(interval, starttime, endtime)

    parameter = {'symbol': currency, 'interval': interval, 'startTime': starttime, 'endTime': endtime}
    percentChange = requests.get("https://api.binance.com/api/v1/klines", params=parameter)
    print(percentChange.text)
    percentChange = percentChange.json()

    if percentChange == []:
        return 0
    startPrice = percentChange[0][1]
    endPrice = percentChange[int(lastSlot)][4]


    calcPChange = calcPercentChange(startPrice, endPrice)

    if(calcPChange >= 0.0):
        return 1

    return 0


def main():
    global cumulativePercentChangeStore
    global initialBalance
    global RESTART
    global RESTART_TN
    global RESTART_LOW
    global EXIT
    currentCurrency = ''
    priceSold = 0.0
    x = 0
    file.write("HEYYYYYYYYYYYYYYYYY" )

    file.write("\n\n\n\n")
    file.write('------------------------------------------------------------------------------------' + "\n")

    print("Date and Time of Run " + str(datetime.datetime.now()))
    file.write("Date and Time of Run " + str(datetime.datetime.now()))


    """
    #pickCrypto()
    binStepSize()
    endTime = int(time.time() * 1000) - 3600000
    startTime = endTime - 3600000 * 2
    updateCrypto('5m', startTime, endTime)
    priceChecker()
"""

    initialBalance = getBalance('BTC')

    binStepSize()
    while(x < MAX_CYCLES and EXIT == 0):
        t = 0
        RESTART = 0
        RESTART_LOW = 0
        RESTART_TN = 0
        endTime = int(time.time() * 1000)
        startTime = endTime - 3600000

        updateCrypto(intervalTypes['5m']['symbol'], startTime, endTime)


        oldCurrency = currentCurrency
        currentCurrency = priceChecker()


        if(oldCurrency != currentCurrency and oldCurrency != ''):
            sellBin(oldCurrency)
            print("THIS RUN SOLD AT: " + str(datetime.datetime.time(datetime.datetime.now())))
            file.write("THIS RUN SOLD AT: " + str(datetime.datetime.time(datetime.datetime.now())))
        print('2. PRICE BOUGHT ' + str(priceBought))
        if(oldCurrency != currentCurrency):
            buyBin(currentCurrency)
            print("THIS RUN BOUGHT AT: " + str(datetime.datetime.time(datetime.datetime.now())))
            file.write("THIS RUN BOUGHT AT: " + str(datetime.datetime.time(datetime.datetime.now())))

        #while statement is more flexible way to wait for a period of time or a restart
        # restart could be caused by a met failure condition or a met sustained one
        while(t < MAX_TIME_CYCLE and RESTART == 0 and RESTART_TN == 0 and RESTART_LOW == 0):
            time.sleep(1)
           # print("We are here")
            if(t % WAIT_FOR_CHECK_FAILURE == 0 and t != 0):
                RESTART = checkFailureCondition(currentCurrency, 0)

            if(t > WAIT_FOR_CHECK_TOO_LOW and t % WAIT_FOR_CHECK_FAILURE):
                RESTART_LOW = checkTooLow(currentCurrency, 1)

            RESTART_TN = checkTooNegative(currentCurrency)
            t+=1

      #  print("We left")
        priceSold = getbinanceprice(currentCurrency)
        print('Price bought ' + str(priceBought) + ' Price sold ' + str(priceSold))
        cumulativePercentChange = calcPercentChange(priceBought, priceSold)
        cumulativePercentChangeStore += cumulativePercentChange
        print("FINAL percent change over the life of owning this crypto " + str(cumulativePercentChange))
        file.write("FINAL percent change over the life of owning this crypto " + str(cumulativePercentChange))

        print("Cumualtive percent change over the life of all cryptos owneed so far " + str(cumulativePercentChangeStore))
        file.write("Cumualtive percent change over the life of all cryptos owneed so far " + str(cumulativePercentChangeStore))

        EXIT = checkExitCondition(currentCurrency)
        x+=1

    sellBin(currentCurrency)


    file.write('---------------------------||||||||||||||||----------------------------------------' + "\n")
    file.write("\n" + "\n" + "\n")


if __name__ == "__main__":
    main()