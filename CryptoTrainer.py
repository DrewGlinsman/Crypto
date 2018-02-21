# Copyright (c) 2018 A&D
# Auto trading tester that runs multiple versions of the trader with different parameters

#todo add a function to randomize the parameters when requested
#todo update the best parameters text file
#todo make the randomize parameters function implement the different types of randomization
#todo make it so that every test having extremely negative output does not still overwrite best parameters

import sys
import random
import requests
import hmac
import hashlib
import time
import math
import datetime
import re
import os
from subprocess import Popen, PIPE, run
from PrivateData import api_key, secret_key

#weird errors removed

# EXPLANATION OF THE PARAMETERS

#PERCENT_QUANTITY_TO_SPEND: the amount of the balance calculated to be spent that we can spend (based on the small fee) #todo look more at why this exists
#PERCENT_TO_SPEND: the amount of the balance of bitcoin to spend. Should be calculated by how many bots are made
#MINIMUM_PERCENT_INCREASE: lowest percent increase for a cryptocurrency to be considered in the start of the bot
#MINIMUM_SCORE: the lowest score for a crypto to be addded to the list of scores to be checked for the remaineder of a run
#MINIMUM_MOVING_AVERAGE: the lowest moving average for a crypto score to be considered
#MAX_DECREASE: the maximum allowed decrease over a short (<15m) interval
#MAX_TIME_CYCLE: the maximum time the bot will run for in ticks (they are counted by a incrementing variable)
#MAX_CYCLES: the maximum amount of times the bot will buy and sell
#MAX_PERCENT_CHANGE: the highest % increase and the lowest % decrease a crypto can have over the life of owning it before an auto reevaluation
#NEGATIVE_WEIGHT: weight applied to negative percent price or percent volume change
#CUMULATIVE_PERCENT_CHANGE: the cumulative % change of a crypto's price over the course of owning it
#CUMULATIVE_PERCENT_CHANGE_STORE: the cumulative percent change over the course of owning several cryptos
#SLOT_WEIGHT: weight applied to each slot of the intervals being checked to see if they the crypto was increasing or decreasing
#TIME_INCREASING_MODIFIER: the unweighted time increasing modifier (time increasing is the count of intervals where the price was increasing)
#VOLUME_INCREASING_MODIFIER: the volume increasing modifier (volume increasing is the count of intervals where the volume traded increased)
#PERCENT_BY_HOUR_MODIFIER: the modifier for the total percent change of a crypto over a longer interval (> 1hr)
#VOLUME_PERCENT_BY_HOUR_MODIFIER: the modifier for the volume percent change over a longer interval (> 1hr)
#FLOOR_PRICE_MODIFIER: the lowest % change above the original price the crypto was bought at before the bot auto sells it (calculated later than the other failure conditions to catch a decreasing price)
#MODIFIED_VOLUME_MODIFIER: the cumulative volume change based on the % change by interval scale
#CUMULATIVE_PRICE_MODIFIER: the cumulative price change modifier for the weighted moving average
#PRIMARY_MODIFIED_VOLUME_SCALER: the scaler to make more volume traded have the same sign as the percent change in the price than the amount that is counted as having the opposite sign
#WAIT_FOR_CHECK_FAILURE: the number of ticks before the failure condition is checked (the crypto is decreasing over the past 10 minutes)
#WAIT_FOR_CHECK_TOO_LOW: the number of ticks before ethe program checks to see if a crypto has decreased too low to its starting point


PARAMETERS = {'PERCENT_QUANTITY_TO_SPEND': .9, 'PERCENT_TO_SPEND': 1.0, 'MINIMUM_PERCENT_INCREASE': 5.0, 'MINIMUM_SCORE': 0.01, 'MINIMUM_MOVING_AVERAGE': .001, 'MAX_DECREASE': -10.0, 'MAX_TIME_CYCLE': 60.0, 'MAX_CYCLES': 24, 'MAX_PERCENT_CHANGE': 15.0, 'NEGATIVE_WEIGHT': 1.0, 'CUMULATIVE_PERCENT_CHANGE': 0.0, 'CUMULATIVE_PERCENT_CHANGE_STORE': 0.0, 'SLOT_WEIGHT': 1.0, 'TIME_INCREASING_MODIFIER': 1.0, 'VOLUME_INCREASING_MODIFIER': 1.0, 'PERCENT_BY_HOUR_MODIFIER': 1.0, 'VOLUME_PERCENT_BY_HOUR_MODIFIER': 1.0, 'FLOOR_PRICE_MODIFIER': 1.005, 'MODIFIED_VOLUME_MODIFIER': 1.0, 'CUMULATIVE_PRICE_MODIFIER': 1.0, 'PRIMARY_MODIFIED_VOLUME_SCALER': 1.0, 'WAIT_FOR_CHECK_FAILURE': 5.0, 'WAIT_FOR_CHECK_TOO_LOW': 10.0}

UNCHANGED_PARAMS = ['PERCENT_QUANTITY_TO_SPEND', 'PERCENT_TO_SPEND', 'MAX_TIME_CYCLE', 'MAX_CYCLES', 'CUMULATIVE_PERCENT_CHANGE', 'CUMULATIVE_PERCENT_CHANGE_STORE', 'WAIT_FOR_CHECK_FAILURE', 'WAIT_FOR_CHECK_TOO_LOW']


priceSymbols = {'bitcoin': 'BTCUSDT', 'ripple': "XRPBTC",
                'ethereum': 'ETHBTC', 'BCC': 'BCCBTC',
                'LTC': 'LTCBTC', 'Dash': 'DASHBTC',
                'Monero': 'XMRBTC', 'Qtum': 'QTUMBTC', 'ETC': 'ETCBTC',
                'Zcash': 'ZECBTC', 'ADA': 'ADABTC', 'ADX': 'ADXBTC', 'AION' : 'AIONBTC', 'AMB': 'AMBBTC', 'APPC': 'APPCBTC', 'ARK': 'ARKBTC', 'ARN': 'ARNBTC', 'AST': 'ASTBTC', 'BAT': 'BATBTC', 'BCD': 'BCDBTC', 'BCPT': 'BCPTBTC', 'BNB': 'BNBBTC', 'BNT': 'BNTBTC', 'BQX': 'BQXBTC', 'BRD': 'BRDBTC', 'BTS': 'BTSBTC', 'CDT': 'CDTBTC', 'CMT': 'CMTBTC', 'CND': 'CNDBTC', 'CTR':'CTRBTC', 'DGD': 'DGDBTC', 'DLT': 'DLTBTC', 'DNT': 'DNTBTC', 'EDO': 'EDOBTC', 'ELF': 'ELFBTC', 'ENG': 'ENGBTC', 'ENJ': 'ENJBTC', 'EOS': 'EOSBTC', 'EVX': 'EVXBTC', 'FUEL': 'FUELBTC', 'FUN': 'FUNBTC', 'GAS': 'GASBTC', 'GTO': 'GTOBTC', 'GVT': 'GVTBTC', 'GXS': 'GXSBTC', 'HSR': 'HSRBTC', 'ICN': 'ICNBTC', 'ICX': 'ICXBTC', 'IOTA': "IOTABTC", 'KMD': 'KMDBTC', 'KNC': 'KNCBTC', 'LEND': 'LENDBTC', 'LINK':'LINKBTC', 'LRC':'LRCBTC', 'LSK':'LSKBTC', 'LUN': 'LUNBTC', 'MANA': 'MANABTC', 'MCO': 'MCOBTC', 'MDA': 'MDABTC', 'MOD': 'MODBTC', 'MTH': 'MTHBTC', 'MTL': 'MTLBTC', 'NAV': 'NAVBTC', 'NEBL': 'NEBLBTC', 'NEO': 'NEOBTC', 'NULS': 'NULSBTC', 'OAX': 'OAXBTC', 'OMG': 'OMGBTC', 'OST': 'OSTBTC', 'POE': 'POEBTC', 'POWR': 'POWRBTC', 'PPT': 'PPTBTC', 'QSP': 'QSPBTC', 'RCN': 'RCNBTC', 'RDN': 'RDNBTC', 'REQ': 'REQBTC', 'SALT': 'SALTBTC', 'SNGLS': 'SNGLSBTC', 'SNM': 'SNMBTC', 'SNT': 'SNTBTC', 'STORJ': 'STORJBTC', 'STRAT': 'STRATBTC', 'SUB': 'SUBBTC', 'TNB': 'TNBBTC', 'TNT': 'TNTBTC', 'TRIG': 'TRIGBTC', 'TRX': 'TRXBTC', 'VEN': 'VENBTC', 'VIB': 'VIBBTC', 'VIBE': 'VIBEBTC', 'WABI': 'WABIBTC', 'WAVES': 'WAVESBTC', 'WINGS': 'WINGSBTC', 'WTC': 'WTCBTC', 'XVG': 'XVGBTC', 'XZC': 'XZCBTC', 'YOYO': 'YOYOBTC', 'ZRX': 'ZRXBTC'}


#will hold the specific parameter given to each list
PARAM_CHOSEN = {}



#will hold the specific parameter given to each list
PARAM_CHOSEN = {}


#list of each variation of the parameter list, one is passed to each instance of the bot
PARAMETER_VARIATIONS=[]

#number of iterations of bot
NUM_ITERATIONS = 50

#number of classes of bots to run
NUM_CLASSES = 5


#final dictionary returned to be rewritten to file
final_Dict = {}

#Directory path (r makes this a raw string so the backslashes do not cause a compiler issue
paramPaths = r'C:\Users\katso\Documents\GitHub\Crypto'
#paramPaths = r'C:\Users\DrewG\Documents\GitHub\Crypto'


#param file name + path

#todo change to "BEST_PARAMETERS" when actually running
paramCompletePath = os.path.join(paramPaths, "TEST_PARAMETERS.txt")


#open a file for appending (a). + creates file if does not exist
file = open(paramCompletePath, "r+")

def keyCheck(key):
    for i in UNCHANGED_PARAMS:
        if i == key:
            return 1

    return 0

#randomizes the parameters before sending them to a subprocess
#typeOfRandom determines what kinds of randomization occurs
#type 0 means normal, type 1 means larger range of randomization
#type 3 means none
#TODO remember after to testing not to randomize stuff like cumulative percent change store (i.e data)
def randomizeParams(paramDict, typeOfRandom):
    #default range size and stepSize
    range = 1.0
    randVal = 0.0
    if(typeOfRandom == 3):
        return 0
    if (typeOfRandom == 0):
        for key, value in paramDict.items():

            if(keyCheck(key) != 1):
                randVal = paramDict[key]
                randVal += random.uniform(-1,1) * range
                paramDict[key] = randVal


    #todo add a normal kind of randomization
    if(typeOfRandom == 1):
        range = 100.0
        for key, value in paramDict.items():
            if(keyCheck(key) != 1):
                randVal = paramDict[key]
                randVal += random.uniform(-1,1) * range
                paramDict[key] = randVal

    #todo add a special kind of randomization


#function just resets parameters to the defaults
def resetParameters(paramDict):
    valList = []
    count = 0

    file.seek(0)

    #loop over the file and split the lines by space and , meaning you only get the value
    for line in file:
        val = line.split(' ')[1]
        trueVal = val.split(',')[0]
        trueVal = float(trueVal)
        valList.append(trueVal)


    #parameter dictionary that will loop over params and rewrite them
    for key, value in paramDict.items():

        paramDict[key] = valList[count]
        count+=1


#write paramDict to a file that will be read from to reset parameters at the start of each test and after each randomization
def reWriteParameters(paramDict):

    file.seek(0)

    for key, value in paramDict.items():
        #if we are at the very last parameter do not print a new line
        if key == 'WAIT_FOR_CHECK_TOO_LOW':
            print('\'%s\': %s,' % (key, value))
            file.write('\'%s\': %s,' % (key, value))

        if key != 'WAIT_FOR_CHECK_TOO_LOW':
            print('\'%s\': %s,\n' % (key, value))
            file.write('\'%s\': %s,\n' % (key, value))

#converts the given string to a Dict. Used to parse the returned string from the bots being trained
def stringToDict(stringToChange):
    newDict = {}
    stringKeySplit = ''
    stringValSplit = ''
    counter = 0

    #split the passed string into a list seperated by spaces
    listSplits = stringToChange.split(' ')

    #loops through each string seperated out into listSplits
    for i in listSplits:
        #if the string is from an even position split it into a future key
        if (counter % 2 == 0):
            stringKeySplit = i.split('\'')[1]
        #if the string is from an odd position split it to be a future value and update newDict to contain it
        if (counter % 2 != 0):
            if ("," in i):
                stringValSplit = i.split(',')[0]
            if("}" in i ):
                stringValSplit = i.split('}')[0]
            newDict.update({stringKeySplit: stringValSplit})



        counter+=1

    return newDict

#makes the string line exclusively consist of the correct string of parameters
def reformatLine(line):


   firstFormat = line.split('LINEBEGIN')[1]
   reformat = firstFormat.split('DONEEND')[0]

   return reformat


def main():
    global NUM_ITERATIONS
    global PARAMETERS
    global file
    global final_Dict
    global reform




    #store the multiple processes


    for i in range(NUM_CLASSES):
        typeOfRandom = 3
        current_Max = 0.0
        procs = []
        count = 0

        #creates NUM_ITERATIONS amounts of bots
        for i in range(NUM_ITERATIONS):


            proc = Popen([sys.executable, 'CryptoEvaluator.py', '{}in.txt'.format(i), '{}out.txt'.format(i)], stdout=PIPE, stdin = PIPE, stderr=PIPE, bufsize=1, universal_newlines=True)
            procs.append(proc)

        #randomizes parameters and runs different instances of the bot using the different starting parameters
        for proc in procs:
            reform = ''


            randomizeParams(PARAMETERS, typeOfRandom)

            #reset typeOfRandom so that every 50th run we use a special set of randomizers
            if(count % 50 == 0):
                typeOfRandom = 1
            if(count % 50 != 0):
                typeOfRandom = 0


            #passing the parameters to the processes
            out = proc.communicate(input = str(PARAMETERS))
            timestamp = int(time.time() * 1000)
            print(str(timestamp))
            print(out)
            #walks through the output from the instance of tester and strips it of the parameters used
            #then stores the parameters if they netted a larger % change than the previous max
            for line in out:
                print(line)
                #to avoid parsing a line that does not contain this special word indicator
                if "LINEBEGIN" not in line:
                    break
                val = line


                if(val == ''):
                    break
                reform = reformatLine(val)

                substring = reform.split("\'CUMULATIVE_PERCENT_CHANGE_STORE\':", 1)[1]

                cumulativePerentChangeStore = substring.split(',', 1)[0]

                print("THIS" + str(cumulativePerentChangeStore))
                cumulativePerentChangeStore = float(cumulativePerentChangeStore)

                print(str(cumulativePerentChangeStore))

                #if the cumulative Percent Stored is greater than the current Max store it and the line of parsed input that it was from
                if cumulativePerentChangeStore >= current_Max or count == 0:
                    current_Max = cumulativePerentChangeStore
                    stored_output = reform
                count += 1
            #reset the parameters dictionary to the original "best" one from the file
            resetParameters(PARAMETERS)

        #convert the stored, parsed string into a dictionary
        final_Dict = stringToDict(stored_output)

        print('Stored : {}'.format(stored_output))
        print('Current Max: {}'.format(current_Max))



        #rewrite the parameter file with the final Dict
        reWriteParameters(final_Dict)
        for i in procs:
            i.wait()


    file.close()
if __name__ == "__main__":
    main()