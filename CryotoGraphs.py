# Copyright (c) 2018 A&D
# Creates graphs for the passed intervals of data

import pandas
import pickle
import CryptoStats

from CryptoTrainer import priceSymbols

#dictionary of parameters
PARAMETERS = {}

#the final part of the directory base
addOnPath = 'Crypto\\'

#reads pickle from a file
def readParamPickle(path):
    logPaths = r'C:\Users\katso\Documents\GitHub\\' + path
    pickle_in = open(logPaths + '\\' + "param.pkl", "rb")
    testDict = pickle.load(pickle_in)

    return testDict

#builds a graph for each crypto using the specified kind of data
def plotData(stats):
    print('placeholder')

def main():
    #setting up the dictionary of parameters and the interval used to grab data
    PARAMETERS = readParamPickle(addOnPath)
    realInterval = PARAMETERS['INTERVAL_TO_TEST'] + PARAMETERS['MIN_OFFSET']


    #initializing all the different kinds of data
    openPriceData = CryptoStats.getOpenPrice(realInterval , PARAMETERS['MINUTES_IN_PAST'])
    closePriceData = CryptoStats.getClosePrice(realInterval, PARAMETERS['MINUTES_IN_PAST'])
    volumeData = CryptoStats.getVolume(realInterval, PARAMETERS['MINUTES_IN_PAST'])
    highPriceData = CryptoStats.getHighPrice(realInterval, PARAMETERS['MINUTES_IN_PAST'])
    lowPriceData = CryptoStats.getLowPrice(realInterval, PARAMETERS['MINUTES_IN_PAST'])

if __name__ == "__main__":
    main()
