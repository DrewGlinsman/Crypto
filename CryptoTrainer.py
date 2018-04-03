# Copyright (c) 2018 A&D
# Auto trading tester that runs multiple versions of the trader with different parameters

#todo add a function to randomize the parameters when requested
#todo update the best parameters text file
#todo make the randomize parameters function implement the different types of randomization
#todo make it so that every test having extremely negative output does not still overwrite best parameters
#todo add in on/off switches and make them do different things for different parameters (i.e. something like negative weight should get treated like a 1.0 not a 0.0 since it is used in necessary calculations)
#todo add in different negative weights depending on which is used.
#todo add command line functionality so that you can input num_classes and num_iterations manually when running from command line

import sys
import random
import time
import datetime
import os
import pathlib
import pickle

from Websockets import generatePriceSymbols
import calendar

from subprocess import Popen, PIPE
from PrivateData import api_key, secret_key

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
#VARIATION_NUM: number stored for what variation on the bot this is, 0 base
#CLASS_NUM: number stored for the class, 0 means no class, 1 and up are the actual classes
#INTERVAL_TO_TEST: the interval over which the bot will be tested (think hour, day, week etc...); used with the crypto evaluator
#MINUTES_IN_PAST: how far back you want the end point of the test to be

PARAMETERS = {'PERCENT_QUANTITY_TO_SPEND': .9, 'PERCENT_TO_SPEND': 1.0, 'MINIMUM_PERCENT_INCREASE': 5.0, 'MINIMUM_SCORE': 0.01, 'MINIMUM_MOVING_AVERAGE': .001, 'MAX_DECREASE': -10.0, 'MAX_TIME_CYCLE': 60.0, 'MAX_CYCLES': 24.0, 'MAX_PERCENT_CHANGE': 15.0, 'NEGATIVE_WEIGHT': 1.0, 'CUMULATIVE_PERCENT_CHANGE': 0.0, 'CUMULATIVE_PERCENT_CHANGE_STORE': 0.0, 'SLOT_WEIGHT': 1.0, 'TIME_INCREASING_MODIFIER': 1.0, 'VOLUME_INCREASING_MODIFIER': 1.0, 'PERCENT_BY_HOUR_MODIFIER': 1.0, 'VOLUME_PERCENT_BY_HOUR_MODIFIER': 1.0, 'FLOOR_PRICE_MODIFIER': 1.005, 'MODIFIED_VOLUME_MODIFIER': 1.0, 'CUMULATIVE_PRICE_MODIFIER': 1.0, 'PRIMARY_MODIFIED_VOLUME_SCALER': 1.0, 'WAIT_FOR_CHECK_FAILURE': 5.0, 'WAIT_FOR_CHECK_TOO_LOW': 10.0, 'VARIATION_NUMBER': 0.0, 'CLASS_NUM': 0.0, 'INTERVAL_TO_TEST': 1440.0, 'MINUTES_IN_PAST': 0.0}


UNCHANGED_PARAMS = ['PERCENT_QUANTITY_TO_SPEND', 'PERCENT_TO_SPEND', 'MAX_TIME_CYCLE', 'MAX_CYCLES', 'CUMULATIVE_PERCENT_CHANGE', 'CUMULATIVE_PERCENT_CHANGE_STORE', 'WAIT_FOR_CHECK_FAILURE', 'WAIT_FOR_CHECK_TOO_LOW', 'VARIATION_NUMBER', 'CLASS_NUM', 'INTERVAL_TO_TEST', 'MINUTES_IN_PAST']


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
PARAMETER_VARIATIONS = []

#number of iterations of bot
NUM_ITERATIONS = 4

#number of classes of bots to run
NUM_CLASSES = 300

#number of minutes in a day
minInDay = 1440


#final dictionary returned to be rewritten to file
final_Dict = {}

#Directory path (r makes this a raw string so the backslashes do not cause a compiler issue
#paramPaths = r'C:\Users\katso\Documents\GitHub\Crypto'
paramPaths = r'C:\Users\DrewG\Documents\GitHub\Crypto'


#param file name + path

#todo change to "BEST_PARAMETERS" when actually running
paramCompletePath = os.path.join(paramPaths, "TEST_PARAMETERS.txt")

#open a file for appending (a). + creates file if does not exist
file = open(paramCompletePath, "r+")

#the timestamp for the run
runTime = 0

#dictionaires for the modes this can be run in
modes = {'SoloEvaluator': {'string': 'SoloEvaluator', 'value': 0}, 'SoloTrainer': {'string': 'SoloTrainer', 'value': 1}, 'MultiTrainer': {'string': 'MultiTrainer', 'value': 2}}

#what is running this evaluator
running = modes['SoloTrainer']['string']

#the mode number
mode = modes['SoloTrainer']['value']

#a dictionary with attributes passed back from an evaluator
attributeDict = {}

#makes a log file for this instance of the trainer that is sorted into a folder by the date it was run
# and its name is just its timestamp
def buildLogs():
    global file2
    global runTime
    global running



    # Directory path (r makes this a raw string so the backslashes do not cause a compiler issue

    #logPaths = r'C:\Users\katso\Documents\GitHub\Crypto\Logs'
    logPaths = r'C:\Users\DrewG\Documents\Github\Crypto\Logs'

    #concatenates with the mode this is running in (solo, training in a class with other variations)
    withMode = logPaths + '\\Mode-' + running

    #datetime object that holds the date
    date =  datetime.date.today()
    day = date.day
    month = date.month
    year = date.year


    # concatenates the logpath with a date so each analysis log set is in its own file by day
    withDate = withMode + '\\Year-' + str(year) + '\\Month-' + str(calendar.month_name[month] + '\\Day-' + str(day))

    withRunTime = withDate + '\\RunTime-' + str(runTime)

    #the label for the trainer so that it gets its own folder
    withTrainer = withRunTime + '\\Trainer'

    # creates a directory if one does not exist
    pathlib.Path(withTrainer).mkdir(parents=True, exist_ok=True)

    # file name concatentation with runNum
    fileName = 'RunTime='  + str(runTime) + "_Trainer.txt"

    print("RUN " + str(runTime))

    # log file name + path
    logCompletePath = os.path.join(withTrainer, fileName)

    # open a file for appending (a). + creates file if does not exist
    file2 = open(logCompletePath, "a+")


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
    foundLast = 0
    line = 0

    lenParam = len(paramDict)
    file2.write("PARAMETER DICTIONARY " + str(paramDict))
    file2.write("LENGTH OF PARAMETER DICT " + str(lenParam))
    count = 1
    for key, value in paramDict.items():
        if count == lenParam:
            lastParam = key
        count+=1

    file2.write("LAST PARAM " + str(lastParam))

    for key, value in paramDict.items():
        #if we are at the very last parameter do not print a new line
        if key == lastParam:
            foundLast = 1
            #print('\'%s\': %s,' % (key, value))
            file.write('\'%s\': %s,' % (key, value))
            file2.write('HEY LOOK AT THIS \'%s\': %s,' % (key, value))

        if key != lastParam and foundLast == 0:
            #print('\'%s\': %s,\n' % (key, value))
            file.write('\'%s\': %s,\n' % (key, value))
            file2.write('HEY LOOK HERE \'%s\': %s,' % (key, value))


    file.seek(0)
    for i in file:
        #print('LINE '+ str(line) + ' : ' + str(i))
        line += 1

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

#if there is input on the command line it will assign the NUM_CLASSES and NUM_ITERATIONS based on the flags passed
# the flag -cl5 will set the classes to 5. the flag -it6 will set the iterations to 6
def setVals():

    global NUM_CLASSES
    global NUM_ITERATIONS

    argv_len = len(sys.argv)
    stringargs = str(sys.argv)
    stringarglist = stringargs.split()

    #if there is more than one arguement (the py file name) than it will loop for the flags in the string
    # of arguments passed, then it splits the string up based on the flags if found
    # flags must be seperated by whitespaces
    if argv_len > 1:
        if '-c1' in stringargs:
            for i in stringarglist:
                if '-cl' in i:
                    NUM_CLASSES = int(i.split('-c1', 1)[1])
        if '-it' in stringargs:
            for j in stringarglist:
                if '-it' in j:
                    NUM_ITERATIONS = int(j.split('-it', 1)[1])




#makes the string line exclusively consist of the correct string of parameters
def reformatLine(line, attDict):


   firstFormat = line.split('LINEBEGIN')[1]
   reformat = firstFormat.split('DONEEND')[0]
   attributes = firstFormat.split('DONEEND')[1]
   num = attributes.split('ABSTAIN')[1]
   realnum = attributes.split('ENDABSTAIN')[0]
   print(str(attributes))
   attDict.update({'NumAbstain': realnum})

   return reformat


def main():
    print("STARTED")
    global NUM_ITERATIONS
    global PARAMETERS
    global file
    global final_Dict
    global reform
    global minInDay
    global runTime
    global mode
    global running

    runTime = int(time.time() * 1000)
    buildLogs()

    priceList = generatePriceSymbols(1000, -1)
    strPriceList = str(priceList)

    #untested function that should check if there are command line arguments
    #setVals()
    resetParameters(PARAMETERS)



    #store the multiple processes
    for i in range(NUM_CLASSES):
        typeOfRandom = 3
        current_Max = 0.0
        procs = []
        count = 0
        variationNum = 0.0
        minInDay = 1440.0


        #if this is the second class you need to reopen the file because it has been closed to commit the changes of the first class
        if i > 0:
            paramCompletePath = os.path.join(paramPaths, "TEST_PARAMETERS.txt")
            file = open(paramCompletePath, "r+")

        #creates NUM_ITERATIONS amounts of bots
        for j in range(NUM_ITERATIONS):


            proc = Popen([sys.executable, 'CryptoEvaluator.py', '{}in.txt'.format(i), '{}out.txt'.format(i)], stdout=PIPE, stdin = PIPE, stderr=PIPE, bufsize=1, universal_newlines=True)
            procs.append(proc)

         #randomizes parameters and runs different instances of the bot using the different starting parameters
        for proc in procs:
            reform = ''

            #randomize parameters and send the bot their class and variation num
            randomizeParams(PARAMETERS, typeOfRandom)
            PARAMETERS['CLASS_NUM'] = i
            PARAMETERS['VARIATION_NUMBER'] = variationNum

            #make the max cycles equal to the number of days of the interval in hours
            PARAMETERS['MAX_CYCLES'] = (PARAMETERS['INTERVAL_TO_TEST'] / minInDay) * 24.0

            #reset typeOfRandom so that every 50th run we use a special set of randomizers
            if(count % 50 == 0):
                typeOfRandom = 1
            if(count % 50 != 0):
                typeOfRandom = 0

            #passing the parameters to the processes by pickling!
            '''
            with open ("PARAMETERS.pkl", "wb") as pickle_file:
                pickle.dump(PARAMETERS, pickle_file)
            with open("RunTime.pkl", "wb") as pickle_file:
                pickle.dump(runTime, pickle_file)
            with open("Mode.pkl","wb") as pickle_file:
                pickle.dump(running, pickle_file)
            with open("priceList.pkl", "wb") as pickle_file:
                pickle.dump(priceList, pickle_file)
            '''
            out = proc.communicate(input = str(PARAMETERS) + ' RunTime ' + str(runTime) + ' Mode ' + str(running))
            timestamp = int(time.time() * 1000)
            print(str(timestamp))
            print("CLASS NUM " + str(PARAMETERS['CLASS_NUM']) + " VARIATION NUMBER " + str(PARAMETERS['VARIATION_NUMBER']))
            print("OUTPUT" + str(out))

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
                reform = reformatLine(val, attributeDict)

                print("REFORM" + str(reform))

                substring = reform.split("\'CUMULATIVE_PERCENT_CHANGE_STORE\':", 1)[1]

                cumulativePerentChangeStore = substring.split(',', 1)[0]

                print("THIS" + str(cumulativePerentChangeStore))
                cumulativePerentChangeStore = float(cumulativePerentChangeStore)

                #print(str(cumulativePerentChangeStore))

                #if the cumulative Percent Stored is greater than the current Max store it and the line of parsed input that it was from
                if (cumulativePerentChangeStore >= current_Max and 20 > (PARAMETERS['MAX_CYCLES'])/2) or count == 0 :
                    current_Max = cumulativePerentChangeStore
                    stored_output = reform
                count += 1
            #reset the parameters dictionary to the original "best" one from the file
            resetParameters(PARAMETERS)
            variationNum += 1
        #convert the stored, parsed string into a dictionary
        final_Dict = stringToDict(stored_output)

        print('Stored : {}'.format(stored_output))
        print('Current Max: {}'.format(current_Max))



        #rewrite the parameter file with the final Dict
        reWriteParameters(final_Dict)
        for z in procs:
            z.wait()

        file.close()


if __name__ == "__main__":
    main()