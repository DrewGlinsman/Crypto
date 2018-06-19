import time
import requests
import os
import datetime
import PriceSymbolsUpdater

from Generics import priceSymbols



# setup the relative file path
dirname = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dirname + '/', '')

# path to save the different text files in
cryptoPaths = os.path.join(dirname + '/', 'BackTestData')

# one day in ms
ONE_DAY = 86400000
ONE_THIRD_DAY = 28800000
count = 1

# dicts for the data
cryptoOpenPriceData = {}
cryptoClosePriceData = {}
cryptoHighData = {}
cryptoLowData = {}
cryptoVolumeData = {}


def getDataBinance(numDays):
    """
    :param numDays:
    :return:
    """
    # code for writing the values into three text files for each crypto: an open price, close price, and volume file.
    for key, currencyname in priceSymbols.items():
        # creating the file path lengths and opening them
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

        endTime = requests.get("https://api.binance.com/api/v1/time")
        endTime = endTime.json()
        endTime = endTime['serverTime']
        print("Time object: {} Type: {}".format(endTime, type(endTime)))

        # while loop with a counter to make sure that the start and endtime stay one day apart but go backwards in time, numdays amount of days
        timeBackwards = numDays * ONE_DAY
        endTime = endTime - timeBackwards

        time.sleep(1)

        while (timeBackwards > 0):
            endTime += ONE_THIRD_DAY
            startTime = endTime - ONE_THIRD_DAY
            parameters = {'symbol': currencyname, 'startTime': startTime, 'endTime': endTime, 'interval': '1m'}
            data = requests.get("https://api.binance.com/api/v1/klines", params=parameters)
            print("Start Time: {} End Time: {}".format(startTime, endTime))
            endTimeDate = datetime.datetime.fromtimestamp(endTime / 1000.0)
            startTimeDate = datetime.datetime.fromtimestamp(startTime / 1000.0)
            print("Start Time: {} End Time: {}".format(startTimeDate, endTimeDate))
            data = data.json()
            print("Data: {}".format(data))
            print("Type: {}".format(type(data)))
            for i in data:
                if (i[1] != '[]'):
                    oprice.write("{},".format(i[1]))
                if(i[2] != '{}'):
                    highPrice.write("{}, ".format(i[2]))
                if(i[3] != '{}'):
                    lowPrice.write("{}, ".format(i[3]))
                if (i[4] != '[]'):
                    cprice.write("{},".format(i[4]))
                if (i[5] != '[]'):
                    volume.write("{},".format(i[5]))
            timeBackwards -= ONE_THIRD_DAY

    # closing all the files once we're done
    oprice.close()
    highPrice.close()
    lowPrice.close()
    cprice.close()
    volume.close()


def getOpenPrice(interval, minutesBack, currencies=priceSymbols):
    """
    :param interval:
    :param minutesBack:
    :param currencies:
    :return:
    """
    if(cryptoOpenPriceData == {}):
        # iterating through all the crypto symbols
        for key, currencyname in currencies.items():
            # the number of number of minutes we have gone back so far
            mins = 0

            # creating the path lengths and opening the openprice file with read permissions
            openPriceCryptoPath = os.path.join(cryptoPaths, currencyname + "OpenPrice" + ".txt")
            oprice = open(openPriceCryptoPath, "r")

            # reading through the file
            odata = oprice.readlines()

            # iterating through each file and adding the correct open prices to the dictionary goes through in reverse to make it oldest to newest
            for line in odata:
                words = line.split(",")
                # iterate through each data point in the line
                for i in words:
                    # check to see that the datapoint is between the endpoint and startpoint of the interval to train on
                    if mins > minutesBack and mins <= (minutesBack + interval):
                        # if there is not already a dictionary created for the value create one and put the first value in it
                        if (cryptoOpenPriceData == {} or currencyname not in cryptoOpenPriceData):
                            temp = {currencyname: [i]}
                            cryptoOpenPriceData.update(temp)
                        # otherwise append the price to the list that is already there
                        else:
                            cryptoOpenPriceData[currencyname].append(i)
                    mins += 1

        # makes a new dictionary if the dicitonary is not made yet and puts the values for each crypto in reverse
        # this is because crypto stat has data ordered newest to oldest and thus it has to be reversed before
        # it can be used to train oldest to newest in the evalutator

        for key, currencyname in currencies.items():
            reversedData = []
            for i in reversed(cryptoOpenPriceData[currencyname]):
                reversedData.append(i)
            cryptoOpenPriceData.update({currencyname: reversedData})

    return cryptoOpenPriceData


def getClosePrice(interval, minutesBack, currencies=priceSymbols):
    """
    :param interval:
    :param minutesBack:
    :param currencies:
    :return:
    """
    if(cryptoClosePriceData == {}):
        # iterating through all the crypto symbols
        for key, currencyname in currencies.items():
            # the number of number of minutes we have gone back so far
            mins = 0
            # creating the path lengths and opening the close price file with read permissions
            closePriceCryptoPath = os.path.join(cryptoPaths, currencyname + "ClosePrice" + ".txt")
            cprice = open(closePriceCryptoPath, "r")

            # reading through the file
            cdata = cprice.readlines()

            # iterating through each file and adding the correct close price to the dictionary goes through in reverse to make it oldest to newest
            for line in cdata:
                words = line.split(",")
                # iterate through each data point in the line
                for i in words:
                    # check to see that the datapoint is between the endpoint and startpoint of the interval to train on
                    if mins > minutesBack and mins <= (minutesBack + interval):
                        if (cryptoClosePriceData == {} or currencyname not in cryptoClosePriceData):
                            temp = {currencyname: [i]}
                            cryptoClosePriceData.update(temp)
                        else:
                            cryptoClosePriceData[currencyname].append(i)
                    mins += 1

        # makes a new dictionary if the dicitonary is not made yet and puts the values for each crypto in reverse
        # this is because crypto stat has data ordered newest to oldest and thus it has to be reversed before
        # it can be used to train oldest to newest in the evalutator

        for key, currencyname in currencies.items():
            reversedData = []
            for i in reversed(cryptoClosePriceData[currencyname]):
                reversedData.append(i)
            cryptoClosePriceData.update({currencyname: reversedData})

    return cryptoClosePriceData


def getVolume(interval, minutesBack, currencies=priceSymbols):
    """
    :param interval:
    :param minutesBack:
    :param currencies:
    :return:
    """
    if(cryptoVolumeData == {}):
        # iterate through all the crypto symbols
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
                        if (cryptoVolumeData == {} or currencyname not in cryptoVolumeData):
                            temp = {currencyname: [i]}
                            cryptoVolumeData.update(temp)
                        else:
                            cryptoVolumeData[currencyname].append(i)
                    mins += 1

        # makes a new dictionary if the dicitonary is not made yet and puts the values for each crypto in reverse
        # this is because crypto stat has data ordered newest to oldest and thus it has to be reversed before
        # it can be used to train oldest to newest in the evalutator

        for key, currencyname in currencies.items():
            reversedData = []
            for i in reversed(cryptoVolumeData[currencyname]):
                reversedData.append(i)

            cryptoVolumeData.update({currencyname: reversedData})

    return cryptoVolumeData


def getHighPrice(interval, minutesBack, currencies=priceSymbols):
    """
    :param interval:
    :param minutesBack:
    :param currencies:
    :return:
    """

    if (cryptoHighData == {}):
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
                        if (cryptoHighData == {} or currencyname not in cryptoHighData):
                            temp = {currencyname: [i]}
                            cryptoHighData.update(temp)
                        else:
                            cryptoHighData[currencyname].append(i)

                    mins += 1

        # makes a new dictionary if the dicitonary is not made yet and puts the values for each crypto in reverse
        # this is because crypto stat has data ordered newest to oldest and thus it has to be reversed before
        # it can be used to train oldest to newest in the evalutator
        for key, currencyname in currencies.items():
            reversedData = []
            for i in reversed(cryptoHighData[currencyname]):
                reversedData.append(i)
            cryptoHighData.update({currencyname: reversedData})

    return cryptoHighData


def getLowPrice(interval, minutesBack, currencies=priceSymbols):
    """
    :param interval:
    :param minutesBack:
    :param currencies:
    :return:
    """

    if (cryptoLowData == {}):
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
                        if (cryptoLowData == {} or currencyname not in cryptoLowData):
                            temp = {currencyname: [i]}
                            cryptoLowData.update(temp)
                        else:
                            cryptoLowData[currencyname].append(i)

                    mins += 1

        # makes a new dictionary if the dicitonary is not made yet and puts the values for each crypto in reverse
        # this is because crypto stat has data ordered newest to oldest and thus it has to be reversed before
        # it can be used to train oldest to newest in the evalutator
        for key, currencyname in currencies.items():
            reversedData = []
            for i in reversed(cryptoLowData[currencyname]):
                reversedData.append(i)
            cryptoLowData.update({currencyname: reversedData})

    return cryptoLowData


#get the data for the specified website
def getData(numDays, website='binance'):
    """
    :param numDays: the number of days of data desired
    :param website: the name of the website to pull the data from
    :return:
    """
    global priceSymbols
    priceSymbols = PriceSymbolsUpdater.priceSymbols

    if(website == 'binance'):
        getDataBinance(numDays)
    else:
        print('not implemented')

def main():
    # creating the filepath for the file with the timestamp in it and reading it into the timestamp and converting it to int
    timefilePath = os.path.join(cryptoPaths, "timestamp.txt")
    timefile = open(timefilePath, "r")
    timestamp = int(timefile.readline())
    timefile.close()

    # after reading in timestamp convert to a date time object and then strip it down to only hours minutes and seconds
    timestamp = datetime.datetime.fromtimestamp(timestamp / 1000.0)
    timestamp = int(timestamp.strftime("%H%M%S"))

    print("{}".format(timestamp))

    # infinite loop to keep the program running where it will get the data at
    while (0 < 1):

        # get the current time stamp and convert it into a time with only hours minutes and seconds
        currentTime = int(time.time() * 1000)
        currentTime = datetime.datetime.fromtimestamp(currentTime / 1000.0)
        currentTime = int(currentTime.strftime("%H%M%S"))

        if (currentTime != timestamp):
            print("Current Time: {} Timestamp to get to: {}".format(currentTime, timestamp))
            time.sleep(1)
        else:
            print("Getting data")
            getData(180)


if __name__ == "__main__":
    main()
