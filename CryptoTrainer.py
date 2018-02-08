# Copyright (c) 2018 A&D
# Auto trading tester that runs multiple versions of the trader with different parameters

#todo add a function to randomize the parameters when requested
#todo update the best parameters text file
#todo make the randomize parameters function implement the different types of randomization

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
#CUMULATIVE_PRICE_MODIFIER: the cumulative price change modifier for the weighted moving average
#PRIMARY_MODIFIED_VOLUME_SCALER: the scaler to make more volume traded have the same sign as the percent change in the price than the amount that is counted as having the opposite sign
#WAIT_FOR_CHECK_FAILURE: the number of ticks before the failure condition is checked (the crypto is decreasing over the past 10 minutes)
#WAIT_FOR_CHECK_TOO_LOW: the number of ticks before ethe program checks to see if a crypto has decreased too low to its starting point

PARAMETERS = {'PERCENT_TO_SPEND': 1, 'MINIMUM_PERCENT_INCREASE': 5.0, 'MINIMUM_SCORE': 1.0, 'MINIMUM_MOVING_AVERAGE': .6, 'MAX_DECREASE': -10, 'MAX_TIME_CYCLE': 3600, 'MAX_CYCLES': 24, 'MAX_PERCENT_CHANGE': 15
, 'NEGATIVE_WEIGHT': 1.5, 'CUMULATIVE_PERCENT_CHANGE_STORE': 0.0, 'SLOT_WEIGHT': 1, 'TIME_INCREASING_MODIFIER': 10, 'VOLUME_INCREASING_MODIFIER': .01, 'PERCENT_BY_HOUR_MODIFIER': 1,
'VOLUME_INCREASING_MODIFIER': .01, 'PERCENT_BY_HOUR_MODIFIER': 1, 'VOLUME_PERCENT_BY_HOUR_MODIFIER': .1, 'FLOOR_PRICE_MODIFIER': 1.005, 'CUMULATIVE_PRICE_MODIFIER': 100, 'PRIMARY_MODIFIED_VOLUME_SCALER': 2, 'WAIT_FOR_CHECK_FAILURE': 300, 'WAIT_FOR_CHECK_TOO_LOW': 600}

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
NUM_ITERATIONS = 5


#Directory path (r makes this a raw string so the backslashes do not cause a compiler issue
#paramPaths = r'C:\Users\katso\Documents\GitHub\Crypto'
drewparamPaths = r'C:\Users\DrewG\Documents\GitHub\Crypto'

#param file name + path
#paramCompletePath = os.path.join(paramPaths, "BEST_PARAMETERS.txt")
drewparamCompletePath = os.path.join(drewparamPaths, "BEST_PARAMETERS.TXT")
#open a file for appending (a). + creates file if does not exist
file = open(drewparamCompletePath, "r")




#randomizes the parameters before sending them to a subprocess
#typeOfRandom determines what kinds of randomization occurs
#type 0 means normal, type 1 means larger range of randomization
#type 3 means none
def randomizeParams(paramDict, typeOfRandom):

    if(typeOfRandom == 3):
        return 0
    if (typeOfRandom == 0):
        print('')
        #todo add a normal kind of randomization
    if(typeOfRandom == 1):
        print('')
        #todo add a special kind of randomization

    numTest = paramDict['MINIMUM_PERCENT_INCREASE']
    numTest *= random.randrange(1, 100)

    paramDict['MINIMUM_PERCENT_INCREASE'] = numTest

#function just resets parameters to the defaults
def resetParameters(paramDict):
    valList = []
    count = 0
    file.seek(0)


    for line in file:
        val = line.split(': ')[1]
        trueVal = val.split(',')[0]
        trueVal = float(trueVal)
        valList.append(trueVal)

    for key, value in paramDict.items():

        paramDict[key] = valList[count]
        count+=1

def main():
    global NUM_ITERATIONS
    global file


    typeOfRandom = 0
    count = 0



    #CODE TO RUN MULTIPLE INSTANCES OF BOT
    procs = []


    current_Max = 0.0
    for i in range(NUM_ITERATIONS):


        proc = Popen([sys.executable, 'tester.py', '{}in.txt'.format(i), '{}out.txt'.format(i)], stdout=PIPE, stdin = PIPE, stderr=PIPE,bufsize=1, universal_newlines=True)
        procs.append(proc)

    for proc in procs:

        randomizeParams(PARAMETERS, typeOfRandom)

        print('Changed {}'.format(PARAMETERS['MINIMUM_PERCENT_INCREASE']))
        if(count % 50 == 0):
            typeOfRandom == 1
        else:
            typeOfRandom == 0

        out = proc.communicate(input = str(PARAMETERS))

        count+=1
        #walks through the output from the instance of tester and strips it of the parameters used
        #then stores the parameters if they netted a larger % change than the previous max
        for line in out:
            val = line

            if(val == ''):
                break
            substring = val.split("\'CUMULATIVE_PERCENT_CHANGE_STORE\':", 1)[1]



            cumulativePerentChangeStore = substring.split(',', 1)[0]
            cumulativePerentChangeStore = float(cumulativePerentChangeStore)


            if cumulativePerentChangeStore >= current_Max:
                current_Max = cumulativePerentChangeStore
                stored_output = line
        resetParameters(PARAMETERS)
    print('{}'.format(stored_output))
    print('{}'.format(current_Max))

    proc.wait()


if __name__ == "__main__":
    main()