# Copyright (c) 2018 A&D
# Auto trading bot that uses params sent by CryptoTrainer to test them


import os
import sys
import CryptoStatAnalysis
import datetime
import pathlib
import CryptoStats
import pickle
import logging


from ErrorCodes import ErrorCodes
from PriceSymbolsUpdater import getStoredSymbols
from CryptoDistribution import readPickle
from CryptoTrainer import  minInDay
from Generics import PARAMETERS, defaultcryptoevaluatorparamspassed, calcPercentChange, mininhour, hourinday, nextDay, implicitcryptodivisions, \
    normalizationValuesToStore, persistentdataforscoretypenames, numFiles, percenttodecimal, defaulterrorflagsforcryptoevaluator

try:
    from urlib import urlencode

except ImportError:
    from urllib.parse import urlencode


# todo make a series of functions used that have random variables in them and random variables left out instead of a simple linear score and simple parameter variation
# todo add in a parser for the stdin
# todo add a minimum volume parameter to weed out the cryptos not traded at a high enough rate
# todo add a minimum financial transaction amount per minute that must be occuring (uses the minimum volume and current price of each crypto)

# GLOBAL_VARIABLES



# How much of bitcoin balance to buy to purhcase more of the crypto (should be fixed to account for the fee of buying)
PERCENT_QUANITITY_TO_SPEND = .9




# the binance intervals, their symbols, and their time in milliseconds
intervalTypes = {'1m': {'symbol': '1m', 'inMS': 60000}, '3m': {'symbol': '3m', 'inMS': 180000}, '5m': {'symbol': '5m', 'inMS': 300000},
                 '15m': {'symbol': '15m', 'inMS': 900000}, '30m': {'symbol': '30m', 'inMS': 1800000}, '1h': {'symbol': '1h', 'inMS': 3600000},
                 '2h': {'symbol': '2h', 'inMS': 7200000}, '4h': {'symbol': '4h', 'inMS': 14400000}, '6h': {'symbol': '6h', 'inMS': 21600000},
                 '8h': {'symbol': '8h', 'inMS': 28800000}, '12h': {'symbol': '12h', 'inMS': 43200000}, '1d': {'symbol': '1d', 'inMS': 86400000},
                 '3d': {'symbol': '3d', 'inMS': 259200000}, '1w': {'symbol': '1w', 'inMS': 604800000}, '1M': {'symbol': '1M', 'inMS': 2629746000}}



# decimal precision allowed for trading each crypto
stepsizes = {}




# whether testing or not
testCheck = 0



file = ''
picklefile = ''

# todo finish implementing this system of tracking the crypto we currently own


# you can use the words instead of these values
YES = 1
NO = 0

realInterval = 0

onehourinmins = 60

#setup the log file for this evaluator
def setUpLog(logdirectory, logfilename):

    logging.basicConfig(filename=logdirectory+logfilename, level='DEBUG')


#makes the corresponding log and variation directory for this evaluator
def initdirectories(paramspassed, dirname, paramstostore, typedirec='storage'):
    """
    :param paramspassed: the params passed from the file running this evaluator
    :param dirname: the base directory relative to the file system
    :param paramstostore: the parameter dictionary to store if there are none stored and this is a solo run evaluator
    :param typedirec: the directory type (training or storage)
    :return:
    """
    directory = "{}/{}/{}/{}/{}/{}/{}/{}/".format(dirname, typedirec, paramspassed['website'], paramspassed['day'], paramspassed['hour'],
                             paramspassed['min'], paramspassed['idnum'], paramspassed['classNum'])

    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
    pathlib.Path(directory + "logs/").mkdir(parents=True, exist_ok=True)

    #if the directory prefix is consistent with this being a solo run evaluator then write and store an evaluator file
    #if none is currently in the directory
    if numFiles(directory) == 0 and paramspassed['directoryprefix'] == 'CryptoEvaluator':
        writeParamPickle(paramstostore, directory, '{}param.pkl'.format(paramspassed['variationNum']))

#reads pickle from a file into the passed parameter dictionary
def readParamPickle(directory, filename):
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


def readTheInput(paramspassed, evaluatorparams, directory):
    """
    :param paramspassed: the params passed to the evaluator
    :param evaluatorparams: the evaluatorparams used by the evlauator to make its decisions
    :param directory: the directory that we will look
    :return: updated paramspassed and evaluator params
    """

    if sys.argv[1] == "CryptoEvaluator": #if there are more than one argument than we know this is being run from a separate file
        # make the max cycles equal to the number of days of the interval in hours
        evaluatorparams['MAX_CYCLES'] = (evaluatorparams['INTERVAL_TO_TEST'] / minInDay) * 24.0
        paramspassed['directoryprefix'] = sys.argv[1]
        paramspassed['website'] = sys.argv[2]
        paramspassed['day'] = sys.argv[3]
        paramspassed['hour'] = sys.argv[4]
        paramspassed['min'] = sys.argv[5]
        paramspassed['variationNum'], evaluatorparams['VARIATION_NUMBER'] = sys.argv[6], sys.argv[6]
        paramspassed['classNum'], evaluatorparams['CLASS_NUM'] = sys.argv[7], sys.argv[7]  #default should be -1
        paramspassed['idnum'] = sys.argv[8]
        paramspassed['lossallowed'] = sys.argv[9]
        paramspassed['startmoney'] = sys.argv[10]

        truedirectory = '{}/{}'.format(directory, sys.argv[1])

        return paramspassed, truedirectory


    elif len(sys.argv) != 3:  # if there are no evaluatorparams passed (will be = 3 if this is being run as a subprocess)
        # make the max cycles equal to the number of days of the interval in hours
        evaluatorparams['MAX_CYCLES'] = (evaluatorparams['INTERVAL_TO_TEST'] / minInDay) * 24.0
        evaluatorparams['CLASS_NUM'] = -1

        # setup the directory to account for this being a single evaluator run
        truedirectory = '{}/CryptoEvaluator'.format(directory)

        return paramspassed, truedirectory

    else: #the evaluatorparams have been passed from another script that is running this one

        for line in sys.stdin:

            if line != '':
                # split the passed string into a list seperated by spaces
                listSplits = line.split(' ')
                #loops through the different values split from the input and stores them in a dictionary
                count = 0
                for key, value in paramspassed.items():
                    paramspassed[key] = listSplits[count]
                    count += 1

        truedirectory = '{}/{}'.format(directory, paramspassed['directoryprefix'])



    return paramspassed,  truedirectory

#get the balance in bitcoins

#buy the specified crypto currency
def buyBin(currency, currentMinute, currencyToTrade, openpricedata):
    """
    :param currency: currency to buy
    :param currentMinute: the current minute of the simulation
    :param currencyToTrade: the currency to sell for the other currency
    :param openpricedata: the list of close prices by minute for the currency
    :return: the price the crypto was bought at, the true bought price (same as the price right now), the crypto
    symbol owned now
    """

    ratio = getbinanceprice(currency, currentMinute, openpricedata)
    priceBought = ratio
    truePriceBought = ratio
    owned = currency

    # mark item as the current crypto being traded and save the buy price at for failure condition
    entry = {currency: {'buyPrice': ratio, 'timestamp': 0}}
    currencyToTrade.clear()
    currencyToTrade.update(entry)

    return priceBought, truePriceBought, owned

# sell the specified crypto
def sellBin(currency):
    """
    :param currency: the currency to buy
    :return:
    """
    return 0


#TODO this function will update the weighted moving average every second the program runs
# def updateWeightedMovingAverage(currency, interval, starttime, endtime):


#get the cumulative volume of the hour ending at the current minute
def getVolume(currency, currentMinute, volumeData, openpricedata):
    """
    :param currency: the currency to evaluate
    :param currentMinute: the current minute in the simulation
    :param volumeData: the list of volumes
    :param openpricedata: the list of close prices for the current crypto
    :return:
    """
    volume = []
    # adds up all the volumes over the interval (starting from an hour from the current minute)
    for x in volumeData[currentMinute - onehourinmins: currentMinute]:
        if(x != ''):
            x = float(x)
            x *= float(getbinanceprice(currency, currentMinute, openpricedata[currency]))
        else:
            x = 0.0
        volume.append(x)

    return volume



# get the binance price of the specified currency


def getbinanceprice(currency, currentMinute, openpricedata):
    """
    :param currency: the currency to get the price of
    :param currentMinute: the current minute of the simulation
    :param openpricedata: the dictionary of close prices for each minute for the current crypto
    :return:
    """
    if openpricedata == {} or currency == '':
        return 0.0

    binPrice = openpricedata[currentMinute]

    return binPrice

    # interval based on this from binance API
    #     m -> minutes;     h -> hours;     d -> days;     w -> weeks;    M -> months
    #  1m  3m   5m  15m  30m  1h 2h 4h 6h 8h  12h  1d   3d  1w   1M
    # method used to update price lists on past hour of trends

# method to iterate through all the cryptos available on binance and store their price changes, percent price changes,
# volume changes, percent volume changes, scores, time increasing, and time decreasing


def updateCrypto(firstminindex, lastminindex, ownedcrypto, params, openPriceData, closePriceData, volumeData,
                 highPriceData, lowPriceData, cryptoSymbols, dataForScore, combinedParamData, cryptosSeperated,
                 persistentancillarydataforscore, maxdataforscore, percentChanges, volumeAmounts, volumePercentChanges,
                 scores, currencyToTrade, namesofvaluestostore, maxdataforcombinedparams):
    """
    :param firstminindex: the start minute of the interval to evaluate
    :param lastminindex: the end minute of the interval to evaluate
    :param ownedcrypto: the current crypto owned
    :param params: the parameters used by this bot
    :param openPriceData: the dictionary of all the open prices
    :param closePriceData: the dictionary of all the close prices
    :param volumeData: the dictionary of all the volumes
    :param highPriceData: the dictionary of all the high prices
    :param lowPriceData: the dictionary of all the low prices
    :param cryptoSymbols: the dictionary of the symbols for each currency
    :param dataForScore: the dictionary with any data needed to calculate the score
    :param combinedParamData: the dictionary with any calculated data for each combined parameter type
    :param cryptosSeperated: the dictionary of lists of implicit divisions made by the bot as it works through the
        cryptos
    :param persistentancillarydataforscore: the data stored to survive the automatic reset of dataforscore
        so that it can be used repeatedly
    :param maxdataforscore: the dictionary of the max values for each type of calculation for the score
    :param percentChanges: the dictionary of percent changes between the open and close price of each minute
    :param volumeAmounts: the dictionary of volumes amounts traded by minute
    :param volumePercentChanges: the volume percent changes by minute
    :param dataForScore: the dictionary with any data needed to calcualate the score
    :param scores: the dictionary used to store the score of each crypto for this updateCrypto run
    :param currencyToTrade: the dictionary of currencies we can trade
    :param namesofvaluestostore: the list with names of values to store for the score
    :param combinedparamsvalues: the dictionary with lists for each each type of combined parameter value
    :param maxdataforcombinedparams: the dictionary for each type of combined parameter value that stores the max
    :return:
    """


    #TODO find code and separate it out into these functions OR write new ones with new code if they do not exits

    #reset the dictionary of data used for the score
    setUpScoringDataDictionary(dataForScore, cryptoSymbols, namesofvaluestostore, maxdataforscore)

    #setup the dictionaries to hold the calculated values and the max for each combined parameter type
    setupStoredCalculationsForCombinedParams(combinedParamData, maxdataforcombinedparams, params['COMBINED_PARAMS'],
                                             cryptoSymbols)

    for key,  currency in cryptoSymbols.items():

        # Pulling the data for each of the five core types for the current symbol
        openPriceDataLocal = openPriceData[currency]
        closePriceDataLocal = closePriceData[currency]
        highPriceDataLocal = highPriceData[currency]
        lowPriceDataLocal = lowPriceData[currency]
        volumeDataLocal = volumeData[currency]

        # todo figure out why this and the one below always starts at 0

        #get the opening volume at the starting minute of the hour interval
        firstvolume = volumeDataLocal[firstminindex]

        #get the closing volume at the ending minute of the hour interval
        lastvolume = volumeDataLocal[lastminindex]

        #get the open price at the starting minute of the hour interval
        firstopenprice = openPriceDataLocal[firstminindex]

        #get the last close price from the ending minute of the interval
        lastcloseprice = closePriceDataLocal[lastminindex]


        #get the highest high price for the hour interval (and replace the currently stored highest high price for the
        #whole simulation
        highesthighprice = findhighpriceandupdatehighestoverall(highPriceDataLocal,
                                                                persistentancillarydataforscore[currency], firstminindex,
                                                                lastminindex)

        #get the lowest low price for the hour interval (and replace the currently stored lowest low price for the
        #whole simualtion
        lowestlowprice = findlowpriceandupdatehighestoverall(lowPriceDataLocal,
                                                             persistentancillarydataforscore[currency], firstminindex,
                                                             lastminindex)


        # get the highest high price overall
        highesthighpriceoverall = persistentancillarydataforscore[currency]['HIGHEST_HIGH_PRICE']

        # get the lowest low price overall
        lowestlowpriceoverall = persistentancillarydataforscore[currency]['LOWEST_LOW_PRICE']

        #get the difference between the highest high price and lowest low price over the whole simulation
        dataForScore[currency]['DIFF_HIGH_AND_LOW_PRICE_OVERALL'] = calcPercentChange(
            highesthighpriceoverall, lowestlowpriceoverall)

        #########################PERCENT BY HOUR CALCULATIONS #########################################

        #get the percent change in price over the hour comparing the open and close price
        dataForScore[currency]['PERCENT_BY_HOUR_OPEN_CLOSE'] = calcPercentChange(firstopenprice, lastcloseprice)

        #get the percent change in price over the hour comparing the high and low price
        dataForScore[currency]['PERCENT_BY_HOUR_HIGH_LOW'] = calcPercentChange(highesthighprice, lowestlowprice)

        #get the percent change in price over the hour comparing the open and highest prices
        dataForScore[currency]['PERCENT_BY_HOUR_OPEN_HIGH'] = calcPercentChange(firstopenprice, highesthighprice)

        #get the percent change in price over the hour comparing the open and lowest prices
        dataForScore[currency]['PERCENT_BY_HOUR_OPEN_LOW'] = calcPercentChange(firstopenprice, lowestlowprice)

        #get the percent change in price over the hour comparing the high and close prices
        dataForScore[currency]['PERCENT_BY_HOUR_HIGH_CLOSE'] = calcPercentChange(highesthighprice, lastcloseprice)

        #get the percent change in price over the hour comparing the low price and close prices
        dataForScore[currency]['PERCENT_BY_HOUR_LOW_CLOSE'] = calcPercentChange(lowestlowprice, lastcloseprice)

        # todo figure out if it should have been endMinute - startMinute - 1 or just endMinute - 1
        # get the percent change in volume over the hour comparing the starting volume traded and the last volume traded
        dataForScore[currency]['VOLUME_PERCENT_BY_HOUR'] = calcPercentChange(firstvolume, lastvolume)

        #################### PRICE AND VOLUME TIME INCREASING CALCULATIONS#######################################


        # iterate through all the open and close prices for the given interval
        percentChanges[currency][:] = []
        for i in range(firstminindex, lastminindex):
            i += 1
            #caclualte and store the percent changes between the open price of one minute and the close price of the next
            percentChanges[currency].append(calcPercentChange(openPriceDataLocal[i - 1], closePriceDataLocal[i]))

        #values used to indicate whether this is a weighted calculation
        notweighted = 0
        weighted = 1

        #get the values for the weighted and unweighted time over the interval that the price of this crypto  increased
        dataForScore[currency]['PRICE_TIME_INCREASING_UNWEIGHTED'] = getPriceTimeIncreasing(notweighted, params,
                                                                                            percentChanges[currency])
        dataForScore[currency]['PRICE_TIME_INCREASING_WEIGHTED'] = getPriceTimeIncreasing(weighted, params,
                                                                                          percentChanges[currency])

        # reset the lists of the volume amounts and volume percent changes
        volumeAmounts[currency][:] = []
        volumePercentChanges[currency][:] = []

        # calculate and store the percent time increasing for volume and price percent changes
        for w in range(firstminindex, lastminindex):
            w += 1
            volumePercentChanges[currency].append(calcPercentChange(volumeDataLocal[w - 1], volumeDataLocal[w]))
            volumeAmounts[currency].append(volumeDataLocal[w])

        #get the values for the weighted and unweighted time over the interval that the volume traded of this crypto increased
        dataForScore[currency]['VOLUME_TIME_INCREASING_UNWEIGHTED'] = \
            getVolumeTimeIncreasing(notweighted, params, volumePercentChanges[currency])
        dataForScore[currency]['VOLUME_TIME_INCREASING_WEIGHTED'] = \
            getVolumeTimeIncreasing(weighted, params, volumePercentChanges[currency])

        # get the modified volume changes
        dataForScore[currency]['MODIFIED_VOLUME'] = getModifiedVolume(currency, params,
                                                                      percentChanges[currency], volumeAmounts[currency])

        # calculate a weightedMovingAverage
        dataForScore[currency]['MOVING_AVERAGE'] = setWeightedMovingAverage(currency, firstminindex, lastminindex, params,
                                                                   closePriceDataLocal
                                                                  ,openPriceDataLocal)

        #update whether each crypto has been purchase
        updatecryptosbought(persistentancillarydataforscore, ownedcrypto)

        #update the counter for how many times each crypto has been owned
        updatecryptosboughtnumberoftimes(persistentancillarydataforscore, ownedcrypto)

    # copy over values that should are persistently stored
    copypersistentdataover(dataForScore, persistentancillarydataforscore)

    #calculate the combined parameter values for all the cryptos
    calculateCombinedParameterValues(params, cryptoSymbols, combinedParamData, dataForScore)

    #set the maximum values for each type calculated
    setMaxValue(dataForScore, maxdataforscore)

    #set the maximum values for each type calculated for the combined parameters
    setMaxValuesCombinedParams(combinedParamData, maxdataforcombinedparams)

    # gets the score for each crypto
    # moved to its own loop so all the values can be properly scaled by the largest value
    for key, currencyname in cryptoSymbols.items():

        # use the calculations to get a score
        calc_score = getScore(params, maxdataforscore, namesofvaluestostore, dataForScore[currencyname],
                              combinedParamData[currencyname],
                              maxdataforcombinedparams)
        new_score = {currencyname: calc_score}
        scores.update(new_score)


    # add cryptos and their scores to dictionary of currencies to trade if they are above the minimum score
    for currencyname, scoreforcurrency in scores.items():

        #make a dictioanry entry for this score and crypto
        entry = {currencyname: scoreforcurrency}

        #if the score is higher than the minimum score
        if (scoreforcurrency > params['MINIMUM_SCORE']):
            #add the crypto-score pair to the dictionary of tradeable currencies
            currencyToTrade.update(entry)

            #add the current crypto into the list of cryptos chosen to be considered for buying
            cryptosSeperated['Chosen'].append(currencyname)

        #if the crypto did not have a score sufficient for consideration
        else:
            cryptosSeperated['Disregarded'].append(currencyname)

    #logging.info("Currrenty to trade: " + str(currencyToTrade))

#copy any data that has to be shared from the persistent data store to the normal data store dictionary
def copypersistentdataover(dataforscore, persistentancillarydataforscore):

    #loop thorough each crypto currency and its associated data types
    for currencyname, datatypedict in dataforscore.items():

        #loop through the each datatype dictionary to look at each datatype and its value
        for datatype, datatypevalue in datatypedict.items():

            #check if the data type is one of the persistent ones
            if datatype in persistentancillarydataforscore[currencyname]:
                #store the value currently persistently stored in the normal data dictionary
                dataforscore[currencyname][datatype] = persistentancillarydataforscore[currencyname][datatype]


#calculate all values for the different combined parameters for this crypto
def calculateCombinedParameterValues(params, cryptoSymbols, storedvaluesforcombinedparams,
                                     storeddataforscore):
    """
    :param params: the list of parameters used by the bot to trade
    :param cryptoSymbols: the dictionary of the price symbols for each crypto
    :param storedvaluesforcombinedparams: the dictionary of lists to store each value of the combined parameters
    :param storeddataforscore:
    :return:
    """

    #loop through each combined parameter
    for combinedparamindex in range(len(params['COMBINED_PARAMS'])):

        #loop through the different cryptos
        for key, currencyname in cryptoSymbols.items():

            #loop through the parameters that need to be combined
            for combinedparam in params['COMBINED_PARAMS'][combinedparamindex]:

                #get the operator for the combined parameter in the list of parameters to be combined
                combinedparamoperator = combinedparam.split()[0]

                #get the name of the parameter to be combined
                paramname = combinedparam.split()[1]

                #if the operator is addition
                if combinedparamoperator == '+':
                    #add the desired parameter value to the value for the current combined parameter for this crypto
                    storedvaluesforcombinedparams[currencyname][combinedparamindex] += \
                        storeddataforscore[currencyname][paramname]

                #if the operator is subtraction
                elif combinedparamoperator == '-':
                    #subtract the desired parameter value to the value for the current combined parameter for this crypto
                    storedvaluesforcombinedparams[currencyname][combinedparamindex] -= \
                        storeddataforscore[currencyname][paramname]

                #if the operator is multiplication
                elif combinedparamoperator == '*':
                    # multiply the desired parameter value to the value for the current combined parameter for this crypto
                    storedvaluesforcombinedparams[currencyname][combinedparamindex] *= \
                        storeddataforscore[currencyname][paramname]

                #otherwise throw an error
                else:
                    logging.error("Not a valid operator for combined params {}".format(combinedparamoperator))
                    logging.error("combined param {} and index {}".format(paramname, combinedparamindex))




# calculates and returns the time spent increasing
# weighted = 0 is false, weighted = 1 is true
 # TODO update the modulo so that it is a modulo not a multiplcation so that patterns are detected
def getPriceTimeIncreasing(isWeighted, params, pricePercentChanges):
    """
    :param isWeighted: boolean value for whether this is a weight time increasing or nonweighted
    the weight refers to whether the more recent the price change is the more significant it is
    :param percentChanges: the dictionary of percent changes of the open and close price for each minute
    :return: the number representing how often this crypto currency was increasing over the time period
    """

    #return the calculated value for price time increasing with or without weight
    if isWeighted == 1:
        return getPriceTimeIncreasingWeighted(pricePercentChanges, params)
    else:
        return getPriceTimeIncreasingUnWeighted(pricePercentChanges, params)


#calculate and return the amount of time that the crypto price was increasing in value without a weight
def getPriceTimeIncreasingUnWeighted(listpricepercentchanges, params):
    """
    :param listpricepercentchanges: list of the price percent changes
    :param params: the parameters used by the bot to make decisions
    :return: the number representing how often this crypto was increasing over the time period without a weight
    """

    slots = 0.0
    slotsincreasing = 0.0

    for minpricepercentchange in listpricepercentchanges:

        slots += 1

        if float(minpricepercentchange) > 0.0:
            slotsincreasing += 1 * minpricepercentchange

        if float(minpricepercentchange) < 0.0:
            slotsincreasing += 1 * minpricepercentchange * params['PRICE_TIME_INCREASING_NEGATIVE_UNWEIGHTED_MODIFIER']


    if(slots == 0.0):
        slots = 1.0

    pricetimeincreasingunweighted = (slotsincreasing / slots)

    return pricetimeincreasingunweighted

#calculate and return the amount of time that the crypto price was increasing in value with a weight
#that makes more recent increases more important
def getPriceTimeIncreasingWeighted(listpricepercentchanges, params):
    """
    :param listpricepercentchanges: list of the price percent changes
    :param params: the parameters used by the bot to make decisions
    :return: the number representing how often this crypto was increasing over the time period with a weight
    """

    slots = 0.0
    slotsincreasing = 0.0

    for minpricepercentchange in listpricepercentchanges:
        slots+=1

        if float(minpricepercentchange) > 0.0:
            slotsincreasing += (1 * (slots * params['PRICE_TIME_INCREASING_SLOT_WEIGHTED_MODIFIER'])
                                * minpricepercentchange)

        if float(minpricepercentchange) < 0.0:
            slotsincreasing += (1 * (slots * params['PRICE_TIME_INCREASING_SLOT_WEIGHTED_MODIFIER'])
                                * minpricepercentchange *
                                params['PRICE_TIME_INCREASING_NEGATIVE_WEIGHTED_MODIFIER'])

    if (slots == 0.0):
        slots = 1.0

    pricetimeincreasingweighted = (slotsincreasing / slots)

    return pricetimeincreasingweighted

# caclulates and returns the time spent increasing for volume
# weighted = 0 is false, weighted = 1 is true
def getVolumeTimeIncreasing(isWeighted,  params, volumePercentChanges):
    """
    :param isWeighted: boolean representing whether this is a weighted calculation or not
    weighted implies that the more recently the increase in volume occured the more signficance it is given
    :param params: the parameters used by this bot to trade
    :param volumePercentChanges: the list of the volume percent changes for a particular crypto
    :return: the calculated value representing the amount of minutes that the volume increased (weighted or unweighted)
    """

    # return the calculated value for volume time increasing with or without weight
    if isWeighted == 0:
        return getVolumeTimeIncreasingUnWeighted(params, volumePercentChanges)

    else:
        return getVolumeTimeIncreasingWeighted(params, volumePercentChanges)



#calculate the unweighted value representing the number of minutes that the volume was increasing
def getVolumeTimeIncreasingUnWeighted(params, volumePercentChanges):
    """
    :param params: the parameters used by the bot for trading
    :param volumePercentChanges: the list of volume percent changes for this particular crypto
    :return: the calculated value representing the amount of minutes that the volume increased. unweighted
    """

    slots = 0.0
    slots_increasing = 0.0

    for minvolumepercentchange in volumePercentChanges:
        slots += 1

        if float(minvolumepercentchange) > 0.0 :
            slots_increasing += 1 * minvolumepercentchange

        if float(minvolumepercentchange) < 0.0:
            slots_increasing += 1 * minvolumepercentchange \
                                * params['PRICE_TIME_INCREASING_NEGATIVE_UNWEIGHTED_MODIFIER']


    if (slots == 0.0):
        slots = 1.0

    volumetimeincreasingunweighted = (slots_increasing / slots)

    return volumetimeincreasingunweighted


#calculate the weighted value representing the number of minutes that the volume was increasing. weighted implies
#that the more recent an increase the more it is considered in the calculation
def getVolumeTimeIncreasingWeighted(params, volumePercentChanges):
    """
    :param params: the parameters used by the bot for trading
    :param volumePercentChanges: the list of volume percent changes for this particular crypto
    :return: the calculated value representing the amount of minutes that the volume increased. weighted
    """

    slots = 0.0
    slots_increasing = 0.0

    for minvolumepercentchange in volumePercentChanges:
        slots += 1

        if float(minvolumepercentchange) > 0.0:
            slots_increasing += (1 * (slots * params['VOLUME_TIME_INCREASING_SLOT_WEIGHTED_MODIFIER'])
                                 * minvolumepercentchange)

        if float(minvolumepercentchange) < 0.0:
            slots_increasing += (1 * (slots * params['VOLUME_TIME_INCREASING_SLOT_WEIGHTED_MODIFIER'])
                                 * minvolumepercentchange * params['VOLUME_TIME_INCREASING_NEGATIVE_WEIGHTED_MODIFIER'])

    if (slots == 0.0):
        slots = 1.0

    volumetimeincreasingweighted = (slots_increasing / slots)

    return volumetimeincreasingweighted

#TODO add in the weight
# calculates the weighted moving average over the specified interval for a crypto currency

def setWeightedMovingAverage(currency, startMinute, endMinute, params, openPriceData, closePriceData):
    """
    :param currency: the currency to evaluate
    :param startMinute: the start minute of the interval being looked at
    :param endMinute: the end minute of the interval being looked at
    :param params: the parameters used by this bot
    :param openPriceData: the dictionary of open prices
    :param closePriceData: the dictionary of close prices
    :return: the moving average for the period and crypto currency
    """

    cumulativePrice = 0.0

    slots = endMinute - startMinute - 1

    if openPriceData == []:
        return 0

    # adds up the cumulative price changes using each interval
    for x in range(startMinute, endMinute):
        startPrice = openPriceData[x]
        endPrice = closePriceData[x]
        change = calcPercentChange(startPrice, endPrice)

        cumulativePrice += change

    # the scaling of the cumulative price
    cumulativePrice = (cumulativePrice / slots) * params['CUMULATIVE_PRICE_MODIFIER']

    return cumulativePrice

# grabs the list of volumes over the interval and percent changes over the interval
# then iterates through and calculates a cumulative volume where the volume is considered negative
# when the percent change was negative and positive when the percent change was positive
def getModifiedVolume(currency, params, percentChanges, volumeAmounts):
    """
    :param currency: currency to get the modified volume of
    :param params: the parameters used by this bot
    :param percentChanges: the percent changes between the open and close price each minute
    :param volumeAmounts: the volume amounts traded for each minute
    :return: the modified volume for this currency
    """
    oldVolume = 0.0

    #current slot in time
    currentSlot = 0

    # adds up the volume with negative percent changes in price resulting in the volume
    # considered to be mostly 'negative', how much is determined by the magnitude
    # of the percent change in price
    for currvolume in volumeAmounts:

        # makes each volume % change back into a decimal

        percentChangeScale = (percentChanges[currentSlot])

        if percentChangeScale < 0:
            oldVolume += percentChangeScale * float(currvolume) * params['MODIFIED_VOLUME_NEGATIVE_MODIFIER']

        # todo the below may have not been there for the last set of tests
        if percentChangeScale >= 0:
            oldVolume += percentChangeScale * float(currvolume)

        currentSlot += 1

    return float(oldVolume)

# method to calculate the "score" that crypto get when they are updated by hour
# score is a combination of weighted time increasing and % change over hour.
# for both volume and price


def getScore(params, maxCryptoCalculationsStored, listofscorevariables,
             dataForScore, combinedParamData, maxCombinedParamsCryptoCalculationsStored):
    """
    :param params: the parameters used by the bot to trade with
    :param maxCryptoCalculationsStored: the dictionary of the max of each calculated value for each variable used in score
    :param listofscorevariables: the list with the key name for each variable used in calcualting the score
    :param dataForScore: the dictionary used to calculate and store data relevant to the score calculation
    :param combinedParamData: the dictionary used to calculate and store data for each combined parameter set
    :param maxCombinedParamsCryptoCalculationsStored: the max of all the calculated values for the combined parameter calculation for each crypto
    :return: the calculated score
    """
    newscore = 0.0

    #add to the score the normal data types
    for datatype in listofscorevariables:

        #scale the data value by the maximum stored data value for that type from all the cryptos and
        #multiply by the associated parameter modifier
        try:
            #if the max is zero we do not divide by anything
            if maxCryptoCalculationsStored[datatype] == 0:
                newscore += (dataForScore[datatype]) * params["{}_MODIFIER".format(datatype)]
            else:
                newscore += (dataForScore[datatype]/maxCryptoCalculationsStored[datatype]) \
                            * params["{}_MODIFIER".format(datatype)]
        except ZeroDivisionError:
            logging.error("Normal score division by zero. ")
            logging.error("datatype {}".format(datatype))
            logging.error(" dataforscore value {}".format(dataForScore[datatype]))
            logging.error(" max value {}".format(maxCryptoCalculationsStored[datatype]))

    #add to the score the combined parameter data
    for combinedparamdatatypeindex in range(len(params['COMBINED_PARAMS'])):
        #scale the combined parameter data value by the maximum stored combined parameter data value for all cryptos
        #and multiply by the associated parameter modifier

        #if the max is zero we do not divide by anything
        if maxCombinedParamsCryptoCalculationsStored[combinedparamdatatypeindex] == 0:
            newscore += combinedParamData[combinedparamdatatypeindex] \
                         * params['COMBINED_PARAMS_MODIFIERS'][combinedparamdatatypeindex]
        else:
            newscore += (combinedParamData[combinedparamdatatypeindex] /
                     maxCombinedParamsCryptoCalculationsStored[combinedparamdatatypeindex]) \
                    * params['COMBINED_PARAMS_MODIFIERS'][combinedparamdatatypeindex]


    return newscore

#find the high price for the hour interval and update the currently stored highest price for the currency
# update the amount of time that has passed since we updated the highest price as well as the number of times that
# the highest price has been surpassed or reached
def findhighpriceandupdatehighestoverall(highprices, persistentdata, startminute, endminute):
    """
    :param highprices: list of high prices over the interval for the current crypto
    :param persistentdata: the dictionary of persistently stored data
    :param startminute: the startminute of the interval
    :param endminute: the endminute of the interval
    :return: the highest price of the hour interval
    """

    #initialize the highest price for the hour
    highestprice = -1000

    #trim high prices to only be the right data
    highprices = highprices[startminute: endminute]

    #loop through every minute of the high prices
    for minute in range(len(highprices)):

        #if the current minute's high price is higher than the current local high price
        if float(highprices[minute]) >= float(highestprice):
            highestprice = highprices[minute]

        #if the high price matches or surpasses the current highest
        if float(highprices[minute]) >= float(persistentdata['HIGHEST_HIGH_PRICE']):

            #write over the current highest price
            persistentdata['HIGHEST_HIGH_PRICE'] = highprices[minute]

            #reset the minutes since we matched or surpassed the highest price
            persistentdata['MINS_SINCE_LAST_HIGH_PRICE'] = 0

            #increment the number of times we have reached or surpassed the highest price
            persistentdata['TIMES_REACH_OR_SURPASS_HIGH_PRICE'] += 1

        #if we do not reach or surpass the high price
        else:
            #increment the number of minute since we reached or surpassed the highest price
            persistentdata['MINS_SINCE_LAST_HIGH_PRICE'] += 1

    return highestprice

#find the low price for the hour interval and update the currently stored lowest price for the currency
# update the amount of time that has passed since we updated the lowest price as well as the number of times
# that the lowest price has been surpassed or reached
def findlowpriceandupdatehighestoverall(lowprices, persistentdata, startminute, endminute):
    """
    :param lowprices: list of low prices over the interval for the current crypto
    :param persistentdata: the dictionary of persistently stored data
    :param startminute: the startminute of the interval
    :param endminute: the endminute of the interval
    :return: the lowest price of the hour interval
    """
    #initialize the lowest price for the hour
    lowestprice = 100000

    #trim low prices to only be the right data
    lowprices = lowprices[startminute: endminute]

    #loop through every minute of the high prices
    for minute in range(len(lowprices)):

        #if the current minute's low price is lower than the current local low price
        if float(lowprices[minute]) >= float(lowestprice):
            lowestprice = lowprices[minute]

        #if the low price matches or fell below the current lowest
        if float(lowprices[minute]) >= float(persistentdata['LOWEST_LOW_PRICE']):

            #write over the current lowest price
            persistentdata['LOWEST_LOW_PRICE'] = lowprices[minute]

            #reset the minutes since we matched or fell below the lowest price
            persistentdata['MINS_SINCE_LAST_LOW_PRICE'] = 0

            #increment the number of times we have reached or fell below the lowest price
            persistentdata['TIMES_REACH_OR_FALL_BELOW_LOW_PRICE'] += 1

        #if we do not reach or fall below the low price
        else:
            #increment the number of minute since we reached or fell below the lowest price
            persistentdata['MINS_SINCE_LAST_LOW_PRICE'] += 1

    return lowestprice

#change value stored for the passed crypto to 1 to indicate it has been purchased before
def updatecryptosbought(persistentdataforscore, ownedcrypto):
    """
    :param persistentdataforscore: dictionary of persistent data used to calculate score
    :param ownedcrypto: the owned crypto
    :return:
    """

    persistentdataforscore[ownedcrypto].update({'OWNED_BEFORE': 1.0})


#increment the counter stored for the passed crypto to indicate it has been purchased another time
def updatecryptosboughtnumberoftimes(persistentdataforscore, ownedcrypto):
    """
    :param persistentdataforscore: dictionary of persistent data used to calculate score
    :param ownedcrypto: the owned crypto
    :return:
    """

    incrementedvalue = persistentdataforscore[ownedcrypto]['OWNED_BEFORE_EACH_TIME'] + 1

    persistentdataforscore[ownedcrypto].update({'OWNED_BEFORE_EACH_TIME': incrementedvalue})


# finds the next currency to buy by first whittling down the list of cryptos to those that pass a certain number
# of the minimum values and then find the one with the highest score of those
def priceChecker(params, currencyToTrade, scores, dataforscore, combinedparamdata, cryptosSeperated):
    """
    :param params: the parameters used by the bot to buy
    :param currencyToTrade: the dictionary of potential currencies to trade (can only choose one)
    :param scores: the dictionary with the scores for all the crypto currencies
    :param dataforscore: the dictionary with the data that is stored for all the cryptos
    :param combinedparamdata: the data used to calculate score from the combined parameters
    :param cryptosSeperated: the crypto currency separations that are implicitly made when calculatingg scores
    and selecting the one to buy
    :return: the currency we have decide to buy
    """
    currencyToBuy = ''

    #whittle down the list to just the cryptos that have elements higher than the minimum amounts specified in
    # our minimum params dictionary
    currencyToTrade = removecryptoswithoutadequateminimumvalues(params, currencyToTrade, dataforscore, combinedparamdata)

    # Compares the two price lists and sets the currencyToBuy to be
    # the coin with the highest score that also is above the minimum moving average
    maxScore = 0
    for key, value in currencyToTrade.items():
        try:
            if(maxScore < scores[key]):
                maxScore = scores[key]
                currencyToBuy = key

        except KeyError:
            logging.info(" key error " + str(key) + " scores[key] " + dataforscore[key]['MOVING_AVERAGE'] + '\n')

    #logging.info('Coin with the highest score is ' + str(currencyToBuy) + ' which is ' + str(maxScore) + '\n' )

    #remember to store the current highest score in the data dictionary
    cryptosSeperated['theMax'].append(currencyToBuy)

    return currencyToBuy  # potential runtime error if all negative todo

#iterate through the currency to trade dictionary and remove cryptos that do not have the minimum values for each
# data type specified
def removecryptoswithoutadequateminimumvalues(params, dictofcurrenciespossibletotradefor, dataforscore,
                                              combinedparamdata):
    """
    :param params: params used for this bot
    :param dictofcurrenciespossibletotradefor: dictionary with the possible crypto currencies to buy
    :param dataforscore: the data stored to calculate the score
    :param combinedparamdata: the data used to calculate score from the combined parameters
    :return: a new dictionary with only the cryptos that are qualified stay
    """

    finaldictionaryofcryptostotrade = {}

    #check that the stored minimum number of datatypes is a valid number
    checkminimumnumberofdatatypestopassiscorrect(params)

    #loop through each crypto in the list
    for currencyname, score in dictofcurrenciespossibletotradefor.items():

        #if the current crypto has data values above the minimum valus in the params dictionary for
        #datatype minimum values
        if(cryptohasadequateminimumvalues(params, dataforscore, combinedparamdata, currencyname)):
            finaldictionaryofcryptostotrade.update({currencyname: score})

    return finaldictionaryofcryptostotrade

#check if the minimum number of datatypes that a crypto needs to be higher than when comparing against
#the dict of data types used as minimums is a value not greater than the maximum number of minimums considered
def checkminimumnumberofdatatypestopassiscorrect(params):
    """
    :param params: the params used by this bot
    :return:
    """

    if params['minnumberofparameterminimumstopassforconsideration'] > len(params['PARAMS_CHECKED_FOR_MINIMUM_VALUES']):
        params['minnumberofparameterminimumstopassforconsideration'] = len(params['PARAMS_CHECKED_FOR_MINIMUM_VALUES'])

#checks if the current crypto has data type values above the minimums set in the params dict
def cryptohasadequateminimumvalues(params, dataforscore, combinedparamdata, currencyname):
    """
    :param params: params used for this bot
    :param dataforscore: the data stored to calculate the score
    :param combinedparamdata: the data used to calculate score from the combined parameters
    :param currencyname: the current crypto being evaluated
    :return:
    """

    #counter to track how many of the set minimum data values the current crypto has a data value higher than
    minimumdatavaluesbetterthan = 0

    #if there are no set minimum values
    if len(params['PARAMS_CHECKED_FOR_MINIMUM_VALUES']) == 0:
        return True

    for datatype, datavalue in params['PARAMS_CHECKED_FOR_MINIMUM_VALUES'].items():

        #if this is a normal data type
        if datatype in dataforscore[currencyname]:
            if dataforscore[currencyname][datatype] > datavalue:
                minimumdatavaluesbetterthan += 1
        #otherwise check if this is within the combined params list
        elif int(datatype) < len(params['COMBINED_PARAMS']):
            if combinedparamdata[currencyname][datatype] > datavalue:
                minimumdatavaluesbetterthan += 1
        else:
            logging.error("Not a valid datatype")
            quit(-1)


    if minimumdatavaluesbetterthan >= params['minnumberofparameterminimumstopassforconsideration']:
        return True

    return False

# checks if the current crypto has been decreasing the past ten minutes
# if yes it forces a new check to see if there is a better crypto
def checkFailureCondition(currency, timesIncreasing, openPriceData, countervalueforpositiveintervals,
                          countervalueforzeropercentchangeintervals):
    """
    :param currency: the currency being evaluated
    :param timesIncreasing: the number of times this can be increasing at minimum to not set off the failure flag
    :param openPriceData: the open price data dictionary
    :param countervalueforpositiveintervals: the amount added to timeincreasingcounter to keep track of the
        positive changes
    :param countervalueforzeropercentchangeintervals: the amount added to timeincreasingcounter to keep track
        of the negative changes
    :return: True if it decreased all intervals and must restart and False if nothing needs to be done
    """

    # get the starting price of the interval
    timeIncreasingCounter = 0

    # iterate through the list of percent changes and add up when the percent change was positive
    for minute in range(1,len(openPriceData[currency])):
        startPrice = openPriceData[currency][minute - 1]
        endPrice = openPriceData[currency][minute]
        percentChange = calcPercentChange(startPrice, endPrice)

        #give quarter credit if there was no percent change and full credit if it was a positive percent change
        if(percentChange > 0):
            timeIncreasingCounter += countervalueforpositiveintervals
        elif(percentChange == 0):
            timeIncreasingCounter += countervalueforzeropercentchangeintervals

    if(timeIncreasingCounter <= timesIncreasing):
        logging.info("DECREASED ALL INTERVALS. RESTART")
        return True

    return False

# checks whether the function has caused too large of negative decrease the specified interval


def checkTooNegative(currency, params, openPriceData, intervallength=1):
    """
    :param currency: the currency being evaluated
    :param params: the parameters used by this bot to trade
    :param openPriceData: the dictionary of open prices
    :param intervallength: the length of the interval to check if the decrease has been too negative (in minutes)
    :return: True if the flag has been set off and False if not. if flag is set up the crypto is sold
    """

    startPrice = openPriceData[currency][0]
    endPrice = openPriceData[currency][0 + intervallength]
    percentChange = calcPercentChange(startPrice, endPrice)


    # if the percent change is less than the negation of the absolute value of max decrease (ensures it is treated as negative
    if(percentChange < (-1 * abs((params['MAX_DECREASE'])))):
        logging.info("TOO NEGATIVE. RESTART")
        return True

    return False

# checks to see if the currency has increased or decreased more than is allowed
# if yes, then the reevaluation process is restarted


def checkPercentChangeOverHoldingTooExtreme(currency, currentMinute, params, priceBought, openpricedata):
    """
    :param currency: the currency being evaluated
    :param currentMinute: the current minute to check 
    :param params: the parameters used by the bot to trade
    :param priceBought: the price the currently owned crypto was bought at
    :param openpricedata: the close price list for the current crypto
    :return: True if a flag was set off requiring the crypto to be sold, False if not
    """ 
    
    #the current price of the the currency
    currentPrice = getbinanceprice(currency, currentMinute, openpricedata[currency])
    
    #the percent change since the price it was purchased at
    percentChange = calcPercentChange(priceBought, currentPrice)


    if(percentChange >  params['MAX_PERCENT_CHANGE_POSITIVE_HOLDING_PERIOD']):
        logging.info("HIT MAX PERCENT CHANGE")
        return True

    if(percentChange < params['MAX_PERCENT_CHANGE_NEGATIVE_HOLDING_PERIOD']):
        logging.info("HIT MINIMUM PERCENT CHANGE")
        return True

    return False

# checks to see if the current currency is too near to its starting point
def checkTooLow(currency, params, priceBought, openpricedataslice):
    """
    :param currency: the currency being looked at
    :param params: the parameters used by the bot for
    :param priceBought: the price that the currently owned cryptocurrency was purchased for
    :param openpricedataslice: the list of open prices for the current crypto for only a slice
    :return: True if this failure flag was set and the crypto must be sold, False otherwise
    """

    currentPrice = getbinanceprice(currency, 0, openpricedataslice[currency])
    floorPrice = params['FLOOR_PRICE_MODIFIER'] * float(priceBought)

    # checks to see if the coin was increasing or decreasing over the last 15 minutes. +13 since endMinute is
    # already one greater than start minute and +8 since checkFailureCondition uses 10 minute intervals
    direction = increasingOrDecreasing(currency, openpricedataslice[currency])


    # check to see if the current price is too low, the crypto is decreasing over the past 15 minutes
    # and all the intervals are decreasing
    if(float(currentPrice) < float(floorPrice) and direction == False ):
        logging.info("WAS TOO LOW")
        return True

    return False


# checks to see if the currency has increased or decreased more than is allowed
# if yes, then the simulation is ended
def checkPercentChangeOverWholePeriodExitSimulation(params):
    """
    :param params: the parameter dictionary
    :return: True if a flag was set off requiring a cessation fo the bots trading, False if not
    """
    if (params['CUMULATIVE_PERCENT_CHANGE_STORE'] > params['MAX_PERCENT_CHANGE_POSITIVE_WHOLE_PERIOD']):
        logging.info("HIT MAX PERCENT CHANGE")
        return True

    if (params['CUMULATIVE_PERCENT_CHANGE_STORE'] < params['MAX_PERCENT_CHANGE_NEGATIVE_WHOLE_PERIOD']):
        logging.info("HIT MINIMUM PERCENT CHANGE")
        return True

    return False

# returns whether the specified currency is increasing or decreasing over the interval
# 0 means decreasing, 1 means stable or increasing


def increasingOrDecreasing(currency, openpricedataslicetocheck):
    """
    :param currency: the currency currency being evaluated
    :param openpricedataslicetocheck: the open price dictionary
    :return: True if this was increasing and False if it was decreasing
    """


    startPrice = openpricedataslicetocheck[0]
    endPrice = openpricedataslicetocheck[-1]

    calcPChange = calcPercentChange(startPrice, endPrice)

    if(calcPChange >= 0.0):
        return True

    return False


# creates a dictionary with all the different statistic holding dictionaries that are created with each run


def createStatsDict(statsDictSetup, percentChanges, volumePercentChanges, volumeAmounts, storedDataForScore,
                    ):
    """
    :param statsDictSetup: the statistics dictionary to be updated
    :param percentChanges: the dictionary of the percent changes between the open and close prices for each minute
    :return:
    """
    statsDictSetup.update({'percentChanges': percentChanges})
    statsDictSetup.update({'volumePercentChanges': volumePercentChanges})
    statsDictSetup.update({'volumeAmounts': volumeAmounts})
    statsDictSetup.update({'storedDataForScore': storedDataForScore})


# sets all the list of how the cryptos were seperated back to being empty


def resetDecisionsStored(dict):
    """
    :param dict: the dictionary to be reset
    :return:
    """
    for key, value in dict.items():

        value[:] = []

# set the parameter dictionary to use string not float by casting the passed dictionary from pickle file


def strToFloat(params):
    """
    :param params: the parameters used by the bot to trade
    :return:
    """
    newDict = params

    for key, value in params.items():
        newDict[key] = float(value)

    return newDict

# create an accurate tradable dictionary of all the cryptos for a given time
def createVolumeDict(paramspassed, minutespassed, cryptoSymbols):
    """
    :param paramspassed: the params passed to the bot
    :param minutespassed: the current number of minutes passed in the simulation
    :param cryptoSymbols: the price symbols dictionary
    :return: the dictionary of buy volumes and sell volumes
    """
    buyVolumeDict = {}
    sellVolumeDict = {}

    #set the hours passed
    hourspassed = minutespassed % mininhour

    #set the true minutes passed
    minutespassed = minutespassed - (hourspassed * mininhour)

    #the starting hour and minute (plus the amount of time passed in the simulation)
    hour = (paramspassed['hour'] + hourspassed) % hourinday
    minute = paramspassed['min'] + minutespassed

    #if we have moved to the next day we need to set the day as the next day
    if hour != 0:
        day = paramspassed['day']
    else:
        day = nextDay(paramspassed['day'])

    delta = minute % 10
    if(delta == 0):
        for key, value in cryptoSymbols.items():
            value = value.lower()
            temp1, temp2 = readPickle(value, day, hour)
            buyVolumeDict.update(temp1)
            sellVolumeDict.update(temp2)

    # if the time difference is greater than or equal to 5 minutes round up
    if (delta >= 5):
        minute = (10 - delta) + minute
        if minute == 60: #if we have advanced to the start of the next hour
            hour = hour + 1
        for key, value in cryptoSymbols.items():
            value = value.lower()
            temp1, temp2 = readPickle(value, day, hour)
            buyVolumeDict.update(temp1)
            sellVolumeDict.update(temp2)

    # if the time difference is less than 5 subtract to nearest 10 minute interval
    elif(delta < 5):
        minute = (minute - delta)
        if minute == 0: #if we have gone back to the start of the hour nothing changes with hour
            hour = hour
        for key, value in cryptoSymbols.items():
            value = value.lower()
            temp1, temp2 = readPickle(value, day, hour)
            buyVolumeDict.update(temp1)
            sellVolumeDict.update(temp2)

    return buyVolumeDict, sellVolumeDict


# return the directory of the class this sits in

def buildDirectory(paramspassed, dirname, typedirec='storage'):
    """
    :param paramspassed: the params passed to this file
    :param dirname: the true directory that we will be looking in and storing the parameters
    :param typedirec: the directory type (training or storage)
    :return: the directory of the log and variations files
    """

    return "{}/{}/{}/{}/{}/{}/{}/{}/".format(dirname, typedirec, paramspassed['website'], paramspassed['day'], paramspassed['hour'],
                             paramspassed['min'], paramspassed['idnum'], paramspassed['classNum'])

# setup the data dictionaries

def setUpData(paramspassed, percentChanges, volumePercentChanges, volumeAmounts, cryptoSymbols):
    """
    :param paramspassed: the params passed to this function
    :param percentChanges: the dictionary of percent changes between open and close price
    :param volumePercentChanges: the dictionary of percent changes between volumes traded
    :param volumeAmounts: the dictionary of the volume amounts traded
    :param cryptoSymbols: the dictionary of crypto tickers
    :return:
    """

    for key, currency in cryptoSymbols.items():
        percentChanges.update({currency:[]})
        volumePercentChanges.update({currency:[]})
        volumeAmounts.update({currency:[]})

#setup the data dictionary so that each crypto currency has its data relevant to scoring stored
#also used to reset
def setUpScoringDataDictionary(storedData, cryptoSymbols, namesofvaluestostore, maxdataforscore):
    """
    :param storedData: the dictionary to hold all stored data for calculating a score
    :param cryptoSymbols: the dictionary of price symbols
    :param namesofvaluestostore: the names of the different values needed to calculate a score
    :param maxdataforscore: the dictionary to hold the maximum values for each datatype
    :return:
    """

    defaultvalue = 0

    #boolean to setup the max values only once
    setmaxdatavalues = False

    #loop through the dictionary of currency names
    for key, currencyname in cryptoSymbols.items():
        #create the sub dictionary for each currency
        storedData.update({currencyname: {}})
        #loop through the list of the data name types to store
        for dataname in namesofvaluestostore:
            #set the key value pair for the datatype for each currency
            storedData[currencyname].update({dataname: defaultvalue})

            #if we have not set the max data values up yet
            if setmaxdatavalues == False:
                maxdataforscore.update({dataname: 0})

        #set the value so the max data values dictionary is not updated with each pass through
        setmaxdatavalues = True


# runs through the dictionary of stored calculations for each crypto and stores the max for each
def setMaxValue(dataforscore, maxdataforscore):
    """
    :param dataforscore: the dictionary of calculations stored for each of the score attributes for the cryptos
    :param maxdataforscore: the dictionary with the maximum value calculates for all the cryptos
    :return:
    """
    #loop through each crypto and their different datatypes stored
    for currencyname, datatypedict in dataforscore.items():
        #loop through the types by their names
        for datatype, datatypevalue in datatypedict.items():

            #absolute value for the current data type for the current crypto
            absolutevaluefordatatype = abs(dataforscore[currencyname][datatype])

            #if no max value is stored for the datatype or the current stored max is less than the current
            #value stored for that crypto
            if maxdataforscore[datatype] == 0 or absolutevaluefordatatype > maxdataforscore[datatype]:

                #replace the current max value for that datatype with the stored value of the current currency
                maxdataforscore[datatype] = absolutevaluefordatatype

#runs through the dictionary of stored calculations for the combined parameters and store the max for each
def setMaxValuesCombinedParams(dataforcombinedparams, maxdataforcombinedparams):
    """
    :param dataforcombinedparams: the dictionary of calculations stored for each of the combined parameters
    :param maxdataforcombinedparams: the dictionary with the maximum value for each combined parameter type
    :return:
    """

    #just exit if there are no combined parameters to calculate
    if len(maxdataforcombinedparams) == 0:
        logging.info("No combined parameters. No max value stored")
        return

    #loop through each crypto and their different datatypes stored
    for currencyname, combinedparamdictofdata in dataforcombinedparams.items():

        #loop through each combined parameter value stored for the crypto
        for combinedparamindex in combinedparamdictofdata:

            #the absolute value of the current crypto's data value for the current combined parameter data
            absolutecryptocombinedparametervalue = abs(dataforcombinedparams[currencyname][combinedparamindex])

            #if no max value is stored for the combined param datatype or the current stored max is less than the
            #current value stored for that crypto combined param
            if maxdataforcombinedparams[combinedparamindex] == 0 or  absolutecryptocombinedparametervalue \
                 > maxdataforcombinedparams[combinedparamindex]:
                #replace the current max value for the combined param type with the stored value of the current currency
                maxdataforcombinedparams[combinedparamindex] = absolutecryptocombinedparametervalue


#setup the stored crypto calculations dictionary of lists and the corresponding dictionary with the max
#calculated values
def setupStoredCryptoCalculationsandMaxes(cryptoCalcualtionsStored, maxCalculationsStored, normalizationValuesToStore,
                                          cryptoSymbols):
    """
    :param cryptoCalcualtionsStored: the dictionary with lists for all the calculations that need to be stored for each crypto
    :param maxCalculationsStored: the dictionary containing the maximum values for each calculation
    :param normalizationValuesToStore: the list of names given to each type of calculation to be stored for
    the normalization of the individual values when deciding a score
    :param cryptoSymbols: the dictionary of crypto currency symbols
    :return:
    """
    #run through each normalization value name
    for valuename in normalizationValuesToStore:
        #loop through all the crypto types
        for key, currencyname in cryptoSymbols.items():
            #check if the currency already had a dictionary for its data made
            if currencyname not in cryptoCalcualtionsStored:
                #make a a new dictionary to hold all the data for that crypto
                cryptoCalcualtionsStored.update({currencyname: {}})

            # add a spot to store the data of this type for the current crypto
            cryptoCalcualtionsStored[currencyname].update({valuename: 0.0})
        #add a float to hold the eventually calculated maximum for value for each calculation type
        maxCalculationsStored.update({valuename: -1000.0})

#setup the stored crypto calculations dictionary of lists and the corresponding dictionary with the max calcualted values
# for each of the combined parameters

def setupStoredCalculationsForCombinedParams(storeCombinedParamsValues, storedCombinedParamsValuesMaxs, combinedparamslist,
                                             cryptoSymbols):
    """
    :param storeCombinedParamsValues: the dictionary of combined parameters calculations to store
    :param storedCombinedParamsValuesMaxs: the dictionary of the max for each combined parameter
    :param combinedparamslist: the list of lists where each sublist has parameters to combine to form a new parameter
    :param cryptoSymbols: the dictionary of price symbols
    :return:
    """

    #if there are no combined parameters just initialize the dictionaries so that no KeyErrors are thrown
    if (len(combinedparamslist) == 0):
        # loop through all the crypto types
        for key, currencyname in cryptoSymbols.items():
            # if the crypto currency name does not have a dictionary for its combined param data
            if currencyname not in storeCombinedParamsValues:
                # make a dictionary to hold the data of the current crypto
                storeCombinedParamsValues.update({currencyname: {}})


    for combinedparamindex in range(len(combinedparamslist)):
        #loop through all the crypto types
        for key, currencyname in cryptoSymbols.items():
            #if the crypto currency name does not have a dictionary for its combined param data
            if currencyname not in storeCombinedParamsValues:
                #make a dictionary to hold the data of the current crypto
                storeCombinedParamsValues.update({currencyname: {}})

            #add a spot to store the data of this type for the current crypto
            storeCombinedParamsValues[currencyname].update({combinedparamindex: 0.0})

        #add a float to hold the max value for each combined parameter calculation type
        storedCombinedParamsValuesMaxs.update({combinedparamindex: -1000.0})

#setup the ancillary peristent data dictionary to hold data that needs to carry over between resets of the normal data
#for score dictionary
def setuppersistentancillaryscoredata(persistentancillaryscoredata, ancillarydatanamelist, cryptoSymbols):
    """
    :param persistentancillaryscoredata: the data dictionary to hold any data that must be persistently stored
    :param ancillarydatanamelist: the list of names of ancillary data types to be stored
    :param cryptoSymbols: the dictionary of price symbols for the crypto currencies
    :return:
    """

    #loop thorugh the list of the names for the data types that will be persistently stored
    for ancillarydataname in ancillarydatanamelist:
        #loop through the different crypto currencies
        for key, currencyname in cryptoSymbols.items():
            #if the currency does not already have a data dictionary
            if currencyname not in persistentancillaryscoredata:
                #make a data dictionary for the current crypto currency
                persistentancillaryscoredata.update({currencyname: {}})

            #make a dictionary entry for the current data type for the current crypto
            persistentancillaryscoredata[currencyname].update({ancillarydataname: 0.0})

#returns a partioned version of the past dict of data for each type of data where
# an hour is taken out by default starting from 60 minutes in the past (if you choose an hour)
# assumes the passed data dicts have lists of data stored for each crypto (so the crypto name is the key for each list)
def getsliceofdictofdata(datadict, lastminintimeperiod=59, timeperiod=60, currency='none'):
    """
    :param datadict: the dictionary of data for each crypto
    :param lastminintimeperiod: the last minute in the time period
    :param timeperiod: the length of the time period
    :param currency: the currency we want to grab the slice for
    :return: the partitioned data dictionary with the specified slice of data
    """
    #the final dictionary of the data partitioned to only hold a time period length slice ending at the designated
    # last minute of data
    partitioneddatadict = {}

    #used to account for the fact the last minute is not counted
    minoffset = 1

    for currencyname, datalist in datadict.items():
        #store the slice of data for all the currencies if no particular one is specified
        if currency == 'none' or currencyname == currency:
            sliceofdata = datalist[lastminintimeperiod + minoffset - timeperiod:lastminintimeperiod + minoffset]

            partitioneddatadict.update({currencyname: sliceofdata})

    return partitioneddatadict

#checks if the restart codes are set off
def norestartcodessetof(errorcodes):
    """
    :param errorcodes: the class object with the error codes
    :return:
    """

    for errorflagname, errorflagvalue in defaulterrorflagsforcryptoevaluator.items():
        if 'RESTART' in errorflagname:
            actualerrorflagvalue = errorcodes.getvalueofflag(errorflagname)

            if actualerrorflagvalue == True:
                return True

    return False

def main():
    # setup the relative file path
    homedirectory = os.path.dirname(os.path.realpath(__file__))


    ##########################START OF OLD GLOBAL VARIABLES#############################################

    startMinNum = 0

    # true price for the crrpto being bought
    truePriceBought = 0.0

    # the number of buys
    numBuys = 0

    # the number of sells
    numSells = 0

    # crypto being bought and held
    currencyToTrade = {}

    # the score of each crypto
    scores = {}

    # percent Changes over all sepearted periods of time
    allOwnedCryptoPercentChanges = []

    # percent changes of the prices for each crypto with an interval size over a specified period of time
    percentChanges = {}

    # percent changes of the volume for each crypto with an interval size over a specified period of time
    volumePercentChanges = {}

    # volume data for each interval over a specified period fo time
    volumeAmounts = {}

    #dictionary to allow data to be persistently held and reused for scoring (some is copied over)
    persistentancillarydataforscore = {}

    #dictionary to hold the data used to calculate the score (non combined params type)
    dataforscore = {}

    #dict to hold the values stored to find the max and normalize for the combined parameters
    combinedparamdata = {}

    #dict to hold the values to be used for scaling the calculated combined parameters
    maxcombinedparamdata = {}

    # hold the max values to be used for scaling
    maxdataforscore = {}

    # the crypto we currently own
    ownCrypto = 'BTCUSDT'

    # number of times that the bot chooses not to buy
    totalAbstain = 0


    #the dictionary that holds the separation of each crypto currency that is implicitly made through the scoring process
    #i.e. based on the score each crypto is disgarded as an option at some point in the process of buying a new one
    cryptosSeparated = implicitcryptodivisions

    ######################END OF OLD GLOBAL VARIABLES ###########################################################

    #reads in the input, usually from the cryptotrainer
    passedparams, dirname = readTheInput(defaultcryptoevaluatorparamspassed, PARAMETERS, homedirectory)

    #get the currently stored symbols
    cryptosymbols = getStoredSymbols(passedparams['website'], homedirectory, list=False)

    #builds the directory to store logs and params
    initdirectories(passedparams, dirname, PARAMETERS, typedirec='training')

    #setup the persistent data dictionary
    setuppersistentancillaryscoredata(persistentancillarydataforscore, persistentdataforscoretypenames, cryptosymbols)

    #setup the normal data dictionaries and get an updated price symbol dictionary
    setUpData(passedparams, percentChanges, volumePercentChanges, volumeAmounts, cryptosymbols)

    #get the directory of the class
    classdirectory = buildDirectory(passedparams, dirname, typedirec='training')

    #the log directory
    logdirectory = classdirectory + 'logs/'

    #the log file name
    logfilename = '{}evaluator.log'.format(passedparams['variationNum'])

    #setup the log file in the log directory
    setUpLog(logdirectory, logfilename)

    # the file name for the parameter file
    paramfilename = '{}param.pkl'.format(passedparams['variationNum'])

    #get the parameters needed for this trading set
    params = readParamPickle(classdirectory, paramfilename)

    # set the real interval to be used for all the data
    realInterval = params['INTERVAL_TO_TEST'] + params['MIN_OFFSET']

    #store the different kinds of data for the interval
    openPriceData = CryptoStats.getOpenPrice(realInterval, params['MINUTES_IN_PAST'], {}, currencies=cryptosymbols)
    closePriceData = CryptoStats.getClosePrice(realInterval, params['MINUTES_IN_PAST'], {}, currencies=cryptosymbols)
    volumeData = CryptoStats.getVolume(realInterval, params['MINUTES_IN_PAST'], {}, currencies=cryptosymbols)
    highPriceData = CryptoStats.getHighPrice(realInterval, params['MINUTES_IN_PAST'], {}, currencies=cryptosymbols)
    lowPriceData = CryptoStats.getLowPrice(realInterval, params['MINUTES_IN_PAST'], {}, currencies=cryptosymbols)

    # initialize the minutes that will define the period
    startMinute = int(startMinNum + params['MIN_OFFSET'])
    endMinute = int(params['MAX_TIME_CYCLE'] + params['MIN_OFFSET'])
    currentMinute = int(startMinute)

    # intitialize the starting currency and the number of cycles the program has run through
    # a cycle is either a period where a crypto was held or where one was bought/sold
    currentCurrency = ''
    cycles = 0

    # initialize the percent change over the whole test and the percent change over the lifetime of owning a crypto
    params['CUMULATIVE_PERCENT_CHANGE_STORE'] = 0.0
    params['CUMULATIVE_PERCENT_CHANGE'] = 0.0

    #set the date and time at the top of the log file
    logging.info("Date and Time of Run " + str(datetime.datetime.now()) + '\n')

    #keep track of how many simulated minutes have passed
    minpassed = 0

    #the start money and end money used to re-calulate the percent change over time
    # (for checking against crypto stats analysis)
    params['START_MONEY'] = passedparams['startmoney']
    currmoney = float(params['START_MONEY'])
    endmoney = currmoney

    # price each crypto was bought at
    priceBought = openPriceData[ownCrypto][currentMinute]

    #the max time cycle in minutes used to set when a cycle will end
    minutesinacycle = params['MAX_TIME_CYCLE']

    #error code class to set flags when either the simulation must end or the current holding period must end
    errorcodes = ErrorCodes(scriptname='CryptoEvaluator')

    # runs the bot for a set number of cycles or unless the EXIT condition is met (read the function checkExitCondition)
    # cycles is either a period where a crypto is held and ones where they are bought/sold
    while(cycles < params['MAX_CYCLES'] and
          errorcodes.getvalueofflag('EXIT_MONEY_CHANGED_TOO_EXTREME_WHOLE_PERIOD') == False):


        #reset all error flags
        errorcodes.resetflags()

        logging.info("Decision {}".format(cycles))


        #used to make something run on multiples of two
        everymultipleof2 = 2
        everymultipleof4 = 4
        everymultipleof10 = 10

        # intialize the time the bot will run for
        t = 0

        # whether the bot decided not to buy or sell on this trade cycle
        numAbstain = 0

        # intialize the checkers that are set whether a buy or sell occured
        didSell = 0
        didBuy = 0

        # reset current minute to be the start minute
        currentMinute = startMinute

        #count a minute off because the minutes are 0 indexed
        minoffset = 1

        #each type of data in a dictionary running from 0 (the beginning of the past hour) to 59 (the minute before this
        # one)
        openpricedatalasthour = getsliceofdictofdata(openPriceData, lastminintimeperiod=startMinute - minoffset)
        closepricedatalasthour = getsliceofdictofdata(closePriceData, lastminintimeperiod=startMinute - minoffset)
        highpricedatalasthour = getsliceofdictofdata(highPriceData, lastminintimeperiod=startMinute - minoffset)
        lowpricedatalasthour = getsliceofdictofdata(lowPriceData, lastminintimeperiod=startMinute - minoffset)
        volumedatalasthour = getsliceofdictofdata(volumeData, lastminintimeperiod=startMinute - minoffset)

        #the first and end minute indices for an hour of minute intervals
        firstminindex = 0
        lastminindex = 59

        # run update crypto to assign scores and sort through all the cryptos and advance a 2 minutes because of how long it takes to run
        updateCrypto(firstminindex, lastminindex, ownCrypto, params, openpricedatalasthour, closepricedatalasthour, volumedatalasthour,
                     highpricedatalasthour, lowpricedatalasthour, cryptosymbols, dataforscore, combinedparamdata, cryptosSeparated,
                 persistentancillarydataforscore, maxdataforscore, percentChanges, volumeAmounts, volumePercentChanges,
                 scores, currencyToTrade, normalizationValuesToStore, maxcombinedparamdata)

        # reset the old currency to be equal to whatever the current crypto currency is
        if currentCurrency == '':
            oldCurrency = ownCrypto
        else:
            oldCurrency = currentCurrency

        # set the current currency to be whatever the price checker returns
        # can be a nothing string, the same crypto, or a new one
        currentCurrency = priceChecker(params, currencyToTrade, scores, dataforscore, combinedparamdata,
                                       cryptosSeparated)

        # sell the current crypto if you want to buy a new one
        if (oldCurrency != currentCurrency) and (currentCurrency != '') and currentCurrency != ownCrypto:

            # store the price it was sold at
            pricesold = getbinanceprice(oldCurrency, currentMinute, openPriceData[oldCurrency])

            # sell the old currency
            sellBin(oldCurrency)

            logging.info("Sold {} for {}".format(oldCurrency, pricesold))

            # if this is the first cycle we do not count the percentChange from 0 to the current price
            if cycles == 0:
                priceBought = pricesold

            # set sell checker
            didSell = 1

            # calculate and store the percent change from when the crypto was bought to when it was sold
            cumulativePercentChange = calcPercentChange(priceBought, pricesold)
            truePercentChange = calcPercentChange(truePriceBought, pricesold)

            #change the cumulative percent change by the actual money this bot is assumed to have
            #as well as by the assumed loss
            # TODO REMOVE ASSUMED LOSS IN THE REAL VERSION OF THIS FILE
            #change the end money to include the percent change of holding this crypto
            endmoney = currmoney + (currmoney * (cumulativePercentChange / percenttodecimal))

            #you loss the same percent (in theory) on each leg of a buy/sell
            buyandsell = 2

            #change the end money to include the assumed loss from the current money
            endmoney = endmoney + (endmoney * (float(passedparams['lossallowed']) / percenttodecimal)) * buyandsell

            #calculate what the real loss would be with an assumed loss and a change based in the money
            truechangewithassumedloss = calcPercentChange(currmoney, endmoney)

            params['CUMULATIVE_PERCENT_CHANGE'] = truechangewithassumedloss
            params['CUMULATIVE_PERCENT_CHANGE_STORE'] += truechangewithassumedloss

            logging.info("Made {}".format(truechangewithassumedloss))

            #set the current money to be end money
            currmoney = endmoney

            # writing to the log about when the run sold and what it bought at and what it sold at
            # as well as what was sold and how it changed
            logging.info("THIS RUN SOLD AT: {}".format(currentMinute))
            logging.info('Selling:  {} Price bought: {} Price sold: {}'.format(oldCurrency, priceBought, pricesold))
            logging.info("FINAL percent change over the life of owning this crypto {}".format(truePercentChange))

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
            priceBought, truePriceBought, ownCrypto = buyBin(currentCurrency, currentMinute,
                                                             currencyToTrade, openPriceData[currentCurrency])

            ownCrypto = currentCurrency

            logging.info("Bought {} for {}".format(currentCurrency, priceBought))
            didBuy = 1

            #more output to files about the buying
            logging.info("THIS RUN BOUGHT AT: " + str(currentMinute))


        # if you buy increment the buy counter
        if didBuy == 1:
            numBuys += 1
        if didSell == 1:
            numSells += 1

        # holding of the crypto currency for minutes less than the specied max or until one of the restart conditions is met
        # assuming there is a current currency owned
        while(t < params['MAX_TIME_CYCLE'] - minoffset and norestartcodessetof(errorcodes) is False
              and currentCurrency != ''):

            #if we are at a multiple of the minutes before we wait to check for this flag and this is not the starting
            # minute of the interval we check if we need to restart and let go of this crypto
            if(t % params['WAIT_FOR_CHECK_FAILURE'] == 0 and t != 0):
                #a slice of ten minutes of time in the past
                openpricedatalasttenmin = getsliceofdictofdata(openPriceData,
                                                               lastminintimeperiod=currentMinute - minoffset,
                                                               timeperiod=10, currency=currentCurrency)
                seterrorflag = checkFailureCondition(currentCurrency, params['NUM_TIMES_INCREASING_MIN_FAILURE_FLAG_VALUE'],
                                                openpricedatalasttenmin,
                                                params['valueaddedforapositivepercentchangeforcheckfailureflag'],
                                                params['valueaddedforazeropercentchangeforcheckoffailureflag'])
                errorcodes.setflag('RESTART_PRICE_DECREASING_TOO_OFTEN_HOLDING_PERIOD', seterrorflag)


            if(t > params['WAIT_FOR_CHECK_TOO_LOW'] and t % everymultipleof10 and t != 0):
                #a slice of the last fifteen minutes
                openpricedatalastfifteenminutes = getsliceofdictofdata(openPriceData,
                                                                       lastminintimeperiod=currentMinute - minoffset,
                                                                       timeperiod=15, currency=currentCurrency)
                seterrorflag = checkTooLow(currentCurrency,params, priceBought, openpricedatalastfifteenminutes)

                errorcodes.setflag('RESTART_PRICE_DROPPED_TOO_CLOSE_TO_ORIGINAL_HOLDING_PERIOD' ,seterrorflag)

            #if we are a a multiple of the minutes before we wait to check this flag and this is not the
            # starting minute of the interval
            if (t > params['WAIT_FOR_CHECK_TOO_NEGATIVE'] and t % everymultipleof2 and t!=0):
                #get the last two minutes of open price data
                openpricedatalasttwominutes = getsliceofdictofdata(openPriceData, lastminintimeperiod=currentMinute - minoffset,
                                                               timeperiod=2, currency=currentCurrency)

                #check the third restarting flag value to see if the crypto has gone too negative
                seterrorflag = checkTooNegative(currentCurrency, params, openpricedatalasttwominutes)

                errorcodes.setflag('RESTART_PRICE_DROPPED_TOO_MUCH_VALUE_HOLDING_PERIOD', seterrorflag)


            #if we are on a multiple of minutes and we have waited the right amount of time
            # and this is not the starting minute
            if (t > params['WAIT_FOR_CHECK_TOO_EXTREME'] and t % everymultipleof4 and t != 0):
                seterrorflag = checkPercentChangeOverHoldingTooExtreme(currentCurrency, currentMinute, params,
                                      priceBought, openPriceData)
                errorcodes.setflag('RESTART_PRICE_CHANGED_TOO_EXTREME_HOLDING_PERIOD', seterrorflag)


            # advance the time and currency minute
            t += 1
            currentMinute += 1
            minpassed += 1

        print("Time {}".format(t))
        # if you kept the same crypto as the last cycle stole the percent change you have gotten from the last cycle of holding the crypto or from when it was bought
        if(oldCurrency == currentCurrency and currentCurrency != ''):

            # get the new price bought and calculate a percent change over this interval of holding the cyrpto
            newPrice = getbinanceprice(currentCurrency, currentMinute, openPriceData[currentCurrency])
            cumulativePercentChange = calcPercentChange(priceBought, newPrice)

            # adds the percent change to the list of all the crypto currencies that have been owned over this run
            # more detail in similar code above
            lenAllOwned = len(allOwnedCryptoPercentChanges)

            if lenAllOwned == 0 or currentCurrency not in allOwnedCryptoPercentChanges[lenAllOwned - 1]:
                newDict = {currentCurrency: [cumulativePercentChange]}
                allOwnedCryptoPercentChanges.append(newDict)
            else:
                allOwnedCryptoPercentChanges[lenAllOwned - 1][currentCurrency].append(cumulativePercentChange)

            #change the end money to include the percent change of holding this crypto
            endmoney = currmoney + (currmoney * (cumulativePercentChange / percenttodecimal))

            #calculate what the real loss would be with a change based on money
            truecumulativechange = calcPercentChange(currmoney, endmoney)

            params['CUMULATIVE_PERCENT_CHANGE'] = truecumulativechange
            params['CUMULATIVE_PERCENT_CHANGE_STORE'] += truecumulativechange

            logging.info("Made {}".format(truecumulativechange))

            #reset currmoney to reflect the changes in value
            currmoney = endmoney

            # set the price bought to the new price found for the interval
            priceBought = newPrice

            logging.info("Held {} at {}".format(currentCurrency, priceBought))

        # keeps tally of the number of times we have not bought total and whether we did or did not buy now
        if oldCurrency == ownCrypto and oldCurrency != '':
            numAbstain = 1
            totalAbstain += 1

        # make a new crypto stats snapshot for analysis of the decision making process
        # startMinute is misleading here. it will be equal to the start of the next cycle not the one that we just walked through
        logging.info("CRYPTOS SEPEARTED " + str(cryptosSeparated))
        logging.info("NUM ABSTAIN "  + str(numAbstain) + '\n')
        logging.info('Did buy ' + str(didBuy) + '\n')
        logging.info('Did sell ' + str(didSell) + '\n')
        logging.info('Bought '+ str(currentCurrency) + '\n')
        logging.info('Sold ' + str(oldCurrency) + '\n')
        logging.info('Own ' + str(ownCrypto) + '\n')

        #the time we held the owned cyrpto for
        timeHeld = currentMinute - startMinute
        starttoend = endMinute - startMinute

        #advance the counter fo cryptos that have happened so
        cycles += 1

        #if this is the last cycle then we sell the current crypto and calcualte the percent change
        #checks if any buys are made because this will be entered even if no trades are made
        if cycles == params['MAX_CYCLES'] and numBuys != 0:
            # sell if there is a crypto left and increment numSells
            sellBin(ownCrypto)
            numSells += 1

            pricesold = getbinanceprice(ownCrypto, currentMinute, openPriceData[ownCrypto])

            logging.info("Sold {} for {}".format(ownCrypto, pricesold))

            # calculate and store the percent change from when the crypto was bought to when it was sold
            cumulativePercentChange = calcPercentChange(priceBought, pricesold)

            # change the cumulative percent change by the actual money this bot is assumed to have
            # as well as by the assumed loss
            # TODO REMOVE ASSUMED LOSS IN THE REAL VERSION OF THIS FILE
            # change the end money to include the percent change of holding this crypto
            endmoney = currmoney + (currmoney * (cumulativePercentChange / percenttodecimal))

            # you loss the same percent (in theory) on each leg of a buy/sell
            buyandsell = 2

            # change the end money to include the assumed loss from the current money
            endmoney = endmoney + (endmoney * (float(passedparams['lossallowed']) / percenttodecimal)) * buyandsell

            # calculate what the real loss would be with an assumed loss and a change based in the money
            truechangewithassumedloss = calcPercentChange(currmoney, endmoney)

            params['CUMULATIVE_PERCENT_CHANGE'] = truechangewithassumedloss
            params['CUMULATIVE_PERCENT_CHANGE_STORE'] += truechangewithassumedloss

            logging.info("Made {}".format(truechangewithassumedloss))

            # set the current money to be end money
            currmoney = endmoney

        # if no crypto was chosen you wait 5 minutes and start again
        elif currentCurrency == '':
            temp = startMinute
            startMinute += 5 + (currentMinute - temp)
            endMinute += 5 + (currentMinute - temp)
            minpassed += 5 + (currentMinute - temp)

        # otherwise you reset the current minute and endminute
        else:
            temp = startMinute
            startMinute += (currentMinute - temp)
            endMinute += (currentMinute - temp)
            minpassed += (currentMinute - temp)

        # check the if we must exit the simulation
        if currentCurrency != '' and currentMinute < realInterval:
            endsimulationorcontinue = checkPercentChangeOverWholePeriodExitSimulation(params)
            errorcodes.setflag('EXIT_MONEY_CHANGED_TOO_EXTREME_WHOLE_PERIOD', endsimulationorcontinue)

        #empty the dictionary of lists of the implicit divisions made between the cryptos
        resetDecisionsStored(cryptosSeparated)

        #print error flags
        errorcodes.printflags()

    #print to file the final percent changes over the run
    logging.info("Cumulative percent change over the life of all cryptos owneed so far {}"
                 .format(params['CUMULATIVE_PERCENT_CHANGE_STORE']))

    #write over the current end money
    params['END_MONEY'] = endmoney

    #print to the log the start and end money
    logging.info("Started with {}".format(params['START_MONEY']))
    print("Started with {}".format(params['START_MONEY']))
    logging.info("Ended with {}".format(params['END_MONEY']))
    print("Ended with {}".format(params['END_MONEY']))

    print("Params used {}".format(params))

    #set the number of cycles of buying and selling to whichever was lower, the number of times buying or selling
    if numBuys > numSells:
        params['CYCLES'] = numSells
    else:
        params['CYCLES'] = numBuys

    #write back to the param pickle file
    writeParamPickle(params, classdirectory, '{}param.pkl'.format(passedparams['variationNum']))


if __name__ == "__main__":
    main()
