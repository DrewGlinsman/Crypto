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
from Generics import UNCHANGED_PARAMS, superParams, defaulttrainerparamspassed, PARAMETERS, priceSymbols, \
    calcPercentChange, listparms, removeEmptyInnerLists, paramsthatcanbecombined, numFiles




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
    :param key: param dictionary key
    :return: 1 if the parameter cannot be randomized and 0 if it can and 3 if it needs to be altered specially
    """

    if key in UNCHANGED_PARAMS: #check if the key is in the list of unchanageable parameters
        return 1

    if key in listparms: #check if this is a list parameter
        return 3

    return 0

# randomizes the parameters before sending them to a subprocess
# typeOfRandom determines what kinds of randomization occurs
# type 0 means normal, type 1 means larger range of randomization
# type 3 means none

def randomizeParams(paramDict, typeOfRandom, baseparams, combinableparams):
    """
    :param paramDict: the parameter dictionary
    :param typeOfRandom: the integer corresponding to the way to randomize
    :param baseparams: the parameters passed to the trainer
    :param combinableparams: the list of parameters that can be combined to form new parameters
    :return:
    """

    ####VALUES EXPLAINING THE PASSED TYPES OF RANDOM#################
    keepdefaultparams = 3
    usesmallerrangerandom = 0
    uselargerangerandom = 1

    ####################VALUES EXPLAINING THE KEYCHECK################
    isalistparameter = 3
    isanunchangeableparameter = 1

    if(typeOfRandom == keepdefaultparams): #keep the default parameters
        return paramDict

    if (typeOfRandom == usesmallerrangerandom):
        for key, value in paramDict.items():
            #generate a value that will be used to determine whether this parameter will be randomized
            randcheck = int(random.uniform(0, 1) * baseparams['randcheckrangeone'])


            #check if this is a list parameter in which case it has to be modified specially
            check = keyCheck(key)

            #if the parameter is a list
            if check == isalistparameter:

                randomizeParamsList(paramDict, key, baseparams['randcheckrangeone'], baseparams['lowercheckthreshold'],
                                    baseparams['smallrange'], baseparams['lowoffirstrange'],
                                    combinableparams, baseparams['lowerstopcheckthreshold'],
                                    baseparams['lowerremovecheckthreshold'], baseparams['maxcombinedparams'],
                                    baseparams['maxparameterscombinedpercombinedparam'])

            #if this is not an unchangeable parameter and the random value generated is above the
            #randomized threshold (meaning this parameter will be randomized)
            elif(check != isanunchangeableparameter and randcheck > baseparams['lowercheckthreshold']):
                randVal = paramDict[key]
                randVal += (random.uniform(-1, 1) * baseparams['smallrange']) + baseparams['lowoffirstrange']
                paramDict[key] = randVal

    if(typeOfRandom == uselargerangerandom):
        for key, value in paramDict.items():
            randcheck = int(random.uniform(0, 1) * baseparams['randcheckrangetwo'])

            #check if this is a list parameter in which case it has to be modified specially
            check = keyCheck(key)

            #if the parameter is a list
            if check == isalistparameter:

                randomizeParamsList(paramDict, key, baseparams['randcheckrangetwo'], baseparams['uppercheckthreshold'],
                                    baseparams['bigrange'], baseparams['lowofsecondrange'],
                                    combinableparams, baseparams['upperstopcheckthreshold'],
                                    baseparams['upperremovecheckthreshold'], baseparams['maxcombinedparams'],
                                    baseparams['maxparameterscombinedpercombinedparam'])

            # if the key is not in the unchangeable params list and
            # the random number generated clears the threshold for modifying it
            elif(check != isanunchangeableparameter and randcheck > baseparams['uppercheckthreshold']):
                randVal = paramDict[key]
                randVal += (random.uniform(-1, 1) * baseparams['bigrange']) + baseparams['lowofsecondrange']
                paramDict[key] = randVal


    return paramDict

# randomize the list parameters. used to modify the list of lists of parameters to combine (to make new parameters)
# and to modify the list of the modifiers for each list of parameters to combine
# combinedparams = [[param1, param2], [param3, param1,param5]]
# combinedparamsmodifiers = [modifier1, modifier2]
def randomizeParamsList(params, keytochange, randcheckrange, checkthreshold, rangevals, lowvalueofrange, combinableparams,
                        stopchangingparamsthreshold, removeparamsthreshold,
                        maxcombinedparams, maxparameterscombinedpercombinedparam):
    """
    :param params: the parameter dictionary to be changed
    :param keytochange: the key value to change
    :param randcheck: the value used to set a range of random values to be used to determine if a parameter should be randomized
    :param checkthreshold: the value that the random check value has to be higher than to allow the parameter to be randomized
    :param rangevals: the range used to make a random value to change the parameter
    :param lowvalueofrange: the low value of that range of values to change the parameter by
    :param combinableparams: the list of parameters that can be combined to form new parameters
    :param stopchangingparamsthreshold: the randomized value must be above this to keep changing a set of parameters
    to combine
    :param removeparamsthreshold: the randomized value must be below this to remove a parameter and above it
    to add one (implied that it is already above the stopchangingparamsthreshold)
    :param maxcombinedparams: the maximum number of combined parameters that a bot can use
    :param maxparameterscombinedpercombinedparam: the maximum number of parameters combined in each combined parameter
    :return: the modified parameter dictionary
    """


    #if the param list is the list of combined params
    #this should be a list of lists where each list is made of the parameters to be combined
    #the first letter of each parameter is whether it should be added (+) or multipled (*) to the
    # rest of the parameters
    if keytochange == 'COMBINED_PARAMS':

        #the upperlimit of the range of random values (is not included in range)
        upperlimitofrange = randcheckrange

        #loop and add new combined parameter lists until we stop
        #and we have not exceeded this trainer's max length of allowed combined parameters
        while(checkaddnewcombinedparamlist(upperlimitofrange, stopchangingparamsthreshold)
              and len(params[keytochange]) < maxcombinedparams):

            #makes a new list for a combined parameter
            indexofnewlist = addnewcombinedparamlist(params[keytochange])

            #picks and then adds a random combinable parameter to the list
            addcombinedparamtolist(params[keytochange][indexofnewlist],
                                   maxparameterscombinedpercombinedparam, combinableparams)

            #generates and adds a modifier to be associated with that combined parameter list
            addmodifiertocombinedparammodifierlist(params['COMBINED_PARAMS_MODIFIERS'], rangevals, lowvalueofrange)

        #loop through the lists of the combined parameters
        for listofcombinedparams in params[keytochange]:

            #first generate a value to make a decision
            modifiyparamdecision = int(random.uniform(0,1) * upperlimitofrange)

            #while the decision value is not to add or remove a parameter or when there are no parameters left in the list
            while(modifiyparamdecision > stopchangingparamsthreshold or len(listofcombinedparams) == 0):
                #if we choose to remove a parameter
                if modifiyparamdecision <= removeparamsthreshold:
                    #generate a value corresponding to an index in the list of parameters to combined
                    #the value is used to decide which parameter to remove
                    indexofparamtoremove = int(random.uniform(0,1) * len(listofcombinedparams))

                    #remove the specified parameter
                    del listofcombinedparams[indexofparamtoremove]

                #if we choose to add a parameter
                elif modifiyparamdecision > removeparamsthreshold:

                    #add a parameter to the current list of combined parameters
                    addcombinedparamtolist(listofcombinedparams, maxparameterscombinedpercombinedparam,
                                           combinableparams)


                #generate a new value for the next decision
                modifiyparamdecision = int(random.uniform(0, 1) * upperlimitofrange)


        #go through the list of lists of combined parameters and remove any lists that are empty
        #simultaneously delete any entries from the list of the modifiers for the combined parameters
        #that correspond to the empty combined parameter lists
        #so if param1 = [[1,2],[]] and param2 = [1,2]
        #then the method changes them to param1 = [[1,2]] and param2 = [1]
        removeEmptyInnerLists(params[keytochange], params['COMBINED_PARAMS_MODIFIERS'])

    #if the param list is the list of combined param modifiers
    elif keytochange == 'COMBINED_PARAMS_MODIFIERS':

        #ensure that the list of combined params modifiers has one modifier for every list in the list of lists
        # of parameters to combine (to make new parameters)
        if (len(params[keytochange]) != len(params['COMBINED_PARAMS'])):
            logging.error("the combined parameter list and the list of its modifiers are not equal length")
            logging.error("combined parameter list length {}".format(len(params['COMBINED_PARAMS'])))
            logging.error("combined parameter modifier list length {}".format(len(params[keytochange])))
            exit(-1)

        #iterate through the list of the combined params modifiers
        #one modifier for each list of combined params
        for modifierindex in range(len(params[keytochange])):

            #generate a value to be used to determine if this modifier will be changed
            randcheck = int(random.uniform(0,1) * randcheckrange)

            #if the random value is above the threshold set for allowing modification
            if randcheck > checkthreshold:

                #generate the random value to modify the modifier with
                randval = (random.uniform(-1,1) * rangevals) + lowvalueofrange

                #modify the combined parameter modifier by that random value generated
                params[keytochange][modifierindex] += randval

    else:
        logging.error("not a valid list key: {}".format(keytochange))
        quit(-1)

#return true if we should add a new combined parameter
def checkaddnewcombinedparamlist(upperlimitrange, stopchangingparamsthreshold):
    """
    :param upperlimitrange: the upper limit of the range of values to generate
    :param stopchangingparamsthreshold: the threshold we need to generate a value above to add a parameter to be combined
    :return:
    """

    # first generate a value to make a decision
    addparamdecisiomn = int(random.uniform(0, 1) * upperlimitrange)

    #if we determine we want to add a parameter
    if addparamdecisiomn > stopchangingparamsthreshold:
        return True

    return False

#make a new list in the combined parameters list so that combinable parameters can be added to the list
# return the index of the new combined parameter list
def addnewcombinedparamlist(combinedparamslist):
    """
    :param combinedparamslist: the parameter dictionary value list that contains all the combined parameters in lists
    :return: the index of the parameter we added
    """

    #index of the new list will be the length of the old list
    indexofnewcombinedparamlist = len(combinedparamslist)



    #add a new list to the combined parameter list
    combinedparamslist.append([])

    return indexofnewcombinedparamlist

#adds a combined parameter to a list in the lists of combined parameters
def addcombinedparamtolist(listofcombinedparams, maxparameterscombinedpercombinedparam, combinableparams):
    """
    :param listofcombinedparams: the list of parameters to be combined we will add another parameter to combine with
    :param maxparameterscombinedpercombinedparam: the maximum number of parameters that can be combined
    :param combinableparams: list of parameters that can be combined
    :return:
    """

    #if that list already has too many parameters to combine we do nothing
    if len(listofcombinedparams) > maxparameterscombinedpercombinedparam:
        return

    # the upper limit that is not included in the add or multiply or subtract parameter decision below
    rangeofdecision = 3

    # the three decisions that can be made about what to do with this parameter
    addition = 0
    subtraction = 1
    multiplication = 2

    # generate a value to determine if this parameter will be added or multipled or subtracted
    # so if added then paramtocombine + alltheothercombinedparams
    # and if multipled paramtocombine * alltheothercombinedparams
    # and if subtracted paramtocombine - alltheothercominedparams
    includeparamdecision = int(random.uniform(0, 1) * rangeofdecision)

    # generate a value corresponding to an index in the list of parameters that can be combined
    # the value is used to decide which parameter to add to the current list of combined parameters
    indexofparamtoinclude = int(random.uniform(0, 1) * len(combinableparams))

    # depending on what we want to do with this parameter we add it to the list
    # of parameters to combine for this particular new parameter and we add a symbol
    # to the front of the parameter name indicating what to do with this parameter
    if includeparamdecision == addition:
        listofcombinedparams.append("+ {}".format(combinableparams[indexofparamtoinclude]))
    elif includeparamdecision == multiplication:
        listofcombinedparams.append("* {}".format(combinableparams[indexofparamtoinclude]))
    elif includeparamdecision == subtraction:
        listofcombinedparams.append("- {}".format(combinableparams[indexofparamtoinclude]))

    else:
        logging.error("not a valid decision {}".format(includeparamdecision))
        quit(-1)

#generate and add a new modifier value for a new combined parameter list
def addmodifiertocombinedparammodifierlist(listofcombinedparametermodifiers, rangevals, lowvalueofrange):
    """
    :param listofcombinedparametermodifiers: the list of the combined parameter modifiers so far
    :param rangevals: the range of values to consider as modifiers
    :param lowvalueofrange: the low value of the range to consider
    :return:
    """

    # instantiate a new modifier value in the corresponding list of combined parameters modifiers
    # each list of combined parameters gets one modifier
    # so combinedparams =  [[param1, param2], [param1, param3, param4]
    # would have combinedparamsmodifiers = [modifier1, modifier2]
    newmodifiervalue = (random.uniform(-1, 1) * rangevals) + lowvalueofrange

    # add the new modifier value to the end of the parameter list of modifiers
    listofcombinedparametermodifiers.append(newmodifiervalue)

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


def pickleInput(paramDict, paramspassed, dirname):
    """
    :param paramDict: dictionary to be pickled
    :param paramspassed: parameters that have been passed to this trainer
    :param dirname: the base directory name
    :return:
    """

    pickleDirect = "{}/{}/{}/{}/{}/{}/{}/{}/".format(dirname, 'training', paramspassed['website'],paramspassed['day'],
                                                                  paramspassed['hour'], paramspassed['min'],
                                                     paramspassed['idnum'], paramDict['CLASS_NUM'])

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
def readParamsPassed(dirname, baseparams, paramspassed):

    """
    :param dirname: the relative directory for the files
    :param baseparams: the params used by this trainer file
    :param paramspassed: the params given to this trainer with information about how it should run
    :return: the parameters passed and the base parameters (the ones used to generate the evaluators)
    """


    if sys.argv[1] == "CryptoTrainer": #parameters have been passed through console or run configuration (i.e. this is run on its own)
        paramspassed = {'directoryprefix': sys.argv[1],'website': sys.argv[2], 'day': sys.argv[3], 'hour': sys.argv[4], 'min': sys.argv[5],
                        'idnum': int(sys.argv[6]), 'originalid': sys.argv[9], 'evalID': sys.argv[10],
                        'lossallowed': sys.argv[11], 'startmoney': sys.argv[12]}
        baseparams['classes'] = sys.argv[7]
        baseparams['variations'] = sys.argv[8]

        #true directory accounts for what script is running this (or rather what is running the chain of scripts if there are multiple levels)
        truedirectory = "{}/{}".format(dirname, sys.argv[1])

    elif len(sys.argv) != 3:  #there are no paramters passed so use default
        # true directory accounts for what script is running this (or rather what is running the chain of scripts if there are multiple levels)
        truedirectory = "{}/CryptoTrainer".format(dirname)

    else: #the parameters have been passed from another script that is running this one
        for line in sys.stdin:
            if line != '':
                params = line.split()

                paramcount = 0
                for key, value in paramspassed.items():
                    paramspassed.update({key: params[paramcount]})
                    paramcount += 1
                # true directory accounts for what script is running this (or rather what is running the chain of scripts if there are multiple levels)
                truedirectory = "{}/{}".format(dirname, (paramspassed['directoryprefix']))



    return paramspassed, truedirectory

#builds the logs for the trainer file if none is created and prepares the logs for the evaluator files
# makes a log file for this instance of the trainer that is sorted into a folder by the date it was run
# and its name is just its timestamp
def initdirectories(paramspassed, baseparams, dirname, evaluatorparams, typedirec='storage'):
    """
    :param paramspassed: the parameters passed from the command line or the superTrainer
    :param baseparams: the parameter of this trainer file
    :param dirname: the base directory relative to the file system
    :param evaluatorparams: the evaluator params used to setup an evaluator in case this is a single cryptoTrainer file
    :param typedirec: the type of the directory (storage, training)
    :return:
    """

    directory = "{}/{}/{}/{}/{}/{}/".format(dirname, typedirec, paramspassed['website'], paramspassed['day'],
                                           paramspassed['hour'], paramspassed['min'])

    # makes the directorys in the path variable if they do not exist
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

    #makes the directory of the associated idnum exist if it does not already
    pathlib.Path("{}/{}".format(directory, paramspassed['idnum'])).mkdir(parents=True, exist_ok=True)


    #if we are running a CryptoTrainer by itself it must make a param file for its evaluators if none exists
    #also make the super param file for the trainer if none exists
    if paramspassed['directoryprefix'] == 'CryptoTrainer':

        #if we are initializing the training directory  and there are no parameter files
        # for the crypto trainer to use we store one
        if typedirec == 'training':

            if numFiles(directory) == 0:
                #make the super param file for this trainer
                writeParamPickle(baseparams,directory,'{}superparam.pkl'.format(paramspassed['idnum']))

        # the storage directory to write the evaluator (base) params
        storagedirectory = "{}{}/".format(directory, paramspassed['originalid'])

        if numFiles(directory) == 0 and typedirec == 'storage':
            #make the evalautor params file
            writeParamPickle(evaluatorparams, storagedirectory, '{}baseparams.pkl'.format(paramspassed['evalID']))

    #if this is a training directory then make a class file for the param variaitons to be picked by the evaluator bots
    #and make log directory for each class
    if typedirec == 'training':
        for numclass in range(int(baseparams['classes'])):
            # makes the param directory of the associated class exist if it does not already
            pathlib.Path("{}/{}/trainerlogs".format(directory, paramspassed['idnum'])).mkdir(parents=True, exist_ok=True)

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
    for j in range(int(baseparams['variations'])):
        proc = Popen([sys.executable, 'CryptoEvaluator.py', '{}in.txt'.format(classnum), '{}out.txt'.format(classnum)], stdout=PIPE,
                     stdin=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True)
        procs.append(proc)

    return procs

#get the correct dictionary using the parameters passed
def buildDirectory(botparams, passparams, dirname, typedirec='storage', typefile='variations'):
    """
    :param botparams: the parameters for the bot
    :param passparams: the parameters passed to this trainer
    :param dirname: the base directory relative to the file system
    :param typedirec: the type of the directory (storage or training)
    :param typefile: the type of the file being looked for (variations or logs)
    :return: the directory string
    """

    return "{}/{}/{}/{}/{}/{}/{}/{}/".format(dirname, typedirec, passparams['website'], passparams['day'], passparams['hour'],
                                       passparams['min'] , passparams['idnum'],botparams['CLASS_NUM'], typefile,
                          )

#changes and returns parameter values passed to reflect the success/failure of this trainer's run
def updateParams(baseparams, defaultbaseparams, valuesrecorded):
    """
    :param baseparams: the "super params" read in from the pickle file corresponding to this trainer
    :param defaultbaseparams: the default parameters used prior to any randomization or optimization
    :param valuesrecorded: the values recorded that detail how this trainer's bot classes performed
    :return: updated baseparams
    """


    #scale the percent changes to make the percentages relative to 1 trade per hour for a day timeframe
    scaleby = (baseparams['INTERVAL_TO_TEST']/baseparams['MAX_CYCLES'])/(defaultbaseparams['INTERVAL_TO_TEST']/
                                                                         defaultbaseparams['MAX_CYCLES'])

    updateparams = baseparams

    # the percentage of the bots generated that were positive
    updateparams.update({'percentpositivebots': valuesrecorded['numposbots'] / valuesrecorded['numbots'] * 100})

    # the percentage of the bots generated that were negative
    updateparams.update({'percentnegativebots': valuesrecorded['numnegbots'] / valuesrecorded['numbots'] * 100})

    # the average bot return
    updateparams.update({'averagebotreturnsaved': (valuesrecorded['totalbotreturn'] / valuesrecorded['numbots']) * scaleby})

    # the worst bot return
    updateparams.update({'worstbotreturnsaved': (valuesrecorded['worstbotreturn']) * scaleby})

    # the best bot return
    updateparams.update({'bestbotreturnsaved': (valuesrecorded['bestbotreturn']) * scaleby})

    return updateparams

#checks if the parameters of the same name in the trainer param file have the same value as their associated
#evaluator param file and write back the evaluator file to the storage directory if anything was changed
def checksharedparams(trainerparams, evaluatorparmas, paramspassed, storagedirectory):
    """
    :param trainerparams: the parameters used by the trainer
    :param evaluatorparmas: the parameters used as the base for all the training of the bots
    :param paramspassed: the parameters passed to this trainer
    :param storagedirectory: the directory where all the original parameters are stored
    :return:
    """

    #counter for the number of parameters we change if they do not match the trainer's values
    counterchangedparams = 0

    #loop through the trainer parameters
    for key, value in trainerparams.items():

        #if this key is also in the evaluator param dict
        if key in evaluatorparmas:
            #if the values are not the same
            if trainerparams[key] != evaluatorparmas[key]:
                #rewrite the evaluator params value with the trainer params value
                evaluatorparmas.update({key: value})
                #increment counter
                counterchangedparams += 1


    #if we change any parameter, rewrite the evaluator params file to the storage directory so
    #that any future uses of the evaluator will have the correct shared parameters
    if counterchangedparams > 0:
        writeParamPickle(evaluatorparmas, storagedirectory, '{}baseparams.pkl'.format(paramspassed['evalID']))

def main():
    global final_Dict
    global reform
    global minInDay
    global runTime

    # setup the relative file path
    homedirectory = os.path.dirname(os.path.realpath(__file__))

    #values to be recorded by this trainer for storage in its passed parameter file
    valuesrecorded =  {'numbots': 0, 'numposbots': 0, 'numnegbots': 0, 'totalbotreturn': 0.0,
                       'worstbotreturn': 0.0, 'bestbotreturn': 0.0}

    # keeps track of how many times the parameters are changed
    newParamCount = 0

    #grab the run time and turn it into milliseconds
    runTime = int(time.time() * 1000)

    #get the params passed and the base params
    paramspassed, dirname = readParamsPassed(homedirectory, superParams, defaulttrainerparamspassed)

    #simple evaluator parameters that will be used to setup a base param file in case this is a single cryptoTrainer run
    evaluatorparams = PARAMETERS

    #initialize (or check that they are) the directories for storing and training
    #we use the default trainer params because they are changed enough for the initialization to work)
    initdirectories(paramspassed, superParams, dirname, evaluatorparams)
    initdirectories(paramspassed, superParams, dirname, evaluatorparams, typedirec='training')

    # the directory for the corresponding storage space for this evaluator and trainer
    storagedirectory = "{}/{}/{}/{}/{}/{}/{}/".format(dirname, 'storage', paramspassed['website'], paramspassed['day'],
                                                      paramspassed['hour'],
                                                      paramspassed['min'], paramspassed['originalid'])
    #training directory corresponding to this trainer file (houses evaluator files)
    direc = "{}/{}/{}/{}/{}/{}/{}/".format(dirname, 'training', paramspassed['website'], paramspassed['day'], paramspassed['hour'],
                                        paramspassed['min'], paramspassed ['idnum'])

    #training directory corresponding to this trainer file (houses the used trainer param file)
    trainingdirec = "{}/{}/{}/{}/{}/{}/".format(dirname, 'training', paramspassed['website'], paramspassed['day'], paramspassed['hour'],
                                        paramspassed['min'])

    # makes the directorys in the path variable if they do not exist
    pathlib.Path(storagedirectory).mkdir(parents=True, exist_ok=True)
    # read the parameters used by this trainer from the training directory
    baseparams = readParamPickle(trainingdirec, "{}superparam.pkl".format(paramspassed['idnum']))

    # ensure that baseparams have the correct number of classes and variations since they are stored in the superParams passed
    # to readParamsPassed
    baseparams['classes'] = superParams['classes']
    baseparams['variations'] = superParams['variations']

    #directory name where the log file is stored
    logdirectory = direc + 'trainerlogs/'

    #name of the directory log file
    logfilename = 'trainer.log'

    #setup up the log file for this trainer
    setUpLog(logdirectory, logfilename)

    #get the stored evaluator parameters relevant to this trainer from storage
    params = readParamPickle(storagedirectory, '{}baseparams.pkl'.format(paramspassed['evalID']))

    #ensure that the shared parameters that the trainer file has are the same as the evaluator file serving as its
    #base for all future trades
    checksharedparams(baseparams, params, paramspassed, storagedirectory)

    #setup a reference parameter file to edit
    writeParamPickle(params, direc, 'baseparams.pkl')

    #the absolute max and min % returned by a bot in any class
    absolute_Max = 0
    absolute_Min = 0

    # store the multiple processes
    for classnum  in range(int(baseparams['classes'])):
        #read the newly updated stored parameters
        params = readParamPickle(direc, 'baseparams.pkl')

        typeOfRandom = 3
        current_Max = -10000
        current_Min = 10000
        count = 0
        variationNum = 0.0
        minInDay = 1440.0

        #make a list of subprocesses that will act as our bots
        procs = createBots(baseparams, classnum)

        #set the best parameters to be whatever the current value for params is
        #if this is the first run then it will be the base params and thereafter it will be whatever bot was best
        #in the previous class of bots
        bestparams = params

        # randomizes parameters and runs different instances of the bot using the different starting parameters
        for proc in procs:
            reform = ''
            # randomize parameters and send the bot their class and variation num
            params = randomizeParams(params, typeOfRandom, baseparams, paramsthatcanbecombined)

            params['CLASS_NUM'] = classnum
            params['VARIATION_NUMBER'] = int(variationNum)

            # make the max cycles equal to the number of days of the interval in hours
            params['MAX_CYCLES'] = (params['INTERVAL_TO_TEST'] / minInDay) * 24.0

            # reset typeOfRandom so that every 50th run we use a special set of randomizers
            if(count % 50 == 0):
                typeOfRandom = 1
            if(count % 50 != 0):
                typeOfRandom = 0

            # store parameters and other variables in pickle files for this bot
            pickleInput(params, paramspassed, dirname)

            # make one bot run with the input stream of runtime, mode, directory path, classnum, and variationum
            out = proc.communicate(input="{} {} {} {} {} {} {} {} {} {}".format(paramspassed['directoryprefix'],
                                                                             paramspassed['website'], paramspassed['day'],
                                                                       paramspassed['hour'], paramspassed['min'],
                                                                       params['CLASS_NUM'], params['VARIATION_NUMBER'],
                                                                       paramspassed['idnum'], paramspassed['lossallowed'],
                                                                             paramspassed['startmoney']))

            #the standard output from the subprocess
            evaluatoroutput = out[0]

            #the standard error from the subprocess
            evaluatorerror = out[1]

            #build the directory string for the parameter dictionary
            directory = buildDirectory(params, paramspassed, dirname, typedirec='training')

            #get the parameter file from the recently finished evaluator bot
            params = readParamPickle(directory
                                                 ,'{}param.pkl'.format(params['VARIATION_NUMBER']))

            #store the percentage change from the money started with to the money ended with
            cumulativePerentChangeStore = calcPercentChange(params['START_MONEY'], params['END_MONEY'])


            #add the cumulative percent change of the current bot to the total % returned
            valuesrecorded.update({'totalbotreturn': valuesrecorded['totalbotreturn'] + cumulativePerentChangeStore})

            #add the change store into the list of returns
            returns.append(cumulativePerentChangeStore)

            # add up the number of positive bots
            if (cumulativePerentChangeStore > 0.0):
                valuesrecorded.update({'numposbots': valuesrecorded['numposbots'] + 1})

            #add up the number of negative bots
            if(cumulativePerentChangeStore < 0.0):
                valuesrecorded.update({'numnegbots': valuesrecorded['numnegbots'] + 1})

            # if the cumulative Percent Stored is greater than the current Max store it and the parameters it was from
            if (cumulativePerentChangeStore >= current_Max and params['CYCLES'] > baseparams['MIN_CYCLES']):

                current_Max = cumulativePerentChangeStore
                bestparams = params
                newParamCount += 1

                #if the current maximum % is higher than the absolute one
                #or if this is the first bot of the first class
                if current_Max > absolute_Max or (count == 0 and classnum == 0):
                    absolute_Max = current_Max

            # if the cumulative Percent Stored is less than the current Min store it and the parameters it was from
            if (cumulativePerentChangeStore <= current_Min and params['CYCLES'] > baseparams['MIN_CYCLES']):
                current_Min = cumulativePerentChangeStore

                #if the current minimum % is higher than the absolute one
                #or if this is the first bot of the first class
                if current_Min < absolute_Min or (count == 0 and classnum == 0):
                    absolute_Min = current_Min


            #load the stored base parameters for this class before the next variation is made
            params = readParamPickle(direc, "baseparams.pkl")
            variationNum += 1
            #add up the number of total bots
            valuesrecorded.update({'numbots': valuesrecorded['numbots'] + 1})

        count += 1
        logging.info('Current Max: {}'.format(current_Max))

        for z in procs:
            z.wait()

        # rewrite the parameter file with the final Dict
        writeParamPickle(bestparams, direc, 'baseparams.pkl')

    #set the last max recorded as the best bot % returned
    valuesrecorded.update({'bestbotreturn': absolute_Max})

    #set the last min recorded as the worst bot % returned
    valuesrecorded.update({'worstbotreturn': absolute_Min})

    #update the params passed with the calculated values relating to the success/failure of the bots
    baseparams = updateParams(baseparams, superParams, valuesrecorded)

    #update the original training "super param" file
    writeParamPickle(baseparams, trainingdirec,'{}superparam.pkl'.format(paramspassed['idnum']))



if __name__ == "__main__":
    main()
