# Copyright (c) 2018 A&D
# Class to store decisions from each bot and then evaluate those decisions

import os
import datetime
import pathlib



from AutoTrader import priceSymbols

class CryptoStatsAnalysis:


    #place data attributes in here that you do not want stored by different instances of the bot
    #or redefine them using the parameter list passed
    def __init__(self, variationNum, classNum,  training, startMinute, endMinute, PARAMS):

        ###### SETTING PATHS FOR SAVING ANALYSIS IN FILES #######
        #used in opening the appropriate file for this
        self.variationNum = variationNum
        self.classNum = classNum

        #training = T will make the analysis files get stored with the other training
        #training = NT will make the analysis files get stored with the normal trading
        self.training = training

        # Directory path (r makes this a raw string so the backslashes do not cause a compiler issue
        logPaths = r'C:\Users\katso\Documents\GitHub\Crypto\Analysis'

        #concatenates the logpath with a date so each analysis log set is in its own file by day
        withDate = logPaths + '\\' + str(datetime.datetime.now().date())

        #concatenates the logpath with a autotrader vs crypto evalutor distinction
        withTraining = withDate + '\\' + training

        #creates a directory if one does not exist
        pathlib.Path(withTraining).mkdir(parents=True, exist_ok=True)

        #file name concatentation with runNum
        fileName = "__" + str(classNum) + ':' + str(variationNum) + "_Analysis.txt"

        # log file name + path
        logCompletePath = os.path.join(withTraining, fileName)

        # open a file for appending (a). + creates file if does not exist
        file = open(logCompletePath, "a+")

        #Storage Variables: variables used for storing different attributes for the cryptos from each successive buy/sell period

        # Each successive iteration uses a different dictionary, each dictionary has a timestamp and a list of crypto objects with their stored data,should also include buy and sell times
        self.runStats = []

        #the parameters the bot used
        self.params = PARAMS

        #overall interval the bot trained on
        self.startMinute = startMinute
        self.endMinute = endMinute


        #FINAL VARIABLES: anything used for final evaluation
        #dictionary where every crypto chosen to be bought is stored and whether they increased or decreased
        self.finalChosen = {}

        #dictionary where every crypto that qualified for potentially buying is stored and whether they increased or decreased
        self.narrowedDown = {}

        #the list of correlations between the score order and percent change for each buy
        self.correlations = []

        #the average correlation between the score order and the percent change
        self.averageCorrelation = []

    #adds a dictionary where every crypto has a special holder object assigned to it with all important information to it from that moment when the dictionary was made
    # this method is called each time a crypto has been bought, as well as when the cryptos decide to keep the same crypto currency, and when they choose not to buy one
    def newStats(self, statsDict, minute, didBuy, didSell, bought, sold):
        self.runStats.append(self.newCryptoDict(minute, statsDict, didBuy, didSell, bought, sold))


    #returns a dictionary with one holder object for each crypto as well as a  stored currentMinute
    def newCryptoDict(self, timestamp, statsDict, didBuy, didSell, bought, sold):
        newDict = {}
        for key, value in priceSymbols.items():
            newDict.update({value: CryptoHolder(value)})
        newDict.update({'currentMinute': timestamp})
        newDict.update({'statsDict': statsDict})
        newDict.update({'didBuy': didBuy})
        newDict.update({'didSell': didSell})
        newDict.update({'bought': bought})
        newDict.update({'sold': sold})


        return newDict

class CryptoHolder():

    #decision can be B for bought, C for chosen, or NC for not chosen
    def __init__(self, cryptoName):
        self.symbol = cryptoName
        self.score = 0.0
        self.mean = 0.0
        self.decision = 'NC'
