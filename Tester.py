# Copyright (c) 2018 A&D
# Small tester to measure the effectiveness of the CryptoTrainer
import sys
import time
import os
import pickle
import pathlib
import PriceSymbolsUpdater
import sqlite3
import datetime
import pytz
import requests
from AutoTrader import getbinanceprice
from Generics import PARAMETERS, superParams, priceSymbols
from PseudoAPI_Datastream import select_by_crypto, getNumRows, add_row


basesource = r'wss://stream.binance.com:9443'

# setup the relative file path
dirname = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dirname, '')

# param file name + path
paramPaths = filename

# makes the directorys in the path variable if they do not exist
pathlib.Path(paramPaths).mkdir(parents=True, exist_ok=True)

paramCompletePath = os.path.join(paramPaths, "param.pickle")

# open a file for appending (a). + creates file if does not exist
file = open(paramCompletePath, "w+")


# list of colors that can be copied into the fivethirtyeightfile
colors = ['008fd5', 'fc4f30', 'e5ae38', '6d904f', '8b8b8b', '810f7c', 'f2d4b6', 'f2ae1b', 'f4bbc2', '1209e0', 'b0dlc5', 'dd1d36', '55b4d4', 'ff8f40', 'd35058', '252a8b', '623b19', 'b8962e', 'ff66be', '35679a', '7fffd4', '458b74', '8a2be2', 'ff4040', '8b2323', 'ffd39b', '98f5ff', '53868b', '7fff00', '458b00', 'd2691e', 'ff7256', '6495ed', 'fff8dc', '00ffff', '008b8b', 'ffb90f', '006400', 'caff70', 'ff8c00', 'cd6600', '9932cc', 'bf3eff', '8fbc8f', 'c1ffc1', '9bcd9b', '97ffff', '00ced1', '9400d3', 'ff1493', '8b0a50', '00bfff', '1e90fff', 'b22222', 'ff3030', '228b22', 'ffd700', 'adff2f', 'ff69b4', 'ff6a6a', '7cfc00', 'bfefff', 'ee9572', '20b2aa', 'ff00ff', '66cdaa', '0000cd', 'e066ff', '00fa9a', '191970', 'b3ee3a', 'ff4500', 'ff83fa', 'bbffff', 'ff0000', '4169e1', '54ff9f', '87ceeb', 'a0522d', '836fff', '00ff7f', '008b45', '63b8ff', 'd2b48c', 'ffe1ff', 'ff6347', '8b3626', '00f5ff', '00868b', 'ee82ee', 'ff3e96', 'f5deb3', 'd02090', 'ffff00', '9acd32', '00c5cd', 'ff7256', '00cdcd', 'eead0e', '6e8b3d', 'ee7800', 'b23aee', '483d8b', '00b2ee', 'ee2c2c', 'ffc125', '00cd00', 'ee6aa7', 'ee6363', 'f08080', 'eedd82', 'ffb6c1', '87cefa', 'b03060', '3cb371', '191970', 'c0ff3e', 'db7093', '98fb98', 'ff82ab', 'cdaf95', 'ffbbff', 'b0e0e6']


def main():
    global  priceSymbols
    priceSymbols = PriceSymbolsUpdater.chooseUpdate('binance', list=True)

    #create path to connect to database and create a cursor object to the database
    dirname = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(dirname + '/', '')
    databasePath = os.path.join(dirname + '/', 'databases/' + 'binance.db')
    conn = sqlite3.connect(databasePath)
    cursor = conn.cursor()

    primeDatabase(conn, priceSymbols)

# reads pickle from a file into the passed parameter dictionary
def readParamPickle(directory, idnum):
    """
    :param directory: the path of the pickle file
    :param idnum: the id number for the superparam file
    :return:
    """
    # makes the directorys in the path variable if they do not exist
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
    with open(directory + str(idnum) + "superparam.pkl", "rb") as pickle_in:
        paramDict = pickle.load(pickle_in)

    return paramDict



#builds the logs for the trainer file if none is created and prepares the logs for the evaluator files
# makes a log file for this instance of the trainer that is sorted into a folder by the date it was run
# and its name is just its timestamp
def initdirectories(paramspassed, typedirec='storage'):
    """
    :param paramspassed: the parameters passed from the command line or the superTrainer
    :return:
    """

    directory = "{}{}/{}/{}/{}/{}".format(filename, typedirec, paramspassed['website'], paramspassed['day'], paramspassed['hour']
                                          , paramspassed['min'])

    # makes the directorys in the path variable if they do not exist
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

    #makes the directory of the associated idnum exist if it does not already
    pathlib.Path("{}/{}".format(directory, paramspassed['idnum'])).mkdir(parents=True, exist_ok=True)

    #if this is a training directory then make a class file for the param variaitons to be picked by the evaluator bots
    #and make log directory for each class
    if typedirec == 'training':
        for numclass in range(superParams['classes']):
            # makes the param directory of the associated class exist if it does not already
            pathlib.Path("{}/{}/{}class/variations".format(directory, paramspassed['idnum'], numclass)).mkdir(parents=True, exist_ok=True)

            # makes the log directory of the associated class exist if it does not already
            pathlib.Path("{}/{}/{}class/logs".format(directory, paramspassed['idnum'], numclass)).mkdir(parents=True, exist_ok=True)




#reads the parameters passed
#determines if the trainer is run standalone or by another function
def readParamsPassed():
    """
    :return: param dictionary storing the parameters passed
    """

    if sys.argv[1] == "Alone":
        print("Alone")
    else:
        for line in sys.stdin:
            if line != '':
                params = line.split()
                passedparams = {'website': params[0], 'day': params[1], 'hour': params[2], 'min': params[3],
                 'idnum': int(params[4])}
    print(passedparams)
    return passedparams

# return the number of price symbols
def get_num_prices():
    count = 0
    for key, value in priceSymbols.items():
        count += 1
    print(count)

# reads pickle from a file


def testReadParamPickle():
    global paramPaths
    pickle_in = open(paramPaths + '/' + "param.pkl", "rb")
    testDict = pickle.load(pickle_in)

    print(testDict)



# write pickle to a file
def testWriteParamPickle(testDict=PARAMETERS, idnum=1, website='', day='', super=False):

    if super:
        path = filename + website + '/' + day
        # makes the directorys in the path variable if they do not exist
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        pickle_out = open(path + '/' + idnum + "superparam.pkl", "wb")
    else:
        pickle_out = open(paramPaths + '/' + "param.pkl", "wb")
    pickle.dump(testDict, pickle_out)
    pickle_out.close()

# gets the minimum $$ amounts that still get the accepted level of percentage lost to overbuying and underselling
# levelToAccess is a parameter that determines how many 'levels' of the bids/asks you get from the api 5,10,20 only


def testCalcMinBidandAsk(acceptedLossPercentage, levelsToAccess):
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


# reads in the ttable stored and places it in a pickle file
def readttable(name='ttablesingle'):

    ttabledict = {}

    with open(name, 'r') as infile:
        for line in infile:
            listsplit = line.split()
            degreefreedom = listsplit[0]
            for index in range(len(listsplit)):
                if index == 0:
                    ttabledict.update({listsplit[index]: []})
                else:
                    ttabledict[degreefreedom].append(listsplit[index])

    writedicttopickle(ttabledict, name)

# writes the dict to a pickle file


def writedicttopickle(dict, name):
    pickleFileName = name + ".pkl"

    picklefile = paramPaths + pickleFileName

    with open(picklefile, "wb") as pickle_out:
        pickle.dump(dict, pickle_out)

def getDatabaseValues(numDays, priceSymbols, startHour, startMin):

    #find the current time to compare the delta between when it should have started and now.
    currentTime = datetime.datetime.now(tz = pytz.UTC)
    currentTime = currentTime.astimezone(pytz.timezone('US/Eastern'))

    #find the hour and min deltas
    hourDelta = currentTime.hour - startHour
    minDelta = currentTime.minute - startMin

    #if there was an hour delta convert to min and add to delta
    if(hourDelta > 0):
        hourInMin = hourDelta * 60
        minDelta += hourInMin

    print(minDelta)
    
    #calculate how many days we need to go back in minutes
    daysInMin = 1440 * numDays
    
    #create path to connect to database and create a cursor object to the database
    dirname = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(dirname + '/', '')
    databasePath = os.path.join(dirname + '/', 'databases/' + 'binance.db')
    conn = sqlite3.connect(databasePath)
    cursor = conn.cursor()

    #instantiate all the dictionaries for the various values
    openPriceDict = {}
    closePriceDict = {}
    volumeDict = {}
    highPriceDict = {}
    lowPriceDict = {}

    #find the length of all the dictionaries so we know how far back we have to move the index.
    openPriceLen = getNumRows(cursor, 'openprices')
    closePriceLen = getNumRows(cursor, 'closeprices')
    volumeLen = getNumRows(cursor, 'volumes')
    highPriceLen = getNumRows(cursor, 'highPrices')
    lowPriceLen =  getNumRows(cursor, 'lowPrices')
    
    #iterate through all the cryptos and add their values to the dictionaries with the key value pair of {crypto name: [list of values]}
    for key, crypto in priceSymbols.items():
        #the index starts at the end of the database - whatever time delta there is - 1 because its an index
        index = openPriceLen - minDelta - 1

        #these cryptos are not part of the database yet
        if(crypto == 'KEYBTC' or crypto == 'NASBTC' or crypto == 'MFTBTC' or crypto == 'DENTBTC'):
            continue

        #iterator object to make sure that we go back far enough
        #todo change openPriceLen in the conditional to daysInMin
        iterator = 0
        while(iterator < openPriceLen):
            #if its the first item we are adding use update to add the key value pair with a list of one value
            if(index == openPriceLen - minDelta - 1):
                openPriceDict.update({crypto:[select_by_crypto(conn, 'openprices', crypto, index)]})
                closePriceDict.update({crypto:[select_by_crypto(conn, 'closeprices', crypto, index)]})
                volumeDict.update({crypto:[select_by_crypto(conn, 'volumes', crypto, index)]})
                highPriceDict.update({crypto:[select_by_crypto(conn, 'highprices', crypto, index)]})
                lowPriceDict.update({crypto:[select_by_crypto(conn, 'lowprices', crypto, index)]})

            #after the first value just append to the list in the key value pair
            else:
                openPriceDict[crypto].append(select_by_crypto(conn, 'openprices', crypto, index))
                closePriceDict[crypto].append(select_by_crypto(conn, 'closeprices', crypto, index))
                volumeDict[crypto].append(select_by_crypto(conn, 'volumes', crypto, index))
                highPriceDict[crypto].append(select_by_crypto(conn, 'highprices', crypto, index))
                lowPriceDict[crypto].append(select_by_crypto(conn, 'lowprices', crypto, index))

            #iterate index backwards farther into the database and iterator forwards towards the min total we are supposed to go back
            index -= 1 
            iterator += 1
    
    return openPriceDict, closePriceDict, volumeDict, highPriceDict, lowPriceDict


#gives the databases 2 hours of data for each datatype
def primeDatabase(connections, priceSymbols):
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
    
    while(x <= ONE_DAY_MIN):
        minute = x - ONE_THIRD_MIN
        # set up the dicts to be made of lists where the index is the minute associated with the list of values
        # and the values of each list correspond to the currencies in order from price symbols
        # these are made this way to facilitate easy transfer to the tables of the database
        for minute in range(x):
            openpricedict.update({minute: []})
            closepricedict.update({minute: []})
            highpricedict.update({minute: []})
            lowpricedict.update({minute: []})
            volumedict.update({minute: []}) 

        #iterate through the dictionary of price symbols and store the five kinds of data in their corresponding dictionaries
        for currencyname in priceSymbols:
            #store 2 hours of data for the five categories to prime the database
            parameters = {'symbol': currencyname, 'startTime': startTime, 'endTime': endTime, 'interval': '1m'}
            data = requests.get("https://api.binance.com/api/v1/klines", params=parameters)
            data = data.json()

            #iterate through the 2 hours of data and store it in ascending order (oldest to newest)
            min = x - ONE_THIRD_MIN

            for interval in data:
                openpricedict[min].append(interval[1])
                closepricedict[min].append(interval[4])
                highpricedict[min].append(interval[2])
                lowpricedict[min].append(interval[3])
                volumedict[min].append(interval[5])

                min+=1

        x += ONE_THIRD_MIN
        endTime = startTime
        startTime -= ONE_THIRD_DAY
    
    print('Open Price Dict: {}, Close Price Dict: {}, High Price Dict: {}, Low Price Dict: {}, Volume Dict: {}'.format(len(openpricedict), len(closepricedict), len(highpricedict), len(lowpricedict), len(volumedict)))

    
    #grabbing the time after the last set of data is stored
    buffertimestart = time.time()

    #add each row of data to the five tables of the database
    for rownum in range(ONE_DAY_MIN):
        #storre the list of values for the current row (minute) in the format used to create a new table row
        opens = (openpricedict[rownum]);
        closes = (closepricedict[rownum]);
        highs = (highpricedict[rownum]);
        lows = (lowpricedict[rownum]);
        volumes = (volumedict[rownum]);

        #pass the new lists of values to the functions that append them as new rows to each database
        add_row(connections, 'openprices', opens, priceSymbols)
        add_row(connections, 'closeprices', closes, priceSymbols)
        add_row(connections, 'highprices', highs, priceSymbols)
        add_row(connections, 'lowprices', lows, priceSymbols)
        add_row(connections, 'volumes', volumes, priceSymbols)
    
    

if __name__ == "__main__":
    main()
