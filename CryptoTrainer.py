# Copyright (c) 2018 A&D
# Auto trading tester that runs multiple versions of the trader with different parameters

# todo add a function to randomize the parameters when requested
# todo make the randomize parameters function implement the different types of randomization
# todo make it so that every test having extremely negative output does not still overwrite best parameters
# todo add in on/off switches and make them do different things for different parameters (i.e. something like negative weight should get treated like a 1.0 not a 0.0 since it is used in necessary calculations)
# todo add in different negative weights depending on which is used.

import sys
import random
import time
import os
import pathlib
import pickle
import logging


from subprocess import Popen, PIPE
from PrivateData import api_key, secret_key
from Generics import UNCHANGED_PARAMS, superParams, defaulttrainerparamspassed, PARAMETERS, priceSymbols, calcPercentChange

# setup the relative file path
dirname = os.path.dirname(os.path.realpath(__file__))


# Directory path (r makes this a raw string so the backslashes do not cause a compiler issue
paramPaths = os.path.join(dirname, '')


# makes the directorys in the path variable if they do not exist
pathlib.Path(paramPaths).mkdir(parents=True, exist_ok=True)

# joining path for the param pickle file
paramCompletePath = os.path.join(paramPaths, "param.pickle")


# will hold the specific parameter given to each list
PARAM_CHOSEN = {}


# will hold the specific parameter given to each list
PARAM_CHOSEN = {}


# list of each variation of the parameter list, one is passed to each instance of the bot
PARAMETER_VARIATIONS = []

# number of minutes in a day
minInDay = 1440

# final dictionary returned to be rewritten to file
final_Dict = {}


# the timestamp for the run
runTime = 0


# a dictionary with attributes passed back from an evaluator
attributeDict = {}

# dictionary of the changed parameters with each rewrite of the parameters file
changed = {}

# the return each run of the crypto currency got
returns = []

#set up the log for this trainer
def setUpLog(logdirectory, logfilename):
    """
    :param logdirectory:
    :param logfilename:
    :return:
    """
    logging.basicConfig(filename=logdirectory+logfilename, level='DEBUG')

# reads pickle from a file into the passed parameter dictionary
def readParamPickle(directory, filename):
    """
    :param directory: the path of the pickle file
    :param filename: the name of the pickle file
    :return:
    """
    # makes the directorys in the path variable if they do not exist
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

    with open(directory + filename, "rb") as pickle_in:
        paramDict = pickle.load(pickle_in)

    return paramDict

# write pickle to a file
def writeParamPickle(storeval, path, filename):
    """
    :param storeval: the object to be written
    :param path: path to the pickle file
    :param filename: the name of the file to pickle to
    :return:
    """
    with open(path + filename, "wb") as pickle_out:
        pickle.dump(storeval, pickle_out)

def keyCheck(key):
    """
    :param key:
    :return:
    """
    for i in UNCHANGED_PARAMS:
        if i == key:
            return 1

    return 0

# randomizes the parameters before sending them to a subprocess
# typeOfRandom determines what kinds of randomization occurs
# type 0 means normal, type 1 means larger range of randomization
# type 3 means none
# TODO remember after to testing not to randomize stuff like cumulative percent change store (i.e data)


def randomizeParams(paramDict, typeOfRandom, baseparams):
    """
    :param paramDict: the parameter dictionary
    :param typeOfRandom: the integer corresponding to the way to randomize
    :param baseparams: the parameters passed to the trainer
    :return:
    """
    if(typeOfRandom == 3): #keep the default parameters
        return 0
    if (typeOfRandom == 0):
        for key, value in paramDict.items():
            randcheck = int(random.uniform(0, 1) * baseparams['randcheckrangeone'])


            if(keyCheck(key) != 1 and randcheck > baseparams['lowercheckthreshold']):
                randVal = paramDict[key]
                randVal += random.uniform(-1, 1) * baseparams['smallrange'] + baseparams['lowoffirstrange']
                paramDict[key] = randVal

    # todo add a normal kind of randomization
    if(typeOfRandom == 1):
        for key, value in paramDict.items():
            randcheck = int(random.uniform(0, 1) * baseparams['randcheckrangetwo'])

            if(keyCheck(key) != 1 and randcheck > baseparams['uppercheckthreshold']): #if the key is not in the unchangeable params list and
                                                       #the random number generated clears the threshold for modifying it
                randVal = paramDict[key]
                randVal += random.uniform(-1, 1) * baseparams['bigrange'] + baseparams['lowofsecondrange']
                paramDict[key] = randVal


# converts the given string to a Dict. Used to parse the returned string from the bots being trained
def stringToDict(stringToChange):
    """
    :param stringToChange:
    :return:
    """
    newDict = {}
    stringKeySplit = ''
    stringValSplit = ''
    counter = 0

    # split the passed string into a list seperated by spaces
    listSplits = stringToChange.split(' ')

    # loops through each string seperated out into listSplits
    for i in listSplits:
        # if the string is from an even position split it into a future key
        if (counter % 2 == 0):
            stringKeySplit = i.split('\'')[1]
        # if the string is from an odd position split it to be a future value and update newDict to contain it
        if (counter % 2 != 0):
            if ("," in i):
                stringValSplit = i.split(',')[0]
            if("}" in i):
                stringValSplit = i.split('}')[0]
            newDict.update({stringKeySplit: stringValSplit})

        counter += 1

    return newDict

# makes the string line exclusively consist of the correct string of parameters


def reformatLine(line, attDict):
    """
    :param line:
    :param attDict:
    :return:
    """
    firstFormat = line.split('LINEBEGIN')[1]
    reformat = firstFormat.split('DONEEND')[0]
    attributes = firstFormat.split('DONEEND')[1]

    return reformat


# pickles the different input files for each bot run


def pickleInput(paramDict, paramspassed):
    """
    :param paramDict: dictionary to be pickled
    :param paramspassed: parameters that have been passed to this trainer
    :return:
    """

    pickleDirect = "{}/{}/{}/{}/{}/{}/{}/{}/variations/".format(dirname, 'training', paramspassed['website'],paramspassed['day'],
                                                                  paramspassed['hour'], paramspassed['min'], paramspassed['idnum'], paramDict['CLASS_NUM'])

    # passing the parameters to the processes by pickling!
    with open(pickleDirect + str(int(paramDict['VARIATION_NUMBER'])) + "param.pkl", "wb") as pickle_file:
        pickle.dump(paramDict, pickle_file)



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

#read the parameters passed to the file
def readParamsPassed():

    """
    :return: the parameters passed and the base parameters (the ones used to generate the evaluators)
    """


    if len(sys.argv) == 1:
        paramspassed = defaulttrainerparamspassed
        baseparams = superParams
        paramspassed = defaulttrainerparamspassed
        baseparams = superParams
    elif sys.argv[1] == "Alone":
        paramspassed = defaulttrainerparamspassed
        baseparams = superParams
        paramspassed = {'website': sys.argv[2], 'day': sys.argv[3], 'hour': sys.argv[4], 'min': sys.argv[5],
                        'idnum': int(sys.argv[6])}
        baseparams = superParams
        baseparams['classes'] = sys.argv[7]
        baseparams['variations'] = sys.argv[8]
    else:
        for line in sys.stdin:
            if line != '':
                params = line.split()
                paramspassed = {'website': params[0], 'day': params[1], 'hour': params[2], 'min': params[3],
                                'idnum': int(params[4])}
                directory = "{}/{}/{}/{}/{}/{}/".format(dirname, 'training', paramspassed['website'], paramspassed['day'], paramspassed['hour']
                                          , paramspassed['min'])
                # makes the directorys in the path variable if they do not exist
                pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
                baseparams = readParamPickle(directory, str(int(paramspassed['idnum']))+"superparam.pkl")


    return paramspassed, baseparams

#builds the logs for the trainer file if none is created and prepares the logs for the evaluator files
# makes a log file for this instance of the trainer that is sorted into a folder by the date it was run
# and its name is just its timestamp
def initdirectories(paramspassed, baseparams, typedirec='storage'):
    """
    :param paramspassed: the parameters passed from the command line or the superTrainer
    :param baseparams: the parameter of this trainer file
    :param typedirec: the type of the directory (storage, training)
    :return:
    """

    directory = "{}/{}/{}/{}/{}/{}".format(dirname, typedirec, paramspassed['website'], paramspassed['day'], paramspassed['hour']
                                          , paramspassed['min'])

    # makes the directorys in the path variable if they do not exist
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

    #makes the directory of the associated idnum exist if it does not already
    pathlib.Path("{}/{}".format(directory, paramspassed['idnum'])).mkdir(parents=True, exist_ok=True)

    #if this is a training directory then make a class file for the param variaitons to be picked by the evaluator bots
    #and make log directory for each class
    if typedirec == 'training':
        for numclass in range(int(baseparams['classes'])):
            # makes the param directory of the associated class exist if it does not already
            pathlib.Path("{}/{}/{}/variations".format(directory, paramspassed['idnum'], numclass)).mkdir(parents=True, exist_ok=True)

            # makes the log directory of the associated class exist if it does not already
            pathlib.Path("{}/{}/{}/logs".format(directory, paramspassed['idnum'], numclass)).mkdir(parents=True, exist_ok=True)


# creates the specified number amounts of bots
def createBots(baseparams, classnum):
    """
    :param baseparams: the parameters used by this trainer
    :param classnum: the number of the class of this bot
    :return: dictionary of subprocesses (bots)
    """
    procs = []
    for j in range(baseparams['variations']):
        proc = Popen([sys.executable, 'CryptoEvaluator.py', '{}in.txt'.format(classnum), '{}out.txt'.format(classnum)], stdout=PIPE,
                     stdin=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True)
        procs.append(proc)

    return procs

#get the correct dictionary using the parameters passed
def buildDirectory(botparams, passparams, typedirec='storage', typefile='variations'):
    """
    :param botparams: the parameters for the bot
    :param passparams: the parameters passed to this trainer
    :param typedirec: the type of the directory (storage or training)
    :param typefile: the type of the file being looked for (variations or logs)
    :return: the directory string
    """

    return "{}/{}/{}/{}/{}/{}/{}/{}/".format(dirname, typedirec, passparams['website'], passparams['day'], passparams['hour'],
                                       passparams['min'],passparams['idnum'],botparams['CLASS_NUM'], typefile,
                          )

def main():
    global final_Dict
    global reform
    global minInDay
    global runTime



    # keeps track of how many times the parameters are changed
    newParamCount = 0

    runTime = int(time.time() * 1000)

    paramspassed, baseparams = readParamsPassed()
    initdirectories(paramspassed, baseparams)
    initdirectories(paramspassed,baseparams,  typedirec='training')

    direc = "{}/{}/{}/{}/{}/{}/{}/".format(dirname, 'training', paramspassed['website'], paramspassed['day'], paramspassed['hour'],
                                        paramspassed['min'], paramspassed ['idnum'])

    #directory name where the log file is stored
    logdirectory = direc + 'trainerlogs/'
    #name of the directory log file
    logfilename = 'trainer.log'
    #setup up the log file for this trainer
    setUpLog(logdirectory, logfilename)

    #setup a reference parameter file to edit
    writeParamPickle(PARAMETERS, direc, 'baseparams.pkl')

    #setup the parameters used to be the base parameters
    params = readParamPickle(direc, 'baseparams.pkl')

    # store the multiple processes
    for i in range(baseparams['classes']):
        typeOfRandom = 3
        current_Max = 0.0
        count = 0
        variationNum = 0.0
        minInDay = 1440.0

        procs = createBots(baseparams, i)

         # randomizes parameters and runs different instances of the bot using the different starting parameters
        for proc in procs:
            reform = ''

            # randomize parameters and send the bot their class and variation num
            randomizeParams(params, typeOfRandom, baseparams)
            params['CLASS_NUM'] = i
            params['VARIATION_NUMBER'] = int(variationNum)

            # make the max cycles equal to the number of days of the interval in hours
            params['MAX_CYCLES'] = (params['INTERVAL_TO_TEST'] / minInDay) * 24.0

            # reset typeOfRandom so that every 50th run we use a special set of randomizers
            if(count % 50 == 0):
                typeOfRandom = 1
            if(count % 50 != 0):
                typeOfRandom = 0

            # store parameters and other variables in pickle files for this bot
            pickleInput(params, paramspassed)

            # make one bot run with the input stream of runtime, mode, directory path, classnum, and variationum
            out = proc.communicate(input="{} {} {} {} {} {} {}".format(paramspassed['website'], paramspassed['day'], paramspassed['hour'],
                                   paramspassed['min'], params['CLASS_NUM'], params['VARIATION_NUMBER'], paramspassed['idnum']))
            print(str(out))

            #build the directory string for the parameter dictionary
            directory = buildDirectory(params, paramspassed, typedirec='training')

            #get the parameter file from the recently finished evaluator bot
            params = readParamPickle(directory + 'variations/'
                                                 , str(int(params['VARIATION_NUMBER'])) + 'param.pkl')

            cumulativePerentChangeStore = calcPercentChange(params['START_MONEY'], params['END_MONEY'])

            returns.append(cumulativePerentChangeStore)

            # if the cumulative Percent Stored is greater than the current Max store it and the line of parsed input that it was from
            if (cumulativePerentChangeStore >= current_Max and params['CYCLES'] > superParams['MIN_CYCLES'] and
                    cumulativePerentChangeStore != 0.0 or count == 0):
                current_Max = cumulativePerentChangeStore
                stored_output = params
                newParamCount += 1
            #load the stored base parameters for this class before the next variation is made
            params = readParamPickle(direc, "baseparams.pkl")
            variationNum += 1

        print('Current Max: {}'.format(current_Max))
        final_Dict = stored_output
        for z in procs:
            z.wait()

        # rewrite the parameter file with the final Dict
        writeParamPickle(final_Dict, direc, 'baseparams.pkl')


if __name__ == "__main__":
    main()
