# Copyright (c) 2018 A&D
# Auto trading bot that uses parameters sent by CryptoTrainer to test them


import os
import sys
import CryptoStatAnalysis
import datetime
import pathlib
import CryptoStats
import pickle
<<<<<<< HEAD
from CryptoDistribution import readPickle
=======
import logging
import  PriceSymbolsUpdater
>>>>>>> e1c541f282411dc27b523bc6e6b7346efd83ea34

from CryptoTrainer import  minInDay
from Generics import PARAMETERS, storedInput, calcPercentChange

try:
    from urlib import urlencode

except ImportError:
    from urllib.parse import urlencode


# todo make a series of functions used that have random variables in them and random variables left out instead of a simple linear score and simple parameter variation
# todo add in a parser for the stdin
# todo add a minimum volume parameter to weed out the cryptos not traded at a high enough rate
# todo add a minimum financial transaction amount per minute that must be occuring (uses the minimum volume and current price of each crypto)

#setup the relative file path
dirname = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dirname + '/', '')

# GLOBAL_VARIABLES

#0 is false, 1 is true
# flags used to exit if different exit conditions are met (set with random params from the parameter set)
RESTART = 0
RESTART_TN = 0
RESTART_LOW = 0
EXIT = 0

# price each crypto is bought at
priceBought = 0.0


# How much of bitcoin balance to buy to purhcase more of the crypto (should be fixed to account for the fee of buying)
PERCENT_QUANITITY_TO_SPEND = .9

priceList = []
#percent changes of the prices for each crypto with an interval size over a specified period of time
percentChanges = {}

#percent changes of the volume for each crypto with an interval size over a specified period of time
volumePercentChanges = {}

#volume data for each interval over a specified period fo time
volumeAmounts = {}

#the percent price change over an hour, the number of intervals the price increased, and the weighted time where the crypto increased
pricePercentData = {}

#holds the percent volume change over an hour, the number of intervals the volume increased, and the weighted time where the crypto increased
volumePercentData = {}

#stores the calculated weightedMovingAverage
weightedMovingAverage = {}

#the modified cumulative volume over a period (a negative percent change will result in the volume change being counted as negative towards the
# cumulative volume stored here
modifiedVolume = {}

# stored volume, mean, and score
storedScores = {}

# holds the the other stat items in it
statDict = {}

# the binance intervals, their symbols, and their time in milliseconds
intervalTypes = {'1m': {'symbol': '1m', 'inMS': 60000}, '3m': {'symbol': '3m', 'inMS': 180000}, '5m': {'symbol': '5m', 'inMS': 300000}, '15m': {'symbol': '15m', 'inMS': 900000}, '30m': {'symbol': '30m', 'inMS': 1800000}, '1h': {'symbol': '1h', 'inMS': 3600000}, '2h': {'symbol': '2h', 'inMS': 7200000}, '4h': {'symbol': '4h', 'inMS': 14400000}, '6h': {'symbol': '6h', 'inMS': 21600000}, '8h': {'symbol': '8h', 'inMS': 28800000}, '12h': {'symbol': '12h', 'inMS': 43200000}, '1d': {'symbol': '1d', 'inMS': 86400000}, '3d': {'symbol': '3d', 'inMS': 259200000}, '1w': {'symbol': '1w', 'inMS': 604800000}, '1M': {'symbol': '1M', 'inMS': 2629746000}}

# the score of each crypto
scores = {}

# decimal precision allowed for trading each crypto
stepsizes = {}

# crypto being bouhgt and held
currencyToTrade = {}

# temporary variable that holds currently held crypto right before the logic to test if
# a new crypto is better to buy
oldCurrency = ''

# the new crytpo determined as the best one to buy
currentCurrency = ''

# in bitcoins (before trading)
initialBalance = 0.0

# in bitcoins (after trading)
currentBalance = 0.0

# cumulative percent change of a crypto's price over the course of owning it
CUMULATIVE_PERCENT_CHANGE = 0.0

# list to hold the values stored to find the max
values = {'PERCENT_BY_HOUR': [], 'VOLUME_BY_HOUR': [], 'TIME_INCREASING': [], 'WEIGHTED_TIME_INCREASING': [], 'VOLUME_TIME_INCREASING': [], 'WEIGHTED_VOLUME_TIME_INCREASING': [], 'MODIFIED_VOLUME': [], 'SCORE': []}


# hold the max values to be used for scaling
maxValues = {'PERCENT_BY_HOUR': 0.0, 'VOLUME_BY_HOUR': 0.0, 'TIME_INCREASING': 0.0, 'WEIGHTED_TIME_INCREASING': 0.0, 'VOLUME_TIME_INCREASING': 0.0, 'WEIGHTED_VOLUME_TIME_INCREASING': 0.0, 'MODIFIED_VOLUME': 0.0, 'SCORE': 0.0}

# number of minutes we want to iterate backwards
startMinute = 0
endMinute = 60
startMinNum = 0
endMinNum = 60
currentMinute = 0

# true price for the crrpto being bought
truePriceBought = 0.0

# the currently owned crypto
owned = 'BTCUSDT'

# the number of buys
numBuys = 0

# the number of sells
numSells = 0

# whether testing or not
testCheck = 0

# percent Changes over all sepearted periods of time
allOwnedCryptoPercentChanges = []

# cryptos seperated by decision into those disregarded, those chosen but not making final cut because of their mean, those selected that have the appropriate mean, and the crypto that is chosen, has the right mean, and is the max
cryptosSeperated = {'Disregarded': [], 'Chosen': [], 'chosenButCut': [], 'chosenNotCut': [], 'theMax': []}


file = ''
picklefile = ''

# todo finish implementing this system of tracking the crypto we currently own
# the crypto we currently own
ownCrypto = 'BTCUSDT'


# you can use the words instead of these values
YES = 1
NO = 0

realInterval = 0

# the different dictionaries used to store the data for the interval
openPriceData = {}
closePriceData = {}
volumeData = {}
highPriceData = {}
lowPriceData = {}

#setup the log file for this evaluator
def setUpLog(logdirectory, logfilename):

    logging.basicConfig(filename=logdirectory+logfilename, level='DEBUG')


#makes the corresponding log and variation directory for this evaluator
def initdirectories(paramspassed, typedirec='storage'):
    """
    :param paramspassed: the parameters passed from the file running this evaluator
    :param typedirec: the directory type (training or storage)
    :return:
    """
    directory = "{}/{}/{}/{}/{}/{}/{}/".format(dirname, typedirec, paramspassed['website'], paramspassed['day'], paramspassed['hour'],
                             paramspassed['min'], paramspassed['idnum'], paramspassed['classNum'])

    pathlib.Path(directory + "variations/").mkdir(parents=True, exist_ok=True)
    pathlib.Path(directory + "logs/").mkdir(parents=True, exist_ok=True)

#reads pickle from a file into the passed parameter dictionary
def readParamPickle( directory, filename):
    """
    :param directory:
    :param filename:
    :return: the parameter dictionary found in the specified directory with the specified filename
    """

    picklefile = directory +filename

    with open(picklefile, "rb") as pickle_in:
        paramDict = pickle.load(pickle_in)

    return paramDict

# write pickle to a file
#write pickle to a file
def writeParamPickle(paramDict, directory, picklefilename):
    """
    :param paramDict:
    :return:
    """
    picklefile = directory + picklefilename

    with open(picklefile, "wb") as pickle_out:
        pickle.dump(paramDict, pickle_out)

    return paramDict


#todo add a way to read in the runNumber from the crypto trainer
def readTheInput():

    global storedInput
    global PARAMETERS

    if len(sys.argv) == 1:  # if there are no parameters passed (will be = 3 if this is being run as a subprocess)
        # make the max cycles equal to the number of days of the interval in hours
        PARAMETERS['MAX_CYCLES'] = (PARAMETERS['INTERVAL_TO_TEST'] / minInDay) * 24.0
        PARAMETERS['CLASS_NUM'] = -1


        return storedInput, PARAMETERS


    if sys.argv[1] == "Alone": #if there are more than one argument than we know this is being run from a separate file
        # make the max cycles equal to the number of days of the interval in hours
        PARAMETERS['MAX_CYCLES'] = (PARAMETERS['INTERVAL_TO_TEST'] / minInDay) * 24.0
        storedInput['website'] = sys.argv[2]
        storedInput['day'] = sys.argv[3]
        storedInput['hour'] = sys.argv[4]
        storedInput['min'] = sys.argv[5]
        storedInput['variationNum'], PARAMETERS['VARIATION_NUMBER'] = sys.argv[6]
        storedInput['classNum'], PARAMETERS['CLASS_NUM'] = sys.argv[7] #default should be -1
        storedInput['idnum'] = sys.argv[8]

        return storedInput, PARAMETERS

    else:

        for line in sys.stdin:

            if line != '':
                # split the passed string into a list seperated by spaces
                listSplits = line.split(' ')
                #loops through the different values split from the input and stores them in a dictionary
                count = 0
                for key, value in storedInput.items():
                    storedInput[key] = listSplits[count]
                    count += 1

    return storedInput, PARAMETERS

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

    # mark item as the current crypto being traded and save the buy price at for failure condition
    entry = {symbol: {'buyPrice': ratio, 'timestamp': 0}}
    currencyToTrade.clear()
    currencyToTrade.update(entry)

# sell the specified crypto


def sellBin(symbol):
    """
    :param symbol:
    :return:
    """
    return 0


# add in the weight todo
# calculates the weighted moving average over the specified interval for a crypto currency

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

    # adds up the cumulative price changes using each interval
    for x in range(startMinute, endMinute):
        startPrice = openPriceDataLocal[x]
        endPrice = closePriceDataLocal[x]
        change = calcPercentChange(startPrice, endPrice)

        cumulativePrice += change

    # the scaling of the cumulative price
    cumulativePrice = (cumulativePrice / slots) * PARAMETERS['CUMULATIVE_PRICE_MODIFIER']

    return cumulativePrice

# this function will update the weighted moving average every second the program runs todo
# def updateWeightedMovingAverage(currency, interval, starttime, endtime):


# gets the cumulative volume over a period and scales it based on the currency's price
def getVolume(currency, currentMinute):
    """
    :param currency:
    :param currentMinute:
    :return:
    """
    global realInterval
    global volumeData

    volume = []
    # building the request
    volumeDataLocal = volumeData[currency]
    # adds up all the volumes over the interval
    for x in volumeDataLocal:
        if(x != ''):
            x = float(x)
            x *= float(getbinanceprice(currency, currentMinute))
        else:
            x = 0.0
        volume.append(x)
    return volume


# grabs the list of volumes over the interval and percent changes over the interal
# then interates through and calculates a cumulative volume where the volume is considered negative
# when the percent change was negative and positive when the percent change was positive
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

    # adds up the volume with negative percent changes in price resulting in the volume
    # considered to be mostly 'negative', how much is determined by the magnitude
    # of the percent change in price
    for i in volumeAmountList:

        # makes each volume % change back into a decimal

        percentChangeScale = (percentChangesList[currentSlot])

        if percentChangeScale < 0:
            vols.append(percentChangeScale * volumeAmountList[currentSlot] * PARAMETERS['NEGATIVE_WEIGHT'])
            volList.append({'volumeofslot': volumeAmountList[currentSlot], 'weight': PARAMETERS['NEGATIVE_WEIGHT']})
            oldVolume += percentChangeScale * volumeAmountList[currentSlot] * PARAMETERS['NEGATIVE_WEIGHT']
        # todo the below may have not been there for the last set of tests
        if percentChangeScale >= 0:
            vols.append(percentChangeScale * volumeAmountList[currentSlot])
            volList.append({'volumeofslot': volumeAmountList[currentSlot], 'weight': 'NONE'})
            oldVolume += percentChangeScale * volumeAmountList[currentSlot]

        currentSlot += 1

    return float(oldVolume)

# get the binance price of the specified currency


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

    # interval based on this from binance API
    #     m -> minutes;     h -> hours;     d -> days;     w -> weeks;    M -> months
    #  1m  3m   5m  15m  30m  1h 2h 4h 6h 8h  12h  1d   3d  1w   1M
    # method used to update price lists on past hour of trends

# method to iterate through all the cryptos available on binance and store their price changes, percent price changes,
# volume changes, percent volume changes, scores, time increasing, and time decreasing


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

        # todo figure out why this and the one below always starts at 0
        # calculate the percent change over the whole hour and store
        openPrice = openPriceDataLocal[startMinute]
        closePriceIndex = endMinute - 1
        closePrice = closePriceDataLocal[closePriceIndex]

        pricePercentData[currency]['percentbyhour'] = calcPercentChange(openPrice, closePrice)

        values['PERCENT_BY_HOUR'].append(pricePercentData[currency]['percentbyhour'])

        # todo figure out if it should have been endMinute - startMinute - 1 or just endMinute - 1
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

    # add cryptos and their scores to dictionary of currencies to trade if they are above the minimum score
    # record which cryptos were not chosen, and which were chosen that had the right score or had the right score and mean
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

    #logging.info("Currrenty to trade: " + str(currencyToTrade))


# caclulates and returns the time spent increasing
# weighted = 0 is false, weighted = 1 is true
 # TODO update the modulo so that it is a modulo not a multiplcation so that
 # patterns are detected
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
        slots += 1

        # the four if statements only differ in that the second two
        # caclcualte slots_increasing using a weight
        # that casues positive increases early in the hour to matter less
        # than increases later in the hour
        # In addition, the second and fourth if statement consider the slots with a negative
        # percent change

        if float(i) > 0.0 and isWeighted == 0:
            slots_increasing += 1 * i

        if float(i) < 0.0 and isWeighted == 0:
            slots_increasing += 1 * i * PARAMETERS['NEGATIVE_WEIGHT']

        if float(i) > 0.0 and isWeighted == 1:
            slots_increasing += (1 * (slots * PARAMETERS['SLOT_WEIGHT']) * i)

        if float(i) < 0.0 and isWeighted == 1:
            slots_increasing += (1 * (slots * PARAMETERS['SLOT_WEIGHT']) * i * PARAMETERS['NEGATIVE_WEIGHT'])

    if(slots == 0.0):
        slots = 1.0

    return (slots_increasing / slots) * PARAMETERS['TIME_INCREASING_MODIFIER']


# caclulates and returns the time spent increasing for volume
# weighted = 0 is false, weighted = 1 is true
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
        slots += 1

        # first two if statements consider the slots_increasing for a nonweighted calcualtion
        # second and fourth if statements consider the negative percent changes

        if float(i) > 0.0 and isWeighted == 0:
            slots_increasing += 1 * i

        if float(i) < 0.0 and isWeighted == 0:
            slots_increasing += 1 * i * PARAMETERS['NEGATIVE_WEIGHT']

        if float(i) > 0.0 and isWeighted == 1:
            slots_increasing += (1 * (slots * PARAMETERS['SLOT_WEIGHT']) * i)

        if float(i) < 0.0 and isWeighted == 1:
            slots_increasing += (1 * (slots * PARAMETERS['SLOT_WEIGHT']) * i * PARAMETERS['NEGATIVE_WEIGHT'])

    if (slots == 0.0):
        slots = 1.0

    return (slots_increasing / slots) * PARAMETERS['VOLUME_INCREASING_MODIFIER']

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
    if(maxValues['TIME_INCREASING'] != 0):
        values['TIME_INCREASING'].append(pricePercentData[symbol]['timeIncreasing'] / maxValues['TIME_INCREASING'])
    values['VOLUME_TIME_INCREASING'].append(volumePercentData[symbol]['timeIncreasing'] / maxValues['TIME_INCREASING'])
    values['WEIGHTED_TIME_INCREASING'].append((pricePercentData[symbol]['weightedtimeIncreasing'] / maxValues['WEIGHTED_TIME_INCREASING']))
    values['WEIGHTED_VOLUME_TIME_INCREASING'].append((volumePercentData[symbol]['weightedtimeIncreasing'] / maxValues['WEIGHTED_VOLUME_TIME_INCREASING']))

    try:
        values['MODIFIED_VOLUME'].append((modifiedVolume[symbol] / maxValues['MODIFIED_VOLUME']))
    except ZeroDivisionError:
        logging.info("Whoopsie zero by division error!" + str(maxValues)  + '\n')
        for i in values:
            logging.info(str(i) + '\n')

    # addingup the parameters to the score variable
    new_score += (volumePercentData[symbol]['percentbyhour'] / maxValues['VOLUME_BY_HOUR']) * PARAMETERS['VOLUME_PERCENT_BY_HOUR_MODIFIER']
    new_score += ((pricePercentData[symbol]['percentbyhour']) / maxValues['PERCENT_BY_HOUR']) * PARAMETERS['PERCENT_BY_HOUR_MODIFIER']

    new_score += (pricePercentData[symbol]['weightedtimeIncreasing'] / maxValues['WEIGHTED_TIME_INCREASING'])

    new_score += (volumePercentData[symbol]['weightedtimeIncreasing'] / maxValues['WEIGHTED_VOLUME_TIME_INCREASING'])

    new_score += (modifiedVolume[symbol] / maxValues['MODIFIED_VOLUME']) * PARAMETERS['MODIFIED_VOLUME_MODIFIER']

<<<<<<< HEAD

=======
>>>>>>> 7566a815060edbc502fb7723146558dd55b69dd2
    return new_score


# finds the next currency to buy
def priceChecker():
    """
    :return:
    """
    currencyToBuy = ''
    # Compares the two price lists and sets the currencyToBuy to be
    # the coin with the highest score that also is above the minimum moving average
    maxScore = 0
    for key, value in currencyToTrade.items():
        #logging.info("The score of " + str(key) +  ' is ' + str(scores[key]) + '\n')

        try:
            if(maxScore < scores[key] and float(weightedMovingAverage[key]) > float(PARAMETERS['MINIMUM_MOVING_AVERAGE'])):
                maxScore = scores[key]
                #logging.info('CURRENT HIGH SCORE: The score of ' + str(key) +  ' is ' + str( scores[key]) + '\n')
                currencyToBuy = key

        except KeyError:
            logging.info(" LINE 550 key error " + str(key) + " scores[key] " + weightedMovingAverage[key]  + '\n')

    #logging.info('Coin with the highest score is ' + str(currencyToBuy) + ' which is ' + str(maxScore) + '\n' )

    cryptosSeperated['theMax'].append(currencyToBuy)
    return currencyToBuy  # potential runtime error if all negative todo


# checks if the current crypto has been decreasing the past ten minutes
# if yes it forces a new check to see if there is a better crypto
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

    # get the starting price of the interval
    startPriceInterval = openPriceDataLocal[startMinute]
    timeIncreasingCounter = 0

    # iterate through the list of percent changes and add up when the percent change was positive
    for x in range(startMinute, endMinute):
        startPrice = openPriceDataLocal[x]
        endPrice = closePriceDataLocal[x]
        #logging.info("Current Crypto: " + str(currency) + ' Start Price: ' +str(startPrice) + ' End Price: ' + str(endPrice))
        percentChange = calcPercentChange(startPrice, endPrice)
        if(percentChange > 0):
            timeIncreasingCounter += 1

    intervalPercentChange = calcPercentChange(startPriceInterval, endPrice)
    #logging.info('Cumulative percent change over THIS INTERVAL ' + str((intervalPercentChange)))
    #logging.info("Times Increasing over the interval: " + str(timeIncreasingCounter))

    if(timeIncreasingCounter <= timesIncreasing):
        #logging.info("DECREASED ALL INTERVALS. RESTART")
        return 1

    return 0

# checks whether the function has caused too large of negative decrease the specified interval


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

    # if the percent change is less than the negation of the absolute value of max decrease (ensures it is treated as negative
    if(percentChange < (-1 * abs((PARAMETERS['MAX_DECREASE'])))):
        #logging.info("TOO NEGATIVE. RESTART")
        return 1

    return 0

# checks to see if the currency has increased or decreased more than is allowed
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

    # chaeck if the max percent change is negative so that the if statements work correctly
    if maxPC < 0:
        multiplyBy = -1
        multiplyBy2 = 1
    if maxPC >= 0:
        multiplyBy = 1
        multiplyBy2 = -1

    if(percentChange > multiplyBy * PARAMETERS['MAX_PERCENT_CHANGE']):
        #logging.info("HIT MAX PERCENT CHANGE")
        return 1

    if(percentChange < multiplyBy2 * PARAMETERS['MAX_PERCENT_CHANGE']):
        #logging.info("HIT MINIMUM PERCENT CHANGE")
        return 1

    return 0

# checks to see if the current currency is too near to its starting point


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

    # checks to see if the coin was increasing or decreasing over the last 15 minutes. +13 since endMinute is already one greater than start minute and +8 since checkFailureCondition uses 10 minute intervals
    direction = increasingOrDecreasing(currency, startMinute, endMinute + 13)
    allIntervalsDecreasing = checkFailureCondition(currency, timesIncreasing, startMinute, endMinute + 8)

    # check to see if the current price is too low, the crypto is decreasing over the past 15 minutes
    # and all the intervals are decreasing
    if(float(currentPrice) < float(floorPrice) and direction == 0 & allIntervalsDecreasing == 1):
        #logging.info("WAS TOO LOW")
        return 1

    return 0

# returns whether the specified currency is increasing or decreasing over the interval
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

# reset the list of parameter values


def resetValues():
    """
    :return:
    """
    # reset the list of parameter value that are calculated below
    for key, value in values.items():
        values[key][:] = []


# runs through the values collected and storess the max value
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

    #logging.info("THE VALUES {}".format(values))
    #logging.info("THE MAX {}".format(maxValues))

# creates a dictionary with all the different statistic holding dictionaries that are created with each run


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

# sets all the list of how the cryptos were seperated back to being empty


def resetDecisionsStored(dict):
    """
    :param dict:
    :return:
    """
    for key, value in dict.items():

        value[:] = []

# set the parameter dictionary to use string not float by casting the passed dictionary from pickle file


def strToFloat(paramDict):
    """
    :param paramDict:
    :return:
    """
    newDict = PARAMETERS

    for key, value in paramDict.items():
        newDict[key] = float(value)

    return newDict

# create an accurate tradable dictionary of all the cryptos for a given time
def createVolumeDict():
    buyVolumeDict = {}
    sellVolumeDict = {}

    # creating a timestamp of the current time and finding which day of the week it is
    currentTime = datetime.datetime.now(tz=pytz.UTC)
    currentTime = currentTime.astimezone(pytz.timezone('US/Eastern'))
    hour = currentTime.strftime("%H%M")
    minute = int(currentTime.strftime("%M"))

    day = currentTime.isoweekday()
    weekday = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
    }[day]

    delta = minute % 10
    if(delta == 0):
        for key, value in priceSymbols.items():
            value = value.lower()
            temp1, temp2 = readPickle(value, weekday, hour)
            buyVolumeDict.update(temp1)
            sellVolumeDict.update(temp2)

    # if the time difference is greater than or equal to 5 minutes round up
    if (delta >= 5):
        currentTime = currentTime + datetime.timedelta(minutes=(10 - delta))
        hour = currentTime.strftime("%H%M")
        for key, value in priceSymbols.items():
            value = value.lower()
            temp1, temp2 = readPickle(value, weekday, hour)
            buyVolumeDict.update(temp1)
            sellVolumeDict.update(temp2)

    # if the time difference is less than 5 subtract to nearest 10 minute interval
    elif(delta < 5):
        currentTime = currentTime + datetime.timedelta(minutes=(-delta))
        hour = currentTime.strftime("%H%M")
        for key, value in priceSymbols.items():
            value = value.lower()
            temp1, temp2 = readPickle(value, weekday, hour)
            buyVolumeDict.update(temp1)
            sellVolumeDict.update(temp2)

    return buyVolumeDict, sellVolumeDict

# todo add in a parser to read the stdin that will be passed with the parameters from cryptotrainer
# return the directory of the class this sits in

def buildDirectory(paramspassed, typedirec='storage'):
    """
    :param paramspassed: the parameters passed to this file
    :param typedirec: the directory type (training or storage)
    :return: the directory of the log and variations files
    """

    return "{}/{}/{}/{}/{}/{}/{}/{}/".format(dirname, typedirec, paramspassed['website'], paramspassed['day'], paramspassed['hour'],
                             paramspassed['min'], paramspassed['idnum'], paramspassed['classNum'])

# setup the data dictionaries if they are missing any cryptocurrencies

def setUpData(paramspassed):
    """
    :param paramspassed: the parameters passed to this function
    :return: the updated price symbol dictionary
    """
    global priceSymbols
    global percentChanges
    global volumePercentChanges
    global volumeAmounts
    global pricePercentData
    global volumePercentData
    global weightedMovingAverage
    global modifiedVolume

    #make sure price symbols has the right symbols
    priceSymbols = PriceSymbolsUpdater.chooseUpdate(paramspassed['website'])

    for key, currency in priceSymbols.items():
        percentChanges.update({currency:[]})
        volumePercentChanges.update({currency:[]})
        volumeAmounts.update({currency:[]})
        pricePercentData.update({currency: {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}})
        volumePercentData.update({currency: {'percentbyhour': 0, 'timeIncreasing': 0, 'weightedtimeIncreasing': 0}})
        weightedMovingAverage.update({currency: []})
        modifiedVolume.update({currency: 0.0})

    return priceSymbols

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
    global priceSymbols



    # number of times that the bot chooses not to buy
    totalAbstain = 0
    #reads in the input, usually from the cryptotrainer
    storedInput, PARAMETERS = readTheInput()

    #setup the normal data dictionaries and get an updated price symbol dictionary
    priceSymbols = setUpData(storedInput)

    #builds the directory to store logs and params
    initdirectories(storedInput, typedirec='training')

    #get the directory of the class
    classdirectory = buildDirectory(storedInput, typedirec='training')

    #the log directory
    logdirectory = classdirectory + 'logs/'

    print(logdirectory)

    #the log file name
    logfilename = str(int(storedInput['variationNum'])) + 'evaluator.log'

    #setup the log file in the log directory
    setUpLog(logdirectory, logfilename)

    #the directory of the param file
    directory = classdirectory + 'variations/'

    #the file name for the parameter file
    paramfilename = str(int(storedInput['variationNum'])) + 'param.pkl'

    #read the pickle parameter file and convert all to float and store in the real param dict
    strPARAMS = readParamPickle(directory, paramfilename)

    PARAMETERS = strToFloat(strPARAMS)

    # set the real interval to be used for all the data
    realInterval = PARAMETERS['INTERVAL_TO_TEST'] + PARAMETERS['MIN_OFFSET']

    #store the different kinds of data for the interval
    openPriceData = CryptoStats.getOpenPrice(realInterval , PARAMETERS['MINUTES_IN_PAST'], {}, currencies=priceSymbols)
    closePriceData = CryptoStats.getClosePrice(realInterval, PARAMETERS['MINUTES_IN_PAST'], {}, currencies=priceSymbols)
    volumeData = CryptoStats.getVolume(realInterval, PARAMETERS['MINUTES_IN_PAST'], {}, currencies=priceSymbols)
    highPriceData = CryptoStats.getHighPrice(realInterval, PARAMETERS['MINUTES_IN_PAST'], {}, currencies=priceSymbols)
    lowPriceData = CryptoStats.getLowPrice(realInterval, PARAMETERS['MINUTES_IN_PAST'], {}, currencies=priceSymbols)

    # initialize the minutes that will define the period
    startMinute = int(startMinNum + PARAMETERS['MIN_OFFSET'])
    endMinute = int(endMinNum + PARAMETERS['MIN_OFFSET'])
    currentMinute = int(startMinute)

    #creates a statistic object to record the different decisions and then analyze them
    cryptoRunStats = CryptoStatAnalysis.CryptoStatsAnalysis(storedInput['variationNum'], PARAMETERS['CLASS_NUM'],
                                                             startMinute, endMinute, PARAMETERS,
                                                            openPriceData, closePriceData, volumeData, highPriceData, lowPriceData,
                                                             logdirectory, storedInput, priceSymbols)

    # intitialize the starting currency and the number of cycles the program has run through
    # a cycle is either a period where a crypto was held or where one was bought/sold
    currentCurrency = ''
    cycles = 0

    # initialize the percent change over the whole test and the percent change over the lifetime of owning a crypto
    PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE'] = 0.0
    PARAMETERS['CUMULATIVE_PERCENT_CHANGE'] = 0.0

    #set the date and time at the top of the log file
    logging.info("Date and Time of Run " + str(datetime.datetime.now()) + '\n')

    # runs the bot for a set number of cycles or unless the EXIT condition is met (read the function checkExitCondition)
    # cycles is either a period where a crypto is held and ones where they are bought/sold
    while(cycles < PARAMETERS['MAX_CYCLES'] and EXIT == 0):

        # intialize the time the bot will run for
        t = 0

        # whether the bot decided not to buy or sell on this trade cycle
        numAbstain = 0

        RESTART = 0
        RESTART_LOW = 0
        RESTART_TN = 0

        # intialize the checkers that are set whether a buy or sell occured
        didSell = 0
        didBuy = 0

        # reset current minute to be the start minute
        currentMinute = startMinute

        # run update crypto to assign scores and sort through all the cryptos and advance a minute because of how long it takes to run
        updateCrypto(startMinute, endMinute, currentMinute)
        currentMinute += 1

        # reset the old currency to be equal to whatever the current crypto currency is
        if currentCurrency == '':
            oldCurrency = ownCrypto
        else:
            oldCurrency = currentCurrency

        # set the current currency to be whatever the price checker returns
        # can be a nothing string, the same crypto, or a new one
        currentCurrency = priceChecker()

        # sellf the current crypto if you want to buy a new one
        if (oldCurrency != currentCurrency) and (currentCurrency != '') and currentCurrency != ownCrypto:

            # store the price it was sold at
            pricesold = getbinanceprice(oldCurrency, currentMinute)

            # sell the old currency
            sellBin(oldCurrency)

            # if this is the first cycle we do not count the percentChange from 0 to the current price
            if cycles == 0:
                priceBought = pricesold

            # set sell checker
            didSell = 1

            # calculate and store the percent change from when the crypto was bought to when it was sold
            cumulativePercentChange = calcPercentChange(priceBought, pricesold)
            truePercentChange = calcPercentChange(truePriceBought, pricesold)
            PARAMETERS['CUMULATIVE_PERCENT_CHANGE'] = cumulativePercentChange
            PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE'] += cumulativePercentChange

            # writing to the log about when the run sold and what it bought at and what it sold at
            # as well as what was sold and how it changed
            #logging.info("THIS RUN SOLD AT: " + str(currentMinute))
            #logging.info('Selling:  ' + str(oldCurrency) + ' Price bought: ' + str(priceBought) +  ' Price sold: ' + str(pricesold) + '\n')
            #logging.info("FINAL percent change over the life of owning this crypto " + str(truePercentChange))

            # calcualates the length of the list of all the owned cryptos in order and their corresponding lists of percent changesover each crycle
            lenAllOwned = len(allOwnedCryptoPercentChanges)

            # if the currency currency is not the same one at the end of the list then make a new dictionary and append it
            # the new dictionary will be the current currency as the key and then a list of percent changes
            # else you just add a new the new percent change to the end of the list of percent changes over the life of that
            # cycle of owning that cryptocurrency
            if lenAllOwned == 0 or currentCurrency != allOwnedCryptoPercentChanges[lenAllOwned - 1]:
                newDict = {currentCurrency: [cumulativePercentChange]}
                allOwnedCryptoPercentChanges.append(newDict)
            else:
                allOwnedCryptoPercentChanges[lenAllOwned - 1][currentCurrency].append(cumulativePercentChange)

        # buy the new cryptocurrency if there was one selected
        if(oldCurrency != currentCurrency) and (currentCurrency != '') and currentCurrency != ownCrypto:
            buyBin(currentCurrency, currentMinute)
            ownCrypto = currentCurrency
            didBuy = 1

            #more output to files about the buying
            #logging.info("THIS RUN BOUGHT AT: " + str(currentMinute))
            #logging.info("Buying " + str(currentCurrency) + " at price: " + str(priceBought))

        # if you buy increment the buy counter
        if didBuy == 1:
            numBuys += 1
        if didSell == 1:
            numSells += 1

        # holding of the crypto currency for minutes less than the specied max or until one of the restart conditions is met
        # assuming there is a current currency owned
        while(t < PARAMETERS['MAX_TIME_CYCLE'] and RESTART == 0 and RESTART_TN == 0 and RESTART_LOW == 0 and currentCurrency != ''):
            if(t % PARAMETERS['WAIT_FOR_CHECK_FAILURE'] == 0 and t != 0):
                RESTART = checkFailureCondition(currentCurrency, 0, currentMinute, currentMinute + 9)

            if(t > PARAMETERS['WAIT_FOR_CHECK_TOO_LOW'] and t % PARAMETERS['WAIT_FOR_CHECK_FAILURE']):
                RESTART_LOW = checkTooLow(currentCurrency, 0, currentMinute, currentMinute + 1)

            RESTART_TN = checkTooNegative(currentCurrency, currentMinute)

            # advance the time and currency minute
            t += 1
            currentMinute += 1

        # check the exit immediately condition
        if currentCurrency != '' and currentMinute < realInterval:
            EXIT = checkExitCondition(currentCurrency, currentMinute)

        # if you kept the same crypto as the last cycle stole the percent chnage you have gotten from the last cycle of holding the crypto or from when it was bought
        if(oldCurrency == currentCurrency and currentCurrency != '' or EXIT == 1):

            # get the new price bought and calculate a percent change over this interval of holding the cyrpto
            newPrice = getbinanceprice(currentCurrency, currentMinute)
            cumulativePercentChange = calcPercentChange(priceBought, newPrice)

            # adds the percent change to the list of all the crypto currencies that have been owned over this run
            # more detail in similar code above
            lenAllOwned = len(allOwnedCryptoPercentChanges)

            if lenAllOwned == 0 or currentCurrency not in allOwnedCryptoPercentChanges[lenAllOwned - 1]:
                newDict = {currentCurrency: [cumulativePercentChange]}
                allOwnedCryptoPercentChanges.append(newDict)
            else:
                allOwnedCryptoPercentChanges[lenAllOwned - 1][currentCurrency].append(cumulativePercentChange)

            PARAMETERS['CUMULATIVE_PERCENT_CHANGE'] = cumulativePercentChange
            PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE'] += cumulativePercentChange

            # set the price bought to the new price found for the interval
            priceBought = newPrice

        # keeps tally of the number of times we have not bought total and whether we did or did not buy now
        if oldCurrency == ownCrypto and oldCurrency != '':
            numAbstain = 1
            totalAbstain += 1

        # if no crypto was chosen you wait 5 minutes and start again
        if currentCurrency == '':
            timeHeld = currentMinute - startMinute
            temp = startMinute
            startMinute += 5 + (currentMinute - startMinute)
            endMinute += 5 + (currentMinute - temp)

        # otherwise you reset the current minute and endminute
        else:
            timeHeld = currentMinute - startMinute
            temp = startMinute
            startMinute += (currentMinute - startMinute)
            endMinute += (currentMinute - temp)

        # make a new crypto stats snapshot for analysis of the decision making process
        # startMinute is misleading here. it will be equal to the start of the next cycle not the one that we just walked through
        #logging.info("CRYPTOS SEPEARTED " + str(cryptosSeperated))
        #logging.info("NUM ABSTAIN "  + str(numAbstain) + '\n')
        #logging.info('Did buy ' + str(didBuy) + '\n')
        #logging.info('Did sell ' + str(didSell) + '\n')
        #logging.info('Bought '+ str(currentCurrency) + '\n')
        #logging.info('Sold ' + str(oldCurrency) + '\n')
        #logging.info('Own ' + str(ownCrypto) + '\n')
        cryptoRunStats.newStats(statDict, startMinute, didBuy, didSell, currentCurrency, oldCurrency, cryptosSeperated, cycles, timeHeld, numAbstain, owned)
        resetDecisionsStored(cryptosSeperated)

        cycles += 1

    #print to file the final percent changes over the run
    #logging.info("Cumulative percent change over the life of all cryptos owneed so far " + str(PARAMETERS['CUMULATIVE_PERCENT_CHANGE_STORE']))

    # sell if there is a crypto left and increment numSells
    sellBin(currentCurrency)
    numSells += 1

    # set variables of the crypto stat analysis object
    cryptoRunStats.setVal(numBuys, 0)
    cryptoRunStats.setVal(numSells, 1)
    #logging.info("NUM SELLS  " + str(numSells)+ '\n')
    cryptoRunStats.setVal(allOwnedCryptoPercentChanges, 2)

    # has the bot do any final calculations
    PARAMETERS['END_MONEY'] = cryptoRunStats.finalCalculations()

    #write the analysis to the file
    cryptoRunStats.writeToFile()

    #set the number of cycles of buying and selling to whichever was lower, the number of times buying or selling
    if numBuys > numSells:
        PARAMETERS['CYCLES'] = numSells
    else:
        PARAMETERS['CYCLES'] = numBuys

    #write back to the param pickle file
    writeParamPickle(PARAMETERS, classdirectory + 'variations/', str(int(storedInput['variationNum'])) + 'param.pkl')


if __name__ == "__main__":
    main()
