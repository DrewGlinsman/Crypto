# Copyright (c) 2018 A&D
# Keeps database continuously updated with new python data for all 5 categories and all cryptos

import pathlib
import requests
import sqlite3
from sqlite3 import Error
import os


#setup the relative file path
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname + '/', '')

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

#gives the databases 2 hours of data for each datatype
def primeDatabase(connections):

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

    count = 0
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
def create_connection(db_file):
    """ create a database connection to a SQLite database """

    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)

    except Error as e:
        print(e)

    return conn

#closes the passed connection
def close_connection(conn):
    conn.close()

#sets the file path for the databses using the relative file path
def setupdbfiles():
    global dirname

    db_file = os.path.join(dirname + '/', 'databases/current.db')
    print(db_file)

    return db_file

#sets up tables in the database corresponding to each crypto
def setuptables(conn):

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

    try:
        c = conn.cursor()
        c.execute(sql_statement)
    except Error as e:
        print(e)

#creates a row for the specified database and open price row values
def add_open_row(conn, openprices):

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

def main():

    db_file = setupdbfiles()

    connection = create_connection(db_file)

    setuptables(connection)

    primeDatabase(connection)

    cursor = connection.cursor()

    close_connection(connection)

if __name__ == "__main__":
    main()