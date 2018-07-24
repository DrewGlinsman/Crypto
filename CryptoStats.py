# Copyright (c) 2018 A&D
#Updates the stored data for static testing and retrieves it

import time
import requests
import os
import pickle
import sys
import pathlib
import PriceSymbolsUpdater
import sqlite3
from Generics import priceSymbols
from PseudoAPI_Datastream import getNumRows, select_by_crypto, select_by_row

#todo figure out if it is better to insert items at front of the lists or to just remake the lists in reverse order



#dictionarys to store the data after its read in from a text file.
cryptoOpenPriceData = {}
cryptoClosePriceData = {}
cryptoVolumeData = {}
cryptoHighData = {}
cryptoLowData = {}
stepsize = {}

#setup the relative file path
dirname = os.path.dirname(os.path.realpath(__file__))

#path to save the different text files in
cryptoPaths = os.path.join(dirname + '/', 'CryptoData')

#makes the directorys in the path variable if they do not exist
pathlib.Path(cryptoPaths).mkdir(parents=True, exist_ok=True)

logPath = os.path.join(dirname + '/', 'CryptoDataDebug.txt')


file = open(logPath, "w")

#one day in ms
ONE_DAY = 86400000
ONE_THIRD_DAY = 28800000
COUNT = 3

def getDataDatabase(startMinuteBack, endMinuteBack):
    """
    :param startMinuteBack: first minute of the interval you want
    :param endMinuteBack: end minute of the interval desired
    :return:
    """
    global priceSymbols

    priceSymbols = PriceSymbolsUpdater.chooseUpdate('binance')

    #code for writing the values into three text files for each crypto: an open price, close price, and volume file.
    dirname = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(dirname + '/', '')
    databasePath = os.path.join(dirname + '/', 'databases/' + 'binance.db')
    conn = sqlite3.connect(databasePath)
    cur = conn.cursor()

    openPriceDict = {}
    closePriceDict = {}
    volumeDict = {}
    highPriceDict = {}
    lowPriceDict = {}

    length = getNumRows(cur, 'openprices')
    print(length)

    startIndex = length - startMinuteBack - 1
    endIndex = length - endMinuteBack - 1
    index = startIndex

    for key, crypto in priceSymbols.items():
        openPriceDict[crypto] = []
        closePriceDict[crypto] = []
        volumeDict[crypto] = []
        highPriceDict[crypto] = []
        lowPriceDict[crypto] = []

    while(endIndex < index <= startIndex):
        for key, crypto in priceSymbols.items():
            openPrice = select_by_crypto(conn, 'openprices', crypto, index)[0][0]
            closePrice = select_by_crypto(conn, 'closeprices', crypto, index)[0][0]
            volume = select_by_crypto(conn, 'volumes', crypto, index)[0][0]
            highPrice = select_by_crypto(conn, 'highprices', crypto, index)[0][0]
            lowPrice = select_by_crypto(conn, 'lowprices', crypto, index)[0][0]

            openPriceDict[crypto].append(openPrice)
            closePriceDict[crypto].append(closePrice)
            volumeDict[crypto].append(volume)
            highPriceDict[crypto].append(highPrice)
            lowPriceDict[crypto].append(lowPrice)

        index -= 1
        
    return openPriceDict, closePriceDict, volumeDict, highPriceDict, lowPriceDict

def getDataBinance(numDays):
    """
    :param numDays:
    :return:
    """
    global priceSymbols
    noData = {}

    priceSymbols = PriceSymbolsUpdater.chooseUpdate('binance')

    #the absolute end time for all data
    absEndTime = requests.get("https://api.binance.com/api/v1/time")
    absEndTime = absEndTime.json()

    #code for writing the values into three text files for each crypto: an open price, close price, and volume file.
    for key, currencyname in priceSymbols.items():

        noDataCount = 0
        #creating the file path lengths and opening them
        openPriceCryptoPath = os.path.join(cryptoPaths, currencyname + "OpenPrice" + ".txt")
        closePriceCryptoPath = os.path.join(cryptoPaths, currencyname + "ClosePrice" + ".txt")
        volumeCryptoPath = os.path.join(cryptoPaths, currencyname + "Volume" + ".txt")
        highCryptoPath = os.path.join(cryptoPaths, currencyname + "High" + ".txt")
        lowCryptoPath = os.path.join(cryptoPaths, currencyname + "Low" + ".txt")
        oprice = open(openPriceCryptoPath, "w")
        cprice = open(closePriceCryptoPath, "w")
        volume = open(volumeCryptoPath, "w")
        highPrice = open(highCryptoPath, "w")
        lowPrice = open(lowCryptoPath, "w")

        #while loop with a counter to make sure that the start and endtime stay one day apart but go backwards in time, numdays amount of days
        timeBackwards = 0
        while(timeBackwards < ONE_DAY*numDays):
            endTime = absEndTime['serverTime'] - timeBackwards
            startTime = endTime - ONE_THIRD_DAY
            parameters = {'symbol': currencyname, 'startTime': startTime, 'endTime': endTime, 'interval': '1m'}
            data = requests.get("https://api.binance.com/api/v1/klines", params=parameters)
            data = data.json()

            if(len(data) == 0):
                noDataCount+=1
                noData.update({currencyname: noDataCount})


            print("Length of data set: {} coin associated with data set: {} data set: {}".format(len(data), currencyname, data))
            for i in reversed(data):
                oprice.write("{},".format(i[1]))
                highPrice.write("{}, ".format(i[2]))
                lowPrice.write("{}, ".format(i[3]))
                cprice.write("{},".format(i[4]))
                volume.write("{},".format(i[5]))
            timeBackwards += ONE_THIRD_DAY

    print(noData)
    #closing all the files once we're done
    oprice.close()
    highPrice.close()
    lowPrice.close()
    cprice.close()
    volume.close()

#get the binance step sizes of each crypto (the step size is the minimum significant digits allowed by binance for crypto to be traded in)
def binStepSize():
    """
    :return:
    """
    #getting the dictionary of a lot of aggregate data for all symbols
    global stepsize
    stepsizeinfo = requests.get("https://api.binance.com/api/v1/exchangeInfo")
    bigdata = stepsizeinfo.json()["symbols"]

    #iterating through the dictionary and adding just the stepsizes into our own dictionary
    for i in bigdata:
        symbol = i["symbol"]
        stepsizem = i["filters"][1]["stepSize"]
        temp = {symbol: stepsizem}
        stepsize.update(temp)


def getOpenPrice(interval, minutesBack, cryptoOpenPriceLocalData = cryptoOpenPriceData, currencies =priceSymbols):
    """
    :param interval:
    :param minutesBack:
    :param cryptoOpenPriceLocalData:
    :return:
    """

    if(cryptoOpenPriceLocalData  == {}):
        #iterating through all the crypto symbols
        for key, currencyname in currencies.items():
            #the number of number of minutes we have gone back so far
            mins = 0

            # creating the path lengths and opening the openprice file with read permissions
            openPriceCryptoPath = os.path.join(cryptoPaths, currencyname + "OpenPrice" + ".txt")
            oprice = open(openPriceCryptoPath, "r")

            #reading through the file
            odata = oprice.readlines()

            # iterating through each file and adding the correct open prices to the dictionary goes through in reverse to make it oldest to newest
            for line in odata:
                words = line.split(",")
                #iterate through each data point in the line
                for i in words:
                    #check to see that the datapoint is between the endpoint and startpoint of the interval to train on
                    if mins > minutesBack and mins <= (minutesBack + interval):

                        # if there is not already a dictionary created for the value create one and put the first value in it
                        if (cryptoOpenPriceLocalData == {} or currencyname not in cryptoOpenPriceLocalData):
                            temp = {currencyname: [i]}
                            cryptoOpenPriceLocalData.update(temp)
                        # otherwise append the price to the list that is already there
                        else:
                            cryptoOpenPriceLocalData[currencyname].append(i)
                    mins+=1

        #makes a new dictionary if the dicitonary is not made yet and puts the values for each crypto in reverse
        # this is because crypto stat has data ordered newest to oldest and thus it has to be reversed before
        # it can be used to train oldest to newest in the evaluator

        for key, currencyname in currencies.items():
            reversedData = []
            for i in reversed(cryptoOpenPriceLocalData[currencyname]):
                reversedData.append(i)
            cryptoOpenPriceLocalData.update({currencyname: reversedData})


    return cryptoOpenPriceLocalData


def getClosePrice(interval, minutesBack, cryptoClosePriceLocalData = cryptoClosePriceData, currencies =priceSymbols):
    """
    :param interval:
    :param minutesBack:
    :param cryptoClosePriceLocalData:
    :return:
    """



    if(cryptoClosePriceLocalData == {}):
        #iterating through all the crypto symbols
        for key, currencyname in currencies.items():
            #the number of number of minutes we have gone back so far
            mins = 0
            #creating the path lengths and opening the close price file with read permissions
            closePriceCryptoPath = os.path.join(cryptoPaths, currencyname + "ClosePrice" + ".txt")
            cprice = open(closePriceCryptoPath, "r")

            #reading through the file
            cdata = cprice.readlines()

            #iterating through each file and adding the correct close price to the dictionary goes through in reverse to make it oldest to newest
            for line in cdata:
                words = line.split(",")
                # iterate through each data point in the line
                for i in words:
                    # check to see that the datapoint is between the endpoint and startpoint of the interval to train on
                    if mins > minutesBack and mins <= (minutesBack + interval):
                        if (cryptoClosePriceLocalData == {} or currencyname not in cryptoClosePriceLocalData):
                            temp = {currencyname: [i]}
                            cryptoClosePriceLocalData.update(temp)
                        else:
                            cryptoClosePriceLocalData[currencyname].append(i)
                    mins+=1

        #makes a new dictionary if the dicitonary is not made yet and puts the values for each crypto in reverse
        # this is because crypto stat has data ordered newest to oldest and thus it has to be reversed before
        # it can be used to train oldest to newest in the evalutator

        for key, currencyname in currencies.items():
            reversedData = []
            for i in reversed(cryptoClosePriceLocalData[currencyname]):
                reversedData.append(i)
            cryptoClosePriceLocalData.update({currencyname: reversedData})

    return cryptoClosePriceLocalData

def getVolume(interval, minutesBack, cryptoVolumeLocalData = cryptoVolumeData, currencies=priceSymbols):
    """
    :param interval:
    :param minutesBack:
    :param cryptoVolumeLocalData:
    :return:
    """

    if(cryptoVolumeLocalData == {}):
        print(interval)
        print(minutesBack)
        #iterate through all the crypto symbols
        for key, currencyname in currencies.items():
            # the number of number of minutes we have gone back so far
            mins = 0
            # creating the path lengths and opening the files with read permissions
            volumeCryptoPath = os.path.join(cryptoPaths, currencyname + "Volume" + ".txt")
            volume = open(volumeCryptoPath, "r")

            # reading through the volume file of the files
            vol = volume.readlines()
            # iterating through each file and adding the volume data to the dictionary
            for line in vol:
                openprice = line.split(",")
                # iterate through each data point in the line goes through in reverse to make it oldest to newest
                for i in openprice:
                    # check to see that the datapoint is between the endpoint and startpoint of the interval to train on
                    if mins > minutesBack and mins <= (minutesBack + interval):
                        if (cryptoVolumeLocalData == {} or currencyname not in cryptoVolumeLocalData):
                            temp = {currencyname: [i]}
                            cryptoVolumeLocalData.update(temp)
                        else:
                            cryptoVolumeLocalData[currencyname].append(i)
                    mins+=1
        #makes a new dictionary if the dicitonary is not made yet and puts the values for each crypto in reverse
        # this is because crypto stat has data ordered newest to oldest and thus it has to be reversed before
        # it can be used to train oldest to newest in the evalutator

        for key, currencyname in currencies.items():
            reversedData = []
            for i in reversed(cryptoVolumeLocalData[currencyname]):
                reversedData.append(i)

            cryptoVolumeLocalData.update({currencyname: reversedData})



    print(len(cryptoVolumeLocalData))
    return cryptoVolumeLocalData

def getHighPrice(interval, minutesBack, cryptoHighPriceLocalData = cryptoHighData, currencies=priceSymbols):
    """
    :param interval:
    :param minutesBack:
    :param cryptoHighPriceLocalData:
    :return:
    """

    if (cryptoHighPriceLocalData == {}):
        # iterating through all the crypto symbols
        for key, currencyname in currencies.items():
            # the number of number of minutes we have gone back so far
            mins = 0
            # creating the path lengths and opening the close price file with read permissions
            highCryptoPath = os.path.join(cryptoPaths, currencyname + "High" + ".txt")
            hprice = open(highCryptoPath, "r")

            # reading through the file
            hdata = hprice.readlines()

            # iterating through each file and adding the correct close price to the dictionary goes through in reverse to make it oldest to newest
            for line in hdata:
                words = line.split(",")
                # iterate through each data point in the line
                for i in words:
                    # check to see that the datapoint is between the endpoint and startpoint of the interval to train on
                    if mins > minutesBack and mins <= (minutesBack + interval):
                        if (cryptoHighPriceLocalData == {} or currencyname not in cryptoHighPriceLocalData):
                            temp = {currencyname: [i]}
                            cryptoHighPriceLocalData.update(temp)
                        else:
                            cryptoHighPriceLocalData[currencyname].append(i)

                    mins += 1

        # makes a new dictionary if the dicitonary is not made yet and puts the values for each crypto in reverse
        # this is because crypto stat has data ordered newest to oldest and thus it has to be reversed before
        # it can be used to train oldest to newest in the evalutator
        for key, currencyname in currencies.items():
            reversedData = []
            for i in reversed(cryptoHighPriceLocalData[currencyname]):
                reversedData.append(i)
            cryptoHighPriceLocalData.update({currencyname: reversedData})

    return cryptoHighPriceLocalData

def getLowPrice(interval, minutesBack, cryptoLowPriceLocalData = cryptoLowData, currencies = priceSymbols):
    """
    :param interval:
    :param minutesBack:
    :param cryptoLowPriceLocalData:
    :return:
    """

    if (cryptoLowPriceLocalData == {}):
        # iterating through all the crypto symbols
        for key, currencyname in currencies.items():
            # the number of number of minutes we have gone back so far
            mins = 0
            # creating the path lengths and opening the close price file with read permissions
            lowCryptoPath = os.path.join(cryptoPaths, currencyname + "Low" + ".txt")
            lprice = open(lowCryptoPath, "r")

            # reading through the file
            ldata = lprice.readlines()

            # iterating through each file and adding the correct close price to the dictionary goes through in reverse to make it oldest to newest
            for line in ldata:
                words = line.split(",")
                # iterate through each data point in the line
                for i in words:
                    # check to see that the datapoint is between the endpoint and startpoint of the interval to train on
                    if mins > minutesBack and mins <= (minutesBack + interval):
                        if (cryptoLowPriceLocalData == {} or currencyname not in cryptoLowPriceLocalData):
                            temp = {currencyname: [i]}
                            cryptoLowPriceLocalData.update(temp)
                        else:
                            cryptoLowPriceLocalData[currencyname].append(i)

                    mins += 1

        # makes a new dictionary if the dicitonary is not made yet and puts the values for each crypto in reverse
        # this is because crypto stat has data ordered newest to oldest and thus it has to be reversed before
        # it can be used to train oldest to newest in the evalutator
        for key, currencyname in currencies.items():
            reversedData = []
            for i in reversed(cryptoLowPriceLocalData[currencyname]):
                reversedData.append(i)
            cryptoLowPriceLocalData.update({currencyname: reversedData})

    return cryptoLowPriceLocalData

#pick the right get Data method for the website asked for

def getData(count, website='binance'):
    """
    :param count: the number of days of data we want
    :param website: the name of the website to grab data from
    :return:
    """

    if(website=='binance'):
        getDataBinance(count)
    else:
        print("Unimplemented")

def main():
    getDataDatabase(5, 5, 5)






if __name__ == "__main__":
    main()
