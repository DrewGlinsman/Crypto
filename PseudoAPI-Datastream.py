# Copyright (c) 2018 A&D
# Keeps database continuously updated with new python data for all 5 categories and all cryptos

import pathlib
import sqlite3
from sqlite3 import Error
import time
import asyncio
import os
import requests
import threading


#setup the relative file path
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname + '/', '')

#the buffer time used to set exactly a minute between the last retrieved priming data and the first new minute of data
buffertimestart = 0

#dictionary that contains all the symbols for the binance API calls
priceSymbols = {'bitcoin': 'BTCUSDT', 'ripple': "XRPBTC",
                'ethereum': 'ETHBTC', 'BCC': 'BCCBTC',
                'LTC': 'LTCBTC', 'Dash': 'DASHBTC',
                'Monero': 'XMRBTC', 'Qtum': 'QTUMBTC', 'ETC': 'ETCBTC',
                'Zcash': 'ZECBTC', 'ADA': 'ADABTC', 'ADX': 'ADXBTC', 'AION' : 'AIONBTC', 'AMB': 'AMBBTC', 'APPC': 'APPCBTC', 'ARK': 'ARKBTC', 'ARN': 'ARNBTC', 'AST': 'ASTBTC', 'BAT': 'BATBTC', 'BCD': 'BCDBTC', 'BCPT': 'BCPTBTC', 'BNB': 'BNBBTC', 'BNT': 'BNTBTC', 'BQX': 'BQXBTC', 'BRD': 'BRDBTC', 'BTS': 'BTSBTC', 'CDT': 'CDTBTC', 'CMT': 'CMTBTC', 'CND': 'CNDBTC', 'DGD': 'DGDBTC', 'DLT': 'DLTBTC', 'DNT': 'DNTBTC', 'EDO': 'EDOBTC', 'ELF': 'ELFBTC', 'ENG': 'ENGBTC', 'ENJ': 'ENJBTC', 'EOS': 'EOSBTC', 'EVX': 'EVXBTC', 'FUEL': 'FUELBTC', 'FUN': 'FUNBTC', 'GAS': 'GASBTC', 'GTO': 'GTOBTC', 'GVT': 'GVTBTC', 'GXS': 'GXSBTC', 'HSR': 'HSRBTC', 'ICN': 'ICNBTC', 'ICX': 'ICXBTC', 'IOTA': "IOTABTC", 'KMD': 'KMDBTC', 'KNC': 'KNCBTC', 'LEND': 'LENDBTC', 'LINK':'LINKBTC', 'LRC':'LRCBTC', 'LSK':'LSKBTC', 'LUN': 'LUNBTC', 'MANA': 'MANABTC', 'MCO': 'MCOBTC', 'MDA': 'MDABTC', 'MOD': 'MODBTC', 'MTH': 'MTHBTC', 'MTL': 'MTLBTC', 'NAV': 'NAVBTC', 'NEBL': 'NEBLBTC', 'NEO': 'NEOBTC', 'NULS': 'NULSBTC', 'OAX': 'OAXBTC', 'OMG': 'OMGBTC', 'OST': 'OSTBTC', 'POE': 'POEBTC', 'POWR': 'POWRBTC', 'PPT': 'PPTBTC', 'QSP': 'QSPBTC', 'RCN': 'RCNBTC', 'RDN': 'RDNBTC', 'REQ': 'REQBTC', 'SALT': 'SALTBTC', 'SNGLS': 'SNGLSBTC', 'SNM': 'SNMBTC', 'SNT': 'SNTBTC', 'STORJ': 'STORJBTC', 'STRAT': 'STRATBTC', 'SUB': 'SUBBTC', 'TNB': 'TNBBTC', 'TNT': 'TNTBTC', 'TRIG': 'TRIGBTC', 'TRX': 'TRXBTC', 'VEN': 'VENBTC', 'VIB': 'VIBBTC', 'VIBE': 'VIBEBTC', 'WABI': 'WABIBTC', 'WAVES': 'WAVESBTC', 'WINGS': 'WINGSBTC', 'WTC': 'WTCBTC', 'XVG': 'XVGBTC', 'XZC': 'XZCBTC', 'YOYO': 'YOYOBTC', 'ZRX': 'ZRXBTC'}

#path to save the different text files in
cryptoPaths = os.path.join(dirname + '/', 'databases')
#makes the directorys in the path variable if they do not exist
pathlib.Path(cryptoPaths).mkdir(parents=True, exist_ok=True)

#two hours in ms
TWO_HOURS = 7200000

#two hours in min
TWO_HOURS_MIN = 120

#one minute in ms
ONE_MIN_MS = 60000

class klinedataThread(threading.Thread):
    def __init__(self, symbol, starttime, endtime):
        """
        :param symbol:
        :param starttime:
        :param endtime:
        """
        threading.Thread.__init__(self)
        self.symbol = symbol
        self.starttime = starttime
        self.endtime = endtime
        self.mindict = {}

    def run(self):
        """
        :return:
        """
        self.mindict.update((asyncio.new_event_loop().run_until_complete(getklinedata(self.symbol, self.starttime, self.endtime))))


    def getmindict(self):
        """
        :return:
        """
        return self.mindict

priceSymbolsLower = {'bitcoin': 'btcusdt', 'ripple': "xrpbtc",
                'ethereum': 'ethbtc', 'bcc': 'bccbtc',
                'ltc': 'ltcbtc', 'dash': 'dashbtc',
                'monero': 'xmrbtc', 'qtum': 'qtumbtc', 'etc': 'etcbtc',
                'zcash': 'zecbtc', 'ada': 'adabtc', 'adx': 'adxbtc', 'aion' : 'aionbtc', 'amb': 'ambbtc', 'appc': 'appcbtc', 'ark': 'arkbtc', 'arn': 'arnbtc', 'ast': 'astbtc', 'bat': 'batbtc', 'bcd': 'bcdbtc', 'bcpt': 'bcptbtc', 'bnb': 'bnbbtc', 'bnt': 'bntbtc', 'bqx': 'bqxbtc', 'brd': 'brdbtc', 'bts': 'btsbtc', 'cdt': 'cdtbtc', 'cmt': 'cmtbtc', 'cnd': 'cndbtc', 'dgd': 'dgdbtc', 'dlt': 'dltbtc', 'dnt': 'dntbtc', 'edo': 'edobtc', 'elf': 'elfbtc', 'eng': 'engbtc', 'enj': 'enjbtc', 'eos': 'eosbtc', 'evx': 'evxbtc', 'fuel': 'fuelbtc', 'fun': 'funbtc', 'gas': 'gasbtc', 'gto': 'gtobtc', 'gvt': 'gvtbtc', 'gxs': 'gxsbtc', 'hsr': 'hsrbtc', 'icn': 'icnbtc', 'icx': 'icxbtc', 'iota': "iotabtc", 'kmd': 'kmdbtc', 'knc': 'kncbtc', 'lend': 'lendbtc', 'link':'linkbtc', 'lrc':'lrcbtc', 'lsk':'lskbtc', 'lun': 'lunbtc', 'mana': 'manabtc', 'mco': 'mcobtc', 'mda': 'mdabtc', 'mod': 'modbtc', 'mth': 'mthbtc', 'mtl': 'mtlbtc', 'nav': 'navbtc', 'nebl': 'neblbtc', 'neo': 'neobtc', 'nuls': 'nulsbtc', 'oax': 'oaxbtc', 'omg': 'omgbtc', 'ost': 'ostbtc', 'poe': 'poebtc', 'powr': 'powrbtc', 'ppt': 'pptbtc', 'qsp': 'qspbtc', 'rcn': 'rcnbtc', 'rdn': 'rdnbtc', 'req': 'reqbtc', 'salt': 'saltbtc', 'sngls': 'snglsbtc', 'snm': 'snmbtc', 'snt': 'sntbtc', 'storj': 'storjbtc', 'strat': 'stratbtc', 'sub': 'subbtc', 'tnb': 'tnbbtc', 'tnt': 'tntbtc', 'trig': 'trigbtc', 'trx': 'trxbtc', 'ven': 'venbtc', 'vib': 'vibbtc', 'vibe': 'vibebtc', 'wabi': 'wabibtc', 'waves': 'wavesbtc', 'wings': 'wingsbtc', 'wtc': 'wtcbtc', 'xvg': 'xvgbtc', 'xzc': 'xzcbtc', 'yoyo': 'yoyobtc', 'zrx': 'zrxbtc'}


symbols = ['btcusdt', "xrpbtc",
                'ethbtc', 'bccbtc',
               'ltcbtc', 'dashbtc',
                'xmrbtc','qtumbtc','etcbtc',
                'zecbtc', 'adabtc', 'adxbtc',  'aionbtc','ambbtc','appcbtc','arkbtc', 'arnbtc',  'astbtc',  'batbtc', 'bcdbtc', 'bcptbtc',  'bnbbtc',  'bntbtc',  'bqxbtc','brdbtc', 'btsbtc',  'cdtbtc', 'cmtbtc', 'cndbtc', 'dgdbtc', 'dltbtc', 'dntbtc',  'edobtc',  'elfbtc','engbtc',  'enjbtc', 'eosbtc', 'evxbtc',  'fuelbtc',  'funbtc',  'gasbtc',  'gtobtc', 'gvtbtc', 'gxsbtc', 'hsrbtc', 'icnbtc', 'icxbtc', "iotabtc", 'kmdbtc', 'kncbtc', 'lendbtc', 'linkbtc', 'lrcbtc', 'lskbtc', 'lunbtc', 'manabtc', 'mcobtc', 'mdabtc', 'modbtc','mthbtc', 'mtlbtc', 'navbtc', 'neblbtc', 'neobtc', 'nulsbtc', 'oaxbtc','omgbtc',  'ostbtc', 'poebtc',  'powrbtc',  'pptbtc',  'qspbtc',  'rcnbtc',  'rdnbtc', 'reqbtc', 'saltbtc', 'snglsbtc', 'snmbtc', 'sntbtc', 'storjbtc', 'stratbtc', 'subbtc',  'tnbbtc',  'tntbtc',  'trigbtc', 'trxbtc',  'venbtc', 'vibbtc', 'vibebtc',  'wabibtc',  'wavesbtc',  'wingsbtc', 'wtcbtc', 'xvgbtc', 'xzcbtc',  'yoyobtc',  'zrxbtc']

lock = threading.Lock()

base = 'wss://stream.binance.com:9443/ws/'

#gran a minute of kline data and return it as a dictionary
async def getklinedata(currency, starttime, endtime):
    """
    :param currency:
    :param starttime:
    :param endtime:
    :return:
    """

    parameters = {'symbol': currency, 'startTime': starttime, 'endTime': endtime, 'interval': '1m'}
    data = requests.get("https://api.binance.com/api/v1/klines", params=parameters)
    data = data.json()
    try:
        return {currency: {'openprice': data[0][1], 'closeprice': data[0][4], 'highprice': data[0][2], 'lowprice': data[0][3], 'volume': data[0][5]}}
    except IndexError:
        print(data)
        quit(0)

#synchronously grab all the minute data for each cryptocurrency, store them in lists, and add the rows of data to their respective datafield
def getcurrentmindata(connection):
    """
    :param connection:
    :return:
    """
    global ONE_MIN_MS

    #list to hold all the threads
    threads = []

    #lists to hold the different data for the cryptos that will be added to the database
    openprices = []
    closeprices = []
    highprices = []
    lowprices = []
    volumes = []

    #dictionary to hold all the returned dictionaries of data
    allmindata = {}

    # starttime and endtime used for api calls
    endtime = requests.get("https://api.binance.com/api/v1/time")
    endtime = endtime.json()
    endtime = endtime['serverTime']
    #the extra 2 is just to make sure that they all give a kline because exactly one minute and some do not register
    starttime = endtime - ONE_MIN_MS + 2

    #iterate through the price symbols dictionary and create a thread to find the crypto data then append the thread to the list of threads
    for key, currencyname in priceSymbols.items():
        thread = klinedataThread(currencyname, starttime, endtime)
        thread.start()
        threads.append(thread)

    #wait for all the threads to finish
    for thread in threads:
        thread.join()
        allmindata.update(thread.getmindict())

    #iterate through the minute data and store them in order in the correct list
    for key, currname in priceSymbols.items():
        openprices.append(allmindata[currname]['openprice'])
        closeprices.append(allmindata[currname]['closeprice'])
        highprices.append(allmindata[currname]['highprice'])
        lowprices.append(allmindata[currname]['lowprice'])
        volumes.append(allmindata[currname]['volume'])

    #add the new row of data to each of the respective database tables
    add_open_row(connection, openprices)
    add_close_row(connection, closeprices)
    add_high_row(connection, highprices)
    add_low_row(connection, lowprices)
    add_volume_row(connection, volumes)

#gives the databases 2 hours of data for each datatype
def primeDatabase(connections):
    """
    :param connections:
    :return:
    """

    global buffertimestart


    #grabbing the starttime of the data desired and the current time (endtime)
    endTime = requests.get("https://api.binance.com/api/v1/time")
    endTime = endTime.json()
    endTime = endTime['serverTime']
    startTime = endTime - TWO_HOURS

    #temporary dictionaries for each of the five types of data
    openpricedict = {}
    closepricedict = {}
    highpricedict = {}
    lowpricedict = {}
    volumedict = {}

    #set up the dicts to be made of lists where the index is the minute associated with the list of values
    # and the values of each list correspond to the currencies in order from price symbols
    # these are made this way to facilitate easy transfer to the tables of the database
    for minute in range(TWO_HOURS_MIN):
        openpricedict.update({minute: []})
        closepricedict.update({minute: []})
        highpricedict.update({minute: []})
        lowpricedict.update({minute: []})
        volumedict.update({minute: []})

    #iterate through the dictionary of price symbols and store the five kinds of data in their corresponding dictionaries
    for key, currencyname in priceSymbols.items():
        #store 2 hours of data for the five categories to prime the database
        parameters = {'symbol': currencyname, 'startTime': startTime, 'endTime': endTime, 'interval': '1m'}
        data = requests.get("https://api.binance.com/api/v1/klines", params=parameters)
        data = data.json()

        #iterate through the 2 hours of data and store it in ascending order (oldest to newest)
        min = 0
        for interval in data:
            openpricedict[min].append(interval[1])
            closepricedict[min].append(interval[4])
            highpricedict[min].append(interval[2])
            lowpricedict[min].append(interval[3])
            volumedict[min].append(interval[5])

            min+=1

    #grabbing the time after the last set of data is stored
    buffertimestart = time.time()

    #add each row of data to the five tables of the database
    for rownum in range(TWO_HOURS_MIN):
        #storre the list of values for the current row (minute) in the format used to create a new table row
        opens = (openpricedict[rownum]);
        closes = (closepricedict[rownum]);
        highs = (highpricedict[rownum]);
        lows = (lowpricedict[rownum]);
        volumes = (volumedict[rownum]);

        #pass the new lists of values to the functions that append them as new rows to each database
        add_open_row(connections, opens)
        add_close_row(connections, closes)
        add_high_row(connections, highs)
        add_low_row(connections, lows)
        add_volume_row(connections, volumes)



#creates a connection with the specified database file
def create_connection_db(db_file):
    """
    :param db_file:
    :return:
    """

    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)

    except Error as e:
        print(e)

    return conn

#closes the passed connection
def close_connection(conn):
    """
    :param conn:
    :return:
    """
    conn.close()

#sets the file path for the databses using the relative file path
def setupdbfiles():
    """
    :return:
    """
    global dirname

    db_file = os.path.join(dirname + '/', 'databases/current.db')
    print(db_file)

    return db_file

#sets up tables in the database corresponding to each crypto
def setuptables(conn):
    """
    :param conn:
    :return:
    """

    #create tables with an integer as the id (in minutes) and a column of real numbers for each crypto

    #table for open prices
    sql_create_table_openprice = """ CREATE TABLE IF NOT EXISTS openprices (
                                        id integer PRIMARY KEY,
                                        BTCUSDT REAL NOT NULL, XRPBTC REAL NOT NULL, ETHBTC REAL NOT NULL, BCCBTC REAL NOT NULL,
                LTCBTC REAL NOT NULL, DASHBTC REAL NOT NULL, XMRBTC REAL NOT NULL, QTUMBTC REAL NOT NULL, ETCBTC REAL NOT NULL,
                ZECBTC REAL NOT NULL, ADABTC REAL NOT NULL, ADXBTC REAL NOT NULL, AIONBTC REAL NOT NULL, AMBBTC REAL NOT NULL,
                APPCBTC REAL NOT NULL, ARKBTC REAL NOT NULL, ARNBTC REAL NOT NULL, ASTBTC REAL NOT NULL, BATBTC REAL NOT NULL,
                BCDBTC REAL NOT NULL, BCPTBTC REAL NOT NULL, BNBBTC REAL NOT NULL, BNTBTC REAL NOT NULL, BQXBTC REAL NOT NULL, 
                BRDBTC REAL NOT NULL, BTSBTC REAL NOT NULL, CDTBTC REAL NOT NULL, CMTBTC REAL NOT NULL, CNDBTC REAL NOT NULL, 
                DGDBTC REAL NOT NULL, DLTBTC REAL NOT NULL, DNTBTC REAL NOT NULL, EDOBTC REAL NOT NULL, 
                ELFBTC REAL NOT NULL, ENGBTC REAL NOT NULL, ENJBTC REAL NOT NULL, EOSBTC REAL NOT NULL, EVXBTC REAL NOT NULL, 
                FUELBTC REAL NOT NULL, FUNBTC REAL NOT NULL, GASBTC REAL NOT NULL, GTOBTC REAL NOT NULL, GVTBTC REAL NOT NULL,
                GXSBTC REAL NOT NULL, HSRBTC REAL NOT NULL, ICNBTC REAL NOT NULL, ICXBTC REAL NOT NULL, IOTABTC REAL NOT NULL, 
                KMDBTC REAL NOT NULL, KNCBTC REAL NOT NULL, LENDBTC REAL NOT NULL, LINKBTC REAL NOT NULL, LRCBTC REAL NOT NULL, 
                LSKBTC REAL NOT NULL, LUNBTC REAL NOT NULL, MANABTC REAL NOT NULL, MCOBTC REAL NOT NULL, MDABTC REAL NOT NULL, 
                MODBTC REAL NOT NULL, MTHBTC REAL NOT NULL, MTLBTC REAL NOT NULL, NAVBTC REAL NOT NULL, NEBLBTC REAL NOT NULL, 
                NEOBTC REAL NOT NULL, NULSBTC REAL NOT NULL, OAXBTC REAL NOT NULL, OMGBTC REAL NOT NULL, OSTBTC REAL NOT NULL, 
                POEBTC REAL NOT NULL, POWRBTC REAL NOT NULL, PPTBTC REAL NOT NULL, QSPBTC REAL NOT NULL, RCNBTC REAL NOT NULL, 
                RDNBTC REAL NOT NULL, REQBTC REAL NOT NULL, SALTBTC REAL NOT NULL, SNGLSBTC REAL NOT NULL, SNMBTC REAL NOT NULL, 
                SNTBTC REAL NOT NULL, STORJBTC REAL NOT NULL, STRATBTC REAL NOT NULL, SUBBTC REAL NOT NULL, TNBBTC REAL NOT NULL, 
                TNTBTC REAL NOT NULL, TRIGBTC REAL NOT NULL, TRXBTC REAL NOT NULL, VENBTC REAL NOT NULL, VIBBTC REAL NOT NULL, 
                VIBEBTC REAL NOT NULL, WABIBTC REAL NOT NULL, WAVESBTC REAL NOT NULL, WINGSBTC REAL NOT NULL, WTCBTC REAL NOT NULL, 
                XVGBTC REAL NOT NULL, XZCBTC REAL NOT NULL, YOYOBTC REAL NOT NULL, ZRXBTC REAL NOT NULL
                ); """

    #table for close prices
    sql_create_table_closeprice = """ CREATE TABLE IF NOT EXISTS closeprices (
                                        id integer PRIMARY KEY,
                                        BTCUSDT REAL NOT NULL, XRPBTC REAL NOT NULL, ETHBTC REAL NOT NULL, BCCBTC REAL NOT NULL,
                LTCBTC REAL NOT NULL, DASHBTC REAL NOT NULL, XMRBTC REAL NOT NULL, QTUMBTC REAL NOT NULL, ETCBTC REAL NOT NULL,
                ZECBTC REAL NOT NULL, ADABTC REAL NOT NULL, ADXBTC REAL NOT NULL, AIONBTC REAL NOT NULL, AMBBTC REAL NOT NULL,
                APPCBTC REAL NOT NULL, ARKBTC REAL NOT NULL, ARNBTC REAL NOT NULL, ASTBTC REAL NOT NULL, BATBTC REAL NOT NULL,
                BCDBTC REAL NOT NULL, BCPTBTC REAL NOT NULL, BNBBTC REAL NOT NULL, BNTBTC REAL NOT NULL, BQXBTC REAL NOT NULL, 
                BRDBTC REAL NOT NULL, BTSBTC REAL NOT NULL, CDTBTC REAL NOT NULL, CMTBTC REAL NOT NULL, CNDBTC REAL NOT NULL, 
                DGDBTC REAL NOT NULL, DLTBTC REAL NOT NULL, DNTBTC REAL NOT NULL, EDOBTC REAL NOT NULL, 
                ELFBTC REAL NOT NULL, ENGBTC REAL NOT NULL, ENJBTC REAL NOT NULL, EOSBTC REAL NOT NULL, EVXBTC REAL NOT NULL, 
                FUELBTC REAL NOT NULL, FUNBTC REAL NOT NULL, GASBTC REAL NOT NULL, GTOBTC REAL NOT NULL, GVTBTC REAL NOT NULL,
                GXSBTC REAL NOT NULL, HSRBTC REAL NOT NULL, ICNBTC REAL NOT NULL, ICXBTC REAL NOT NULL, IOTABTC REAL NOT NULL, 
                KMDBTC REAL NOT NULL, KNCBTC REAL NOT NULL, LENDBTC REAL NOT NULL, LINKBTC REAL NOT NULL, LRCBTC REAL NOT NULL, 
                LSKBTC REAL NOT NULL, LUNBTC REAL NOT NULL, MANABTC REAL NOT NULL, MCOBTC REAL NOT NULL, MDABTC REAL NOT NULL, 
                MODBTC REAL NOT NULL, MTHBTC REAL NOT NULL, MTLBTC REAL NOT NULL, NAVBTC REAL NOT NULL, NEBLBTC REAL NOT NULL, 
                NEOBTC REAL NOT NULL, NULSBTC REAL NOT NULL, OAXBTC REAL NOT NULL, OMGBTC REAL NOT NULL, OSTBTC REAL NOT NULL, 
                POEBTC REAL NOT NULL, POWRBTC REAL NOT NULL, PPTBTC REAL NOT NULL, QSPBTC REAL NOT NULL, RCNBTC REAL NOT NULL, 
                RDNBTC REAL NOT NULL, REQBTC REAL NOT NULL, SALTBTC REAL NOT NULL, SNGLSBTC REAL NOT NULL, SNMBTC REAL NOT NULL, 
                SNTBTC REAL NOT NULL, STORJBTC REAL NOT NULL, STRATBTC REAL NOT NULL, SUBBTC REAL NOT NULL, TNBBTC REAL NOT NULL, 
                TNTBTC REAL NOT NULL, TRIGBTC REAL NOT NULL, TRXBTC REAL NOT NULL, VENBTC REAL NOT NULL, VIBBTC REAL NOT NULL, 
                VIBEBTC REAL NOT NULL, WABIBTC REAL NOT NULL, WAVESBTC REAL NOT NULL, WINGSBTC REAL NOT NULL, WTCBTC REAL NOT NULL, 
                XVGBTC REAL NOT NULL, XZCBTC REAL NOT NULL, YOYOBTC REAL NOT NULL, ZRXBTC REAL NOT NULL
                ); """

    #table for high prices
    sql_create_table_highprice = """ CREATE TABLE IF NOT EXISTS highprices (
                                        id integer PRIMARY KEY,
                                        BTCUSDT REAL NOT NULL, XRPBTC REAL NOT NULL, ETHBTC REAL NOT NULL, BCCBTC REAL NOT NULL,
                LTCBTC REAL NOT NULL, DASHBTC REAL NOT NULL, XMRBTC REAL NOT NULL, QTUMBTC REAL NOT NULL, ETCBTC REAL NOT NULL,
                ZECBTC REAL NOT NULL, ADABTC REAL NOT NULL, ADXBTC REAL NOT NULL, AIONBTC REAL NOT NULL, AMBBTC REAL NOT NULL,
                APPCBTC REAL NOT NULL, ARKBTC REAL NOT NULL, ARNBTC REAL NOT NULL, ASTBTC REAL NOT NULL, BATBTC REAL NOT NULL,
                BCDBTC REAL NOT NULL, BCPTBTC REAL NOT NULL, BNBBTC REAL NOT NULL, BNTBTC REAL NOT NULL, BQXBTC REAL NOT NULL, 
                BRDBTC REAL NOT NULL, BTSBTC REAL NOT NULL, CDTBTC REAL NOT NULL, CMTBTC REAL NOT NULL, CNDBTC REAL NOT NULL, 
                DGDBTC REAL NOT NULL, DLTBTC REAL NOT NULL, DNTBTC REAL NOT NULL, EDOBTC REAL NOT NULL, 
                ELFBTC REAL NOT NULL, ENGBTC REAL NOT NULL, ENJBTC REAL NOT NULL, EOSBTC REAL NOT NULL, EVXBTC REAL NOT NULL, 
                FUELBTC REAL NOT NULL, FUNBTC REAL NOT NULL, GASBTC REAL NOT NULL, GTOBTC REAL NOT NULL, GVTBTC REAL NOT NULL,
                GXSBTC REAL NOT NULL, HSRBTC REAL NOT NULL, ICNBTC REAL NOT NULL, ICXBTC REAL NOT NULL, IOTABTC REAL NOT NULL, 
                KMDBTC REAL NOT NULL, KNCBTC REAL NOT NULL, LENDBTC REAL NOT NULL, LINKBTC REAL NOT NULL, LRCBTC REAL NOT NULL, 
                LSKBTC REAL NOT NULL, LUNBTC REAL NOT NULL, MANABTC REAL NOT NULL, MCOBTC REAL NOT NULL, MDABTC REAL NOT NULL, 
                MODBTC REAL NOT NULL, MTHBTC REAL NOT NULL, MTLBTC REAL NOT NULL, NAVBTC REAL NOT NULL, NEBLBTC REAL NOT NULL, 
                NEOBTC REAL NOT NULL, NULSBTC REAL NOT NULL, OAXBTC REAL NOT NULL, OMGBTC REAL NOT NULL, OSTBTC REAL NOT NULL, 
                POEBTC REAL NOT NULL, POWRBTC REAL NOT NULL, PPTBTC REAL NOT NULL, QSPBTC REAL NOT NULL, RCNBTC REAL NOT NULL, 
                RDNBTC REAL NOT NULL, REQBTC REAL NOT NULL, SALTBTC REAL NOT NULL, SNGLSBTC REAL NOT NULL, SNMBTC REAL NOT NULL, 
                SNTBTC REAL NOT NULL, STORJBTC REAL NOT NULL, STRATBTC REAL NOT NULL, SUBBTC REAL NOT NULL, TNBBTC REAL NOT NULL, 
                TNTBTC REAL NOT NULL, TRIGBTC REAL NOT NULL, TRXBTC REAL NOT NULL, VENBTC REAL NOT NULL, VIBBTC REAL NOT NULL, 
                VIBEBTC REAL NOT NULL, WABIBTC REAL NOT NULL, WAVESBTC REAL NOT NULL, WINGSBTC REAL NOT NULL, WTCBTC REAL NOT NULL, 
                XVGBTC REAL NOT NULL, XZCBTC REAL NOT NULL, YOYOBTC REAL NOT NULL, ZRXBTC REAL NOT NULL
                ); """

    #table for low prices
    sql_create_table_lowprice = """ CREATE TABLE IF NOT EXISTS lowprices (
                                        id integer PRIMARY KEY,
                                        BTCUSDT REAL NOT NULL, XRPBTC REAL NOT NULL, ETHBTC REAL NOT NULL, BCCBTC REAL NOT NULL,
                LTCBTC REAL NOT NULL, DASHBTC REAL NOT NULL, XMRBTC REAL NOT NULL, QTUMBTC REAL NOT NULL, ETCBTC REAL NOT NULL,
                ZECBTC REAL NOT NULL, ADABTC REAL NOT NULL, ADXBTC REAL NOT NULL, AIONBTC REAL NOT NULL, AMBBTC REAL NOT NULL,
                APPCBTC REAL NOT NULL, ARKBTC REAL NOT NULL, ARNBTC REAL NOT NULL, ASTBTC REAL NOT NULL, BATBTC REAL NOT NULL,
                BCDBTC REAL NOT NULL, BCPTBTC REAL NOT NULL, BNBBTC REAL NOT NULL, BNTBTC REAL NOT NULL, BQXBTC REAL NOT NULL, 
                BRDBTC REAL NOT NULL, BTSBTC REAL NOT NULL, CDTBTC REAL NOT NULL, CMTBTC REAL NOT NULL, CNDBTC REAL NOT NULL, 
                DGDBTC REAL NOT NULL, DLTBTC REAL NOT NULL, DNTBTC REAL NOT NULL, EDOBTC REAL NOT NULL, 
                ELFBTC REAL NOT NULL, ENGBTC REAL NOT NULL, ENJBTC REAL NOT NULL, EOSBTC REAL NOT NULL, EVXBTC REAL NOT NULL, 
                FUELBTC REAL NOT NULL, FUNBTC REAL NOT NULL, GASBTC REAL NOT NULL, GTOBTC REAL NOT NULL, GVTBTC REAL NOT NULL,
                GXSBTC REAL NOT NULL, HSRBTC REAL NOT NULL, ICNBTC REAL NOT NULL, ICXBTC REAL NOT NULL, IOTABTC REAL NOT NULL, 
                KMDBTC REAL NOT NULL, KNCBTC REAL NOT NULL, LENDBTC REAL NOT NULL, LINKBTC REAL NOT NULL, LRCBTC REAL NOT NULL, 
                LSKBTC REAL NOT NULL, LUNBTC REAL NOT NULL, MANABTC REAL NOT NULL, MCOBTC REAL NOT NULL, MDABTC REAL NOT NULL, 
                MODBTC REAL NOT NULL, MTHBTC REAL NOT NULL, MTLBTC REAL NOT NULL, NAVBTC REAL NOT NULL, NEBLBTC REAL NOT NULL, 
                NEOBTC REAL NOT NULL, NULSBTC REAL NOT NULL, OAXBTC REAL NOT NULL, OMGBTC REAL NOT NULL, OSTBTC REAL NOT NULL, 
                POEBTC REAL NOT NULL, POWRBTC REAL NOT NULL, PPTBTC REAL NOT NULL, QSPBTC REAL NOT NULL, RCNBTC REAL NOT NULL, 
                RDNBTC REAL NOT NULL, REQBTC REAL NOT NULL, SALTBTC REAL NOT NULL, SNGLSBTC REAL NOT NULL, SNMBTC REAL NOT NULL, 
                SNTBTC REAL NOT NULL, STORJBTC REAL NOT NULL, STRATBTC REAL NOT NULL, SUBBTC REAL NOT NULL, TNBBTC REAL NOT NULL, 
                TNTBTC REAL NOT NULL, TRIGBTC REAL NOT NULL, TRXBTC REAL NOT NULL, VENBTC REAL NOT NULL, VIBBTC REAL NOT NULL, 
                VIBEBTC REAL NOT NULL, WABIBTC REAL NOT NULL, WAVESBTC REAL NOT NULL, WINGSBTC REAL NOT NULL, WTCBTC REAL NOT NULL, 
                XVGBTC REAL NOT NULL, XZCBTC REAL NOT NULL, YOYOBTC REAL NOT NULL, ZRXBTC REAL NOT NULL
                ); """

    #table for volumes
    sql_create_table_volumes = """ CREATE TABLE IF NOT EXISTS volumes (
                                        id integer PRIMARY KEY,
                                        BTCUSDT REAL NOT NULL, XRPBTC REAL NOT NULL, ETHBTC REAL NOT NULL, BCCBTC REAL NOT NULL,
                LTCBTC REAL NOT NULL, DASHBTC REAL NOT NULL, XMRBTC REAL NOT NULL, QTUMBTC REAL NOT NULL, ETCBTC REAL NOT NULL,
                ZECBTC REAL NOT NULL, ADABTC REAL NOT NULL, ADXBTC REAL NOT NULL, AIONBTC REAL NOT NULL, AMBBTC REAL NOT NULL,
                APPCBTC REAL NOT NULL, ARKBTC REAL NOT NULL, ARNBTC REAL NOT NULL, ASTBTC REAL NOT NULL, BATBTC REAL NOT NULL,
                BCDBTC REAL NOT NULL, BCPTBTC REAL NOT NULL, BNBBTC REAL NOT NULL, BNTBTC REAL NOT NULL, BQXBTC REAL NOT NULL, 
                BRDBTC REAL NOT NULL, BTSBTC REAL NOT NULL, CDTBTC REAL NOT NULL, CMTBTC REAL NOT NULL, CNDBTC REAL NOT NULL, 
                DGDBTC REAL NOT NULL, DLTBTC REAL NOT NULL, DNTBTC REAL NOT NULL, EDOBTC REAL NOT NULL, 
                ELFBTC REAL NOT NULL, ENGBTC REAL NOT NULL, ENJBTC REAL NOT NULL, EOSBTC REAL NOT NULL, EVXBTC REAL NOT NULL, 
                FUELBTC REAL NOT NULL, FUNBTC REAL NOT NULL, GASBTC REAL NOT NULL, GTOBTC REAL NOT NULL, GVTBTC REAL NOT NULL,
                GXSBTC REAL NOT NULL, HSRBTC REAL NOT NULL, ICNBTC REAL NOT NULL, ICXBTC REAL NOT NULL, IOTABTC REAL NOT NULL, 
                KMDBTC REAL NOT NULL, KNCBTC REAL NOT NULL, LENDBTC REAL NOT NULL, LINKBTC REAL NOT NULL, LRCBTC REAL NOT NULL, 
                LSKBTC REAL NOT NULL, LUNBTC REAL NOT NULL, MANABTC REAL NOT NULL, MCOBTC REAL NOT NULL, MDABTC REAL NOT NULL, 
                MODBTC REAL NOT NULL, MTHBTC REAL NOT NULL, MTLBTC REAL NOT NULL, NAVBTC REAL NOT NULL, NEBLBTC REAL NOT NULL, 
                NEOBTC REAL NOT NULL, NULSBTC REAL NOT NULL, OAXBTC REAL NOT NULL, OMGBTC REAL NOT NULL, OSTBTC REAL NOT NULL, 
                POEBTC REAL NOT NULL, POWRBTC REAL NOT NULL, PPTBTC REAL NOT NULL, QSPBTC REAL NOT NULL, RCNBTC REAL NOT NULL, 
                RDNBTC REAL NOT NULL, REQBTC REAL NOT NULL, SALTBTC REAL NOT NULL, SNGLSBTC REAL NOT NULL, SNMBTC REAL NOT NULL, 
                SNTBTC REAL NOT NULL, STORJBTC REAL NOT NULL, STRATBTC REAL NOT NULL, SUBBTC REAL NOT NULL, TNBBTC REAL NOT NULL, 
                TNTBTC REAL NOT NULL, TRIGBTC REAL NOT NULL, TRXBTC REAL NOT NULL, VENBTC REAL NOT NULL, VIBBTC REAL NOT NULL, 
                VIBEBTC REAL NOT NULL, WABIBTC REAL NOT NULL, WAVESBTC REAL NOT NULL, WINGSBTC REAL NOT NULL, WTCBTC REAL NOT NULL, 
                XVGBTC REAL NOT NULL, XZCBTC REAL NOT NULL, YOYOBTC REAL NOT NULL, ZRXBTC REAL NOT NULL
                ); """

    if conn is not None:
        #setting up the open prices table
        create_table(conn, sql_create_table_openprice)

        #setting up the close prices table
        create_table(conn, sql_create_table_closeprice)

        #setting up the high prices table
        create_table(conn, sql_create_table_highprice)

        #setting up the low prices table
        create_table(conn, sql_create_table_lowprice)

        #setting up the volumes table
        create_table(conn, sql_create_table_volumes)

    else:
        print('Error! There is no database')


#creates the table for the connection and table specified
def create_table(conn, sql_statement):
    """
    :param conn:
    :param sql_statement:
    :return:
    """

    try:
        c = conn.cursor()
        c.execute(sql_statement)
    except Error as e:
        print(e)

#creates a row for the specified database and open price row values
def add_open_row(conn, openprices):
    """
    :param conn:
    :param openprices:
    :return:
    """
    sql = ''' INSERT INTO openprices(BTCUSDT , XRPBTC , ETHBTC , BCCBTC ,
                LTCBTC , DASHBTC , XMRBTC , QTUMBTC , ETCBTC ,
                ZECBTC , ADABTC , ADXBTC , AIONBTC , AMBBTC ,
                APPCBTC , ARKBTC , ARNBTC , ASTBTC , BATBTC ,
                BCDBTC , BCPTBTC , BNBBTC , BNTBTC , BQXBTC , 
                BRDBTC , BTSBTC , CDTBTC , CMTBTC , CNDBTC , 
                DGDBTC , DLTBTC , DNTBTC , EDOBTC , 
                ELFBTC , ENGBTC , ENJBTC , EOSBTC , EVXBTC , 
                FUELBTC , FUNBTC , GASBTC , GTOBTC , GVTBTC ,
                GXSBTC , HSRBTC , ICNBTC , ICXBTC , IOTABTC , 
                KMDBTC , KNCBTC , LENDBTC , LINKBTC , LRCBTC , 
                LSKBTC , LUNBTC , MANABTC , MCOBTC , MDABTC , 
                MODBTC , MTHBTC , MTLBTC , NAVBTC , NEBLBTC , 
                NEOBTC , NULSBTC , OAXBTC , OMGBTC , OSTBTC , 
                POEBTC , POWRBTC , PPTBTC , QSPBTC , RCNBTC , 
                RDNBTC , REQBTC , SALTBTC , SNGLSBTC , SNMBTC , 
                SNTBTC , STORJBTC , STRATBTC , SUBBTC , TNBBTC , 
                TNTBTC , TRIGBTC , TRXBTC , VENBTC , VIBBTC , 
                VIBEBTC , WABIBTC , WAVESBTC , WINGSBTC , WTCBTC , 
                XVGBTC , XZCBTC , YOYOBTC , ZRXBTC )
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, openprices)


# creates a row for the specified database and close price row values
def add_close_row(conn, closeprices):
    """
    :param conn:
    :param closeprices:
    :return:
    """
    sql = ''' INSERT INTO closeprices(BTCUSDT , XRPBTC , ETHBTC , BCCBTC ,
                LTCBTC , DASHBTC , XMRBTC , QTUMBTC , ETCBTC ,
                ZECBTC , ADABTC , ADXBTC , AIONBTC , AMBBTC ,
                APPCBTC , ARKBTC , ARNBTC , ASTBTC , BATBTC ,
                BCDBTC , BCPTBTC , BNBBTC , BNTBTC , BQXBTC , 
                BRDBTC , BTSBTC , CDTBTC , CMTBTC , CNDBTC , 
                DGDBTC , DLTBTC , DNTBTC , EDOBTC , 
                ELFBTC , ENGBTC , ENJBTC , EOSBTC , EVXBTC , 
                FUELBTC , FUNBTC , GASBTC , GTOBTC , GVTBTC ,
                GXSBTC , HSRBTC , ICNBTC , ICXBTC , IOTABTC , 
                KMDBTC , KNCBTC , LENDBTC , LINKBTC , LRCBTC , 
                LSKBTC , LUNBTC , MANABTC , MCOBTC , MDABTC , 
                MODBTC , MTHBTC , MTLBTC , NAVBTC , NEBLBTC , 
                NEOBTC , NULSBTC , OAXBTC , OMGBTC , OSTBTC , 
                POEBTC , POWRBTC , PPTBTC , QSPBTC , RCNBTC , 
                RDNBTC , REQBTC , SALTBTC , SNGLSBTC , SNMBTC , 
                SNTBTC , STORJBTC , STRATBTC , SUBBTC , TNBBTC , 
                TNTBTC , TRIGBTC , TRXBTC , VENBTC , VIBBTC , 
                VIBEBTC , WABIBTC , WAVESBTC , WINGSBTC , WTCBTC , 
                XVGBTC , XZCBTC , YOYOBTC , ZRXBTC )
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, closeprices)


# creates a row for the specified database and high price row values
def add_high_row(conn, highprices):
    """
    :param conn:
    :param highprices:
    :return:
    """
    sql = ''' INSERT INTO highprices(BTCUSDT , XRPBTC , ETHBTC , BCCBTC ,
                LTCBTC , DASHBTC , XMRBTC , QTUMBTC , ETCBTC ,
                ZECBTC , ADABTC , ADXBTC , AIONBTC , AMBBTC ,
                APPCBTC , ARKBTC , ARNBTC , ASTBTC , BATBTC ,
                BCDBTC , BCPTBTC , BNBBTC , BNTBTC , BQXBTC , 
                BRDBTC , BTSBTC , CDTBTC , CMTBTC , CNDBTC , 
                DGDBTC , DLTBTC , DNTBTC , EDOBTC , 
                ELFBTC , ENGBTC , ENJBTC , EOSBTC , EVXBTC , 
                FUELBTC , FUNBTC , GASBTC , GTOBTC , GVTBTC ,
                GXSBTC , HSRBTC , ICNBTC , ICXBTC , IOTABTC , 
                KMDBTC , KNCBTC , LENDBTC , LINKBTC , LRCBTC , 
                LSKBTC , LUNBTC , MANABTC , MCOBTC , MDABTC , 
                MODBTC , MTHBTC , MTLBTC , NAVBTC , NEBLBTC , 
                NEOBTC , NULSBTC , OAXBTC , OMGBTC , OSTBTC , 
                POEBTC , POWRBTC , PPTBTC , QSPBTC , RCNBTC , 
                RDNBTC , REQBTC , SALTBTC , SNGLSBTC , SNMBTC , 
                SNTBTC , STORJBTC , STRATBTC , SUBBTC , TNBBTC , 
                TNTBTC , TRIGBTC , TRXBTC , VENBTC , VIBBTC , 
                VIBEBTC , WABIBTC , WAVESBTC , WINGSBTC , WTCBTC , 
                XVGBTC , XZCBTC , YOYOBTC , ZRXBTC )
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, highprices)


# creates a row for the specified database and low price row values
def add_low_row(conn, lowprices):
    """
    :param conn:
    :param lowprices:
    :return:
    """
    sql = ''' INSERT INTO lowprices(BTCUSDT , XRPBTC , ETHBTC , BCCBTC ,
                LTCBTC , DASHBTC , XMRBTC , QTUMBTC , ETCBTC ,
                ZECBTC , ADABTC , ADXBTC , AIONBTC , AMBBTC ,
                APPCBTC , ARKBTC , ARNBTC , ASTBTC , BATBTC ,
                BCDBTC , BCPTBTC , BNBBTC , BNTBTC , BQXBTC , 
                BRDBTC , BTSBTC , CDTBTC , CMTBTC , CNDBTC , 
                DGDBTC , DLTBTC , DNTBTC , EDOBTC , 
                ELFBTC , ENGBTC , ENJBTC , EOSBTC , EVXBTC , 
                FUELBTC , FUNBTC , GASBTC , GTOBTC , GVTBTC ,
                GXSBTC , HSRBTC , ICNBTC , ICXBTC , IOTABTC , 
                KMDBTC , KNCBTC , LENDBTC , LINKBTC , LRCBTC , 
                LSKBTC , LUNBTC , MANABTC , MCOBTC , MDABTC , 
                MODBTC , MTHBTC , MTLBTC , NAVBTC , NEBLBTC , 
                NEOBTC , NULSBTC , OAXBTC , OMGBTC , OSTBTC , 
                POEBTC , POWRBTC , PPTBTC , QSPBTC , RCNBTC , 
                RDNBTC , REQBTC , SALTBTC , SNGLSBTC , SNMBTC , 
                SNTBTC , STORJBTC , STRATBTC , SUBBTC , TNBBTC , 
                TNTBTC , TRIGBTC , TRXBTC , VENBTC , VIBBTC , 
                VIBEBTC , WABIBTC , WAVESBTC , WINGSBTC , WTCBTC , 
                XVGBTC , XZCBTC , YOYOBTC , ZRXBTC )
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, lowprices)


# creates a row for the specified database and volume price row values
def add_volume_row(conn, volumes):
    """
    :param conn:
    :param volumes:
    :return:
    """
    sql = ''' INSERT INTO volumes(BTCUSDT , XRPBTC , ETHBTC , BCCBTC ,
                LTCBTC , DASHBTC , XMRBTC , QTUMBTC , ETCBTC ,
                ZECBTC , ADABTC , ADXBTC , AIONBTC , AMBBTC ,
                APPCBTC , ARKBTC , ARNBTC , ASTBTC , BATBTC ,
                BCDBTC , BCPTBTC , BNBBTC , BNTBTC , BQXBTC , 
                BRDBTC , BTSBTC , CDTBTC , CMTBTC , CNDBTC , 
                DGDBTC , DLTBTC , DNTBTC , EDOBTC , 
                ELFBTC , ENGBTC , ENJBTC , EOSBTC , EVXBTC , 
                FUELBTC , FUNBTC , GASBTC , GTOBTC , GVTBTC ,
                GXSBTC , HSRBTC , ICNBTC , ICXBTC , IOTABTC , 
                KMDBTC , KNCBTC , LENDBTC , LINKBTC , LRCBTC , 
                LSKBTC , LUNBTC , MANABTC , MCOBTC , MDABTC , 
                MODBTC , MTHBTC , MTLBTC , NAVBTC , NEBLBTC , 
                NEOBTC , NULSBTC , OAXBTC , OMGBTC , OSTBTC , 
                POEBTC , POWRBTC , PPTBTC , QSPBTC , RCNBTC , 
                RDNBTC , REQBTC , SALTBTC , SNGLSBTC , SNMBTC , 
                SNTBTC , STORJBTC , STRATBTC , SUBBTC , TNBBTC , 
                TNTBTC , TRIGBTC , TRXBTC , VENBTC , VIBBTC , 
                VIBEBTC , WABIBTC , WAVESBTC , WINGSBTC , WTCBTC , 
                XVGBTC , XZCBTC , YOYOBTC , ZRXBTC )
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, volumes)

#selects and then prints all the rows for the given connection and table name
#ex: select_all_rows(connection, 'openprices')
def select_all_rows(conn, tablename):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :param tablename: the table name
    :return rows: the rows
    """
    cur = conn.cursor()
    statement = "SELECT * FROM " + tablename
    cur.execute(statement)

    rows = cur.fetchall()

    for row in rows:
        print(row)

    return rows

#grab a specific row of data
#ex: select_by_row(connection, 'openprices', 1)
def select_by_row(conn, tablename, id):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param tablename: the table name
    :param id: the row number
    :return row: the row
    """
    cur = conn.cursor()
    statement = "SELECT * FROM " + tablename + " WHERE id=?"
    cur.execute(statement, (id,))

    rows = cur.fetchall()

    for row in rows:
        print(row)

    return rows

#grab the column of prices for a crypto (can specify a specific row as well)
#ex: select_by_crypto(connection, 'openprices', 'BTCUSDT')
#ex 2: select_by_crypto(connection, 'openprices', 'BTCUSDT', 1)
def select_by_crypto(conn, tablename, crypto, id=-1):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param tablename: the table name
    :param crypto: the name of the crypto you want the data for
    :param id: the row number
    :return row: the row
    """
    cur = conn.cursor()

    if id != -1:
        statement = "SELECT " + crypto + " FROM " + tablename + " WHERE id=?"
        cur.execute(statement, (id,))
    else:
        statement = "SELECT * FROM  " + tablename
        cur.execute(statement)

    rows = cur.fetchall()

    for row in rows:
        print(row)

    return rows

#delete all the rows from the specified table
def delete_rows(conn, tablename):
    """
    :param conn: the connection object to a specific database
    :param tablename: the name of a table in the database
    :return:
    """

    cur = conn.cursor()

    statement = "DELETE FROM " + tablename
    cur.execute(statement)

def main():

    #the number of minutes that have passed
    mins = 0

    #the max number of minutes we will let this datastream run for (should be set by whatever function runs this)
    minmax = 1440

    #the different table names
    tablenames = ['openprices', 'closeprices', 'highprices', 'lowprices', 'volumes']

    db_file = setupdbfiles()

    connection = create_connection_db(db_file)

    setuptables(connection)

    #deleting all rows from each table so the next run begins with a fresh set of data
    for tablename in tablenames:
        delete_rows(connection, tablename)

    connection.commit()

    #set the database up with 240 minutes of data
    primeDatabase(connection)

    #set the mins passed to reflect the new data
    mins+=240

    #waits for one minute - time spent priming database with 2 hours of data so that the next data we grab is a full minute
    #after we have primed
    time.sleep(60.0 - ((time.time() - buffertimestart) % 60.0))

    #commit any changes
    connection.commit()

    #loop that runs every minute to grab another row of data
    starttime = time.time()
    while mins < minmax:
        getcurrentmindata(connection)
        connection.commit()
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))

    #deleting all rows from each table so the next run begins with a fresh set of data
    for tablename in tablenames:
        delete_rows(connection, tablename)

    connection.commit()
    close_connection(connection)

if __name__ == "__main__":
    main()



#OLD FUNCTIONS TO GRAB EVERY STREAM INDEPENDENTLY AS WELL AS ALL THE STREAMS AT ONCE

"""
async def getklinedata(symbol):

    
    :param symbol the currency we want the depth for:
    :return:

    payload return structure
    "e": "kline",     // Event type
    "E": 123456789,   // Event time
    "s": "BNBBTC",    // Symbol
    "k": {
    "t": 123400000, // Kline start time
    "T": 123460000, // Kline close time
    "s": "BNBBTC",  // Symbol
    "i": "1m",      // Interval
    "f": 100,       // First trade ID
    "L": 200,       // Last trade ID
    "o": "0.0010",  // Open price
    "c": "0.0020",  // Close price
    "h": "0.0025",  // High price
    "l": "0.0015",  // Low price
    "v": "1000",    // Base asset volume
    "n": 100,       // Number of trades
    "x": false,     // Is this kline closed?
    "q": "1.0000",  // Quote asset volume
    "V": "500",     // Taker buy base asset volume
    "Q": "0.500",   // Taker buy quote asset volume
    "B": "123456"   // Ignore
  }
}

    

    symbol = symbol
    interval = '1m'
    symbolPath = str(symbol) + "@kline_" + str(interval)
    wsURL = os.path.join(base, symbolPath)

    async with websockets.connect(wsURL) as websocket:

                #set a variable equal to the payload received from the websocket
                kline = await websocket.recv()

                print(kline)
                #recv() returns a string represnetaiton of a dictionary but we need a dictionary so this line changes a string to a dictionary
                #kline = ast.literal_eval(kline)

async def klines():

    interval = '1m'
    allsymbols = ''
    count = 0
    for currency in symbols:
        newpath = str(currency) + "@kline_" + str(interval)
        if count == 0:
            allsymbols += newpath
        else:
            allsymbols += '/' + newpath
        count+=1

    base = 'wss://stream.binance.com:9443/stream?streams='

    wsURL = base + allsymbols

    print(wsURL)

    while True:
        async with websockets.connect(wsURL) as websocket:
            kline = await websocket.recv()
            print(kline)
"""