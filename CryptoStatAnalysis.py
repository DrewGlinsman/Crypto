# Copyright (c) 2018 A&D
# Class to store decisions from each bot and then evaluate those decisions

import os
import datetime


class CryptoStatsAnalysis:


    #place data attributes in here that you do not want stored by different instances of the bot
    #or redefine them using the parameter list passed
    def __init__(self, run, training):

        ###### SETTING PATHS FOR SAVING ANALYSIS IN FILES #######
        #used in opening the appropriate file for this
        runNum = run

        #training = T will make the analysis files get stored with the other training
        #training = NT will make the analysis files get stored with the normal trading
        training = training

        # Directory path (r makes this a raw string so the backslashes do not cause a compiler issue
        logPaths = r'C:\Users\katso\Documents\GitHub\Crypto\Analysis'

        #concatenates the logpath with a date so each analysis log set is in its own file by day
        withDate = logPaths + '\\' + str(datetime.datetime.now().date())

        #concatenates the logpath with a autotrader vs crypto evalutor distinction
        withTraining = withDate + '\\' + training

        #file name concatentation with runNum
        fileName = "__" + str(runNum) + "_Analysis.txt"

        # log file name + path
        logCompletePath = os.path.join(logPaths, fileName)

        # open a file for appending (a). + creates file if does not exist
        file = open(logCompletePath, "a+")
