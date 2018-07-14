# Copyright (c) 2018 A&D
# Keeps database continuously updated with new python data for all 5 categories and all cryptos

import pathlib
import sqlite3
import time
import asyncio
import os
import requests
import threading
import PriceSymbolsUpdater
import sys
from Generics import datastreamparamspassed


#setup the relative file path
dirname = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dirname + '/', '')

#the buffer time used to set exactly a minute between the last retrieved priming data and the first new minute of data
buffertimestart = 0

#path to save the different text files in
cryptoPaths = os.path.join(dirname + '/', 'databases')
#makes the directorys in the path variable if they do not exist
pathlib.Path(cryptoPaths).mkdir(parents=True, exist_ok=True)

#two hours in ms
TWO_HOURS = 7200000

#two hours in min
TWO_HOURS_MIN = 120

#one day in ms
ONE_DAY = 86400000

#one day in min
ONE_DAY_MIN = 1440

#one third day in ms
ONE_THIRD_DAY = 28800000

#one third day in min
ONE_THIRD_MIN = 480

#one minute in ms
ONE_MIN_MS = 60000

#one second in ms
ONE_SEC_MS = 1000

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
    print(data.text)
    data = data.json()

    print(data)
    try:
        return {currency: {'openprice': data[0][1], 'closeprice': data[0][4], 'highprice': data[0][2], 'lowprice': data[0][3], 'volume': data[0][5]}}
    except IndexError:
        print("Index error " + str(data))
        print(currency)
        quit(0)

#synchronously grab all the minute data for each cryptocurrency, store them in lists, and add the rows of data to their respective datafield
def getcurrentmindata(connection, pricesymbols):
    """
    :param connection:
    :param pricesymbols: the list of crypto names
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
    starttime = endtime - ONE_MIN_MS - ONE_SEC_MS * 2

    #iterate through the price symbols dictionary and create a thread to find the crypto data then append the thread to the list of threads
    for currencyname in pricesymbols:
        thread = klinedataThread(currencyname, starttime, endtime)
        thread.start()
        threads.append(thread)

    #wait for all the threads to finish
    for thread in threads:
        thread.join()
        allmindata.update(thread.getmindict())

    #iterate through the minute data and store them in order in the correct list
    for currname in priceSymbols:
        openprices.append(allmindata[currname]['openprice'])
        closeprices.append(allmindata[currname]['closeprice'])
        highprices.append(allmindata[currname]['highprice'])
        lowprices.append(allmindata[currname]['lowprice'])
        volumes.append(allmindata[currname]['volume'])

    #add the new row of data to each of the respective database tables
    add_row(connection, 'openprices', openprices, priceSymbols)
    add_row(connection, 'closeprices', closeprices, priceSymbols)
    add_row(connection, 'highprices', highprices, priceSymbols)
    add_row(connection, 'lowprices', lowprices, priceSymbols)
    add_row(connection, 'volumes', volumes, priceSymbols)

#gives the databases 2 hours of data for each datatype
def primeDatabase(connections, priceSymbols, params):
    """
    :param connections:
    :param priceSymbols: the price symbols to use
    :return:
    """

    #global buffertimestart

    #one day in ms
    ONE_DAY = 86400000

    #one day in min
    ONE_DAY_MIN = 1440

    #one third day in ms
    ONE_THIRD_DAY = 28800000

    #one third day in min
    ONE_THIRD_MIN = 480

    #one minute in ms
    ONE_MIN_MS = 60000

    #one second in ms
    ONE_SEC_MS = 1000

    #grabbing the starttime of the data desired and the current time (endtime)
    endTime = requests.get("https://api.binance.com/api/v1/time")
    endTime = endTime.json()
    endTime = endTime['serverTime']
    startTime = endTime - ONE_THIRD_DAY

    #temporary dictionaries for each of the five types of data
    openpricedict = {}
    closepricedict = {}
    highpricedict = {}
    lowpricedict = {}
    volumedict = {}

    x = ONE_THIRD_MIN
    
    buffertimestart = time.time()

    # set up the dicts to be made of lists where the index is the minute associated with the list of values
    # and the values of each list correspond to the currencies in order from price symbols
    # these are made this way to facilitate easy transfer to the tables of the database
    for minute in range(params['minutestoprime']):
        openpricedict.update({minute: []})
        closepricedict.update({minute: []})
        highpricedict.update({minute: []})
        lowpricedict.update({minute: []})
        volumedict.update({minute: []}) 

    while(x <= params['minutestoprime']):
        minute = x - ONE_THIRD_MIN

        print('Minute: {}, X: {}'.format(minute, x))
       
        #iterate through the dictionary of price symbols and store the five kinds of data in their corresponding dictionaries
        for currencyname in priceSymbols:
            #store 2 hours of data for the five categories to prime the database
            parameters = {'symbol': currencyname, 'startTime': startTime, 'endTime': endTime, 'interval': '1m'}
            data = requests.get("https://api.binance.com/api/v1/klines", params=parameters)
            data = data.json()

            #iterate through the data and store it in ascending order (oldest to newest)
            minute = x - ONE_THIRD_MIN
            for interval in data:
                openpricedict[minute].append(interval[1])
                closepricedict[minute].append(interval[4])
                highpricedict[minute].append(interval[2])
                lowpricedict[minute].append(interval[3])
                volumedict[minute].append(interval[5])

                minute += 1

        x += ONE_THIRD_MIN
        endTime = startTime
        startTime -= ONE_THIRD_DAY
    
    #grabbing the time after the last set of data is stored
    buffertimeend = time.time()
    
    #calculate the time difference in seconds between when we started and ended priming the database
    secondsTaken = buffertimeend - buffertimestart

    #convert these two to milliseconds so they can be used by binance
    buffertimestart = int(buffertimestart) * 1000
    buffertimeend = int(buffertimeend) * 1000        


    for currencyname in priceSymbols:
        #store the overflow minute data for the five categories to prime the database
        parameters = {'symbol': currencyname, 'startTime': buffertimestart, 'endTime': buffertimeend, 'interval': '1m'}
        data = requests.get("https://api.binance.com/api/v1/klines", params=parameters)
        data = data.json()

        #how many minutes binance says has passed
        binanceMin = len(data)

        #this program takes between 2 and 3 minutes sometimes binance returns 3 so if they returned 3 we need to wait to reflect 3 minutes passing 
        if(len(data) == 3):
            delta = 180 - secondsTaken
            time.sleep(delta)
            secondsTaken = 180

        #add the minutes to prime so that we can add to the end of the dictionary
        binanceMin += params['minutestoprime']

        #if the new keys haven't been created create them
        if(params['minutestoprime'] not in openpricedict):
            for minute in range(params['minutestoprime'], binanceMin):
                openpricedict[minute] = []
                closepricedict[minute] = []
                highpricedict[minute] = []
                lowpricedict[minute] = []
                volumedict[minute] = []

        print('Length returned: {}'.format(len(data)))
        x = 0
        #iterate through and append the actual data to the dictionaries
        for minute in range(params['minutestoprime'], binanceMin):
            openpricedict[minute].append(data[x][1])
            closepricedict[minute].append(data[x][4])
            highpricedict[minute].append(data[x][2])
            lowpricedict[minute].append(data[x][3])
            volumedict[minute].append(data[x][5])

            x += 1
    
    print('exited loop')
    logging.info('Open Price Dict: {}'.format(str(openpricedict)))

    #print('Open Price Dict: {}'.format(openpricedict))
    #add each row of data to the five tables of the database
    for rownum in range(params['minutestoprime']): 
       #storre the list of values for the current row (minute) in the format used to create a new table row
        opens = (openpricedict[rownum]);
        closes = (closepricedict[rownum]);
        highs = (highpricedict[rownum]);
        lows = (lowpricedict[rownum]);
        volumes = (volumedict[rownum]);

        #print('Open Price Dict: {}'.format(opens))

        #pass the new lists of values to the functions that append them as new rows to each database
        add_row(connections, 'openprices', opens, priceSymbols)
        add_row(connections, 'closeprices', closes, priceSymbols)
        add_row(connections, 'highprices', highs, priceSymbols)
        add_row(connections, 'lowprices', lows, priceSymbols)
        add_row(connections, 'volumes', volumes, priceSymbols)
    
    connections.commit()

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
def setupdbfiles(website='binance'):
    """
    :param website: the website being used
    :return:
    """
    global dirname

    db_file = os.path.join(dirname + '/', 'databases/' + website + '.db')
    print(db_file)

    return db_file

#build a string to represent the columnds of a table with all the pricesymbols
def buildBaseTableString(pricesymbols):
    """
    :param pricesymbols: the list of price symbols
    :return: the build string
    """
    buildstring = ""

    for currency in pricesymbols:
        buildstring +=', ' + currency + ' REAL NOT NULL'

    return buildstring

#sets up tables in the database corresponding to each crypto
def setuptables(conn, priceSymbols):
    """
    :param conn: the connection object
    :param priceSymbols: the symbols to make for each column name
    :return:
    """

    baseString = buildBaseTableString(priceSymbols)

    #create tables with an integer as the id (in minutes) and a column of real numbers for each crypto

    #table for open prices
    sql_create_table_openprice = """ CREATE TABLE IF NOT EXISTS openprices (
                                        id integer PRIMARY KEY""" + baseString + """ 
                ); """

    #table for close prices
    sql_create_table_closeprice = """ CREATE TABLE IF NOT EXISTS closeprices (
                                        id integer PRIMARY KEY""" + baseString + """
                ); """

    #table for high prices
    sql_create_table_highprice = """ CREATE TABLE IF NOT EXISTS highprices (
                                        id integer PRIMARY KEY""" + baseString + """
                ); """

    #table for low prices
    sql_create_table_lowprice = """ CREATE TABLE IF NOT EXISTS lowprices (
                                        id integer PRIMARY KEY""" + baseString + """
                ); """

    #table for volumes
    sql_create_table_volumes = """ CREATE TABLE IF NOT EXISTS volumes (
                                        id integer PRIMARY KEY"""+ baseString + """
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

#build a string to be used to add data to a row
def buildAddRow(tablename,  colnames):
    """
    :param tablename:
    :param colnames: the names of the columns in order
    :return:
    """
    numcols = len(colnames)

    buildstring = " INSERT INTO " + tablename + "("

    #add the name of each symbol with a space and comma and space following
    #unless it is the last symbol
    for index in range(numcols):
        if index < numcols - 1:
            buildstring+= colnames[index] + ' , '
        else:
            buildstring+= colnames[index]

    buildstring+= ' ) VALUES('

    #add question marks for each value to be added
    #last question mark is not followed by a comma
    for i in range(numcols):
        if i < numcols - 1:
                buildstring+= '?,'
        else:
            buildstring+='?'

    buildstring +=  ') '

    return buildstring

#creates a row for the specified database, table, with the given list of values
def add_row(conn, tablename, values, colnames):
    """
    :param conn:
    :param tablename:
    :param values: the list of values to be added
    :param colnames: the names of the columns in order
    :return:
    """
    sqlstatement = buildAddRow(tablename, colnames)


    cur = conn.cursor()
    cur.execute(sqlstatement, values)



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

#read in the parameters
def readParams(paramspassed):
    """
    :param paramspassed: the parameters passed to this file
    :return: the updated params passed
    """

    #the number of minutes that have passed
    mins = 0

    #the max number of minutes we will let this datastream run for (should be set by whatever function runs this)
    minmax = 1440


    if len(sys.argv) == 1:
        paramspassed.update({'website': 'binance'})
        paramspassed.update({'mins': mins})
        paramspassed.update({'minmax': minmax})
        paramspassed.update({'hourrstoprime': 0})
        paramspassed.update(({'freshrun': False}))

    elif(sys.argv[1] == 'Alone'):
        paramspassed.update({'website': sys.argv[2]})
        paramspassed.update({'mins': mins})
        paramspassed.update({'minmax': sys.argv[3]})
        paramspassed.update({'hourrstoprime': sys.argv[4]})
        paramspassed.update(({'freshrun': sys.argv[5]}))

    else:
        for line in sys.stdin:
            if line != '':
                # split the passed string into a list seperated by spaces
                listSplits = line.split(' ')

                #loops through the different values split from the input and stores them in a dictionary
                count = 0
                for key, value in paramspassed.items():
                    paramspassed[key] = listSplits[count]
                    count += 1

    return paramspassed

#returns the number of rows of a data base
def getNumRows(cursor, tablename):
    """
    :param cursor: cursor for the database
    :param tablename: the name of the database table
    :return:
    """

    dataCopy = cursor.execute("select count(*) from " + tablename)
    values = dataCopy.fetchone()
    print
    values[0]

def main():
    global priceSymbols

    #read in any passed parameters
    params = readParams(datastreamparamspassed)

    #this price symbols is different and is just a list of the names
    #we also store them so that any file needing the symbols can pull them from storage
    #thus whatever symbols are used in making the table are also used by scripts requesting data from that table
    priceSymbols = PriceSymbolsUpdater.chooseUpdate(params['website'], list=True, store=True)
    #store the price symbols dictionary version as well
    PriceSymbolsUpdater.chooseUpdate(params['website'], list=False,store=True)

    quit()

    #the different table names
    tablenames = ['openprices', 'closeprices', 'highprices', 'lowprices', 'volumes']

    db_file = setupdbfiles()

    connection = create_connection_db(db_file)

    setuptables(connection, priceSymbols)

    connection.commit()

    cursor = connection.cursor()

    if(params['freshrun']):
        for name in tablenames:
            delete_rows(connection, name)
            
        connection.commit()
    

    numRows = getNumRows(cursor, 'openprices')

    if(isinstance(numRows, int)):
        #set the minutes past to be the number of rows already in each table
        params['mins'] = numRows

    #uncommon if you want to prime the database (TODO use to prime with params['hourprime'] = hourstoprime and params['freshrun'] = true

    #set the database up with 240 minutes of data
    primeDatabase(connection, priceSymbols, params)

    #set the mins passed to reflect the new data
    params['mins'] += params['minutestoprime']



    '''
    #waits for one minute - time spent priming database with 2 hours of data so that the next data we grab is a full minute
    #after we have primed
    time.sleep(60.0 - ((time.time() - buffertimestart) % 60.0))

    #commit any changes
    connection.commit()

    #loop that runs every minute to grab another row of data
    starttime = time.time()
    while int(params['mins']) < int(params['minmax']):
        getcurrentmindata(connection, priceSymbols)
        connection.commit()
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))
        params['mins'] +=1
    '''
    connection.commit()
    close_connection(connection)

if __name__ == "__main__":
    main()
