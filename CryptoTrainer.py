# Copyright (c) 2018 A&D
# Auto trading tester that runs multiple versions of the trader with different parameters


import sys
import random
import time
import os
import pathlib
import pickle
import logging


from subprocess import Popen, PIPE
from Generics import UNCHANGED_PARAMS, superParams, defaulttrainerparamspassed, PARAMETERS, priceSymbols, \
    calcPercentChange, listparms, removeEmptyInnerLists, paramsthatcanbecombined, numFiles, \
    SPECIAL_PARAMS,  dictparams, SPECIAL_PARAMS_RANGE_OF_RANDOMIZATION

from PriceSymbolsUpdater import getStoredSymbols


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



# randomizes the parameters before sending them to a subprocess
# typeOfRandom determines what kinds of randomization occurs
# type 0 means normal, type 1 means larger range of randomization
# type 3 means none

def randomizeParams(paramDict, typeOfRandom, baseparams, combinableparams, specialparameterslist,
                    specialparametersrandomizationranges, paramspassed, homedirectory):
    """
    :param paramDict: the parameter dictionary
    :param typeOfRandom: the integer corresponding to the way to randomize
    :param baseparams: the parameters passed to the trainer
    :param combinableparams: the list of parameters that can be combined to form new parameters
    :param specialparameterslist: the list of the lists of parameters that have special ranges to be randomized with
    :param specialparametersrandomizationranges: the list of ranges that each special parameter list of parameters
        is randomized using.
    :param paramspassed: the parameters passed to this file
    :param homedirectory: the primary directory of the file
    :return:
    """

    ####VALUES EXPLAINING THE PASSED TYPES OF RANDOM#################
    keepdefaultparams = 3
    usesmallerrangerandom = 0
    uselargerangerandom = 1

    ####################VALUES EXPLAINING THE KEYCHECK################
    isaspecialparameter = 4
    isalistparameter = 3
    isadictparameter = 2
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
            #if the parameter is a dict
            elif check == isadictparameter:

                randomizeParamsDict(paramDict, baseparams, key, combinableparams, 'lower', paramspassed, homedirectory)

            #if the parameter is a special parameter with its own range value
            elif check == isaspecialparameter:

                randomizeSpecialParam(paramDict, key, specialparameterslist, specialparametersrandomizationranges,
                                      randcheck, baseparams['lowercheckthreshold'])

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

            # if the parameter is a dict
            elif check == isadictparameter:

                randomizeParamsDict(paramDict, baseparams, key, combinableparams, 'upper', paramspassed, homedirectory)

            #if the param is a special param with its own range values
            elif check == isaspecialparameter:

                randomizeSpecialParam(paramDict, key, specialparameterslist, specialparametersrandomizationranges,
                                      randcheck, baseparams['uppercheckthreshold'])

            # if the key is not in the unchangeable params list and
            # the random number generated clears the threshold for modifying it
            elif(check != isanunchangeableparameter and randcheck > baseparams['uppercheckthreshold']):
                randVal = paramDict[key]
                randVal += (random.uniform(-1, 1) * baseparams['bigrange']) + baseparams['lowofsecondrange']
                paramDict[key] = randVal


    return paramDict


#looks to see if the passsed parameter key is one of the kinds that requires a non-default kind of randomizatiom
def keyCheck(key):
    """
    :param key: param dictionary key
    :return:
    """

    if key in UNCHANGED_PARAMS: #check if the key is in the list of unchanageable parameters
        return 1

    #check if the key is in the list of dictionary parameters
    if key in dictparams:
        return 2

    if key in listparms: #check if this is a list parameter
        return 3

    #loop through the lists of the list of lists of parameters to modify by specific ranges
    for list in SPECIAL_PARAMS:
        if key in list:
            return 4

    return 0


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

        #remove the extra combined parameters if we have too many
        removeextracombinedparams(params, maxcombinedparams)

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
            while(modifiyparamdecision > stopchangingparamsthreshold and len(listofcombinedparams) != 0):
                #if we choose to remove a parameter
                if modifiyparamdecision <= removeparamsthreshold:

                    indexofparamtoremove = len(listofcombinedparams)

                    while indexofparamtoremove == len(listofcombinedparams):
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

#remove the combined parameter lists starting from the end if there are too many
# mirror the removes in the combined parameter modifier list
def removeextracombinedparams(params, maxcombinedparams):
    """
    :param params: parameters used by the evaluator bots to trade
    :param maxcombinedparams: the maximum number of combined parameters
    :return:
    """

    while(len(params['COMBINED_PARAMS']) > maxcombinedparams):
        #remove the last list of combined parameters
        params['COMBINED_PARAMS'] = params['COMBINED_PARAMS'][:-1]

        #remove the corresponding modifier from the list of modifiers
        params['COMBINED_PARAMS_MODIFIERS'] = params['COMBINED_PARAMS_MODIFIERS'][:-1]


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

#randomize the parameter that is a dictionary by selecting the right dictionary randomization function
def randomizeParamsDict(params, baseparams, key, normaparamslist, upperorlowervalues, paramspassed, homedirectory):
    """
    :param params: the parameter dictionary used by the evaluators
    :param baseparams: the base params for the trainer
    :param key: current parameter key looked at (of params)
    :param normaparamslist: the normal parameter list
    :param upperorlowervalues: whether these are upper or lower values
    :param paramspassed: the parameters passed to this file
    :param homedirectory: the primary directory of the file
    :return:
    """


    if key == 'PARAMS_CHECKED_FOR_MINIMUM_VALUES':
        randomizeParamDictofMinimumParameterValues(params, baseparams, normaparamslist, upperorlowervalues)
    elif key == 'CRYPTO_SCORE_MODIFIERS':
        randomizeParamDictofCryptoScoreModifiers(params, baseparams, upperorlowervalues, paramspassed, homedirectory)
    else:
        logging.error("Not a valid key {}".format(key))
        quit(-1)

#randomize the key, value pairs for the dictionary of parameter minimum values
def randomizeParamDictofMinimumParameterValues(params, baseparams, normalparamslist, upperorlowervalues):
    """
    :param params: the parameter dictionary used by the evaluator bots to trade with
    :param baseparams: the base parameters used by this trainer
    :param normalparamslist: the list of parameters considered normal
    :param upperorlowervalues: whether we are changing this parameter dictionary upper (bigger) or lower (smaller)
        ranges of values for both the decision to change each value and the amount to change each value by
    :return:
    """

    #ensure that the parameter dictionary of minimum parameters values is not too long
    checkparamdictofminumumsisappropriatelength(params, baseparams)

    #only run the code to choose a new parameter to add as a minimum value if there is room for another parameter
    if len(params['PARAMS_CHECKED_FOR_MINIMUM_VALUES']) < baseparams['maxparameterstouseasminimums']:

        #decide if we will grab a combined parameter or a normal parameter to use as a minimum
        nameofparamtype = normalparameterorcombinedparameter(params)

        addanewparametertouseasaminimum(params, normalparamslist, nameofparamtype)

    #loop through the parameters used as minimum values and randomize them
    randomizethevaluesofthedictionaryofdatatypeminimumvalues(params, baseparams, upperorlowervalues)

    #remove a parameter used as a minimum value
    removeparameterusedasaminimum(params)

#removes the last parameter key, value pair if the dictionary has more pairs than is allowed for this trainer
def checkparamdictofminumumsisappropriatelength(params, baseparams):
    """
    :param params: the parameter dictionary used by the evaluator bots to trade
    :param baseparams: the base parameter dictionary used by this trainer
    :return:
    """

    while(len(params['PARAMS_CHECKED_FOR_MINIMUM_VALUES']) > baseparams['maxparameterstouseasminimums']):

        #pick a key to be removed
        keychosentoberemoved = choosekeyofdicttoremove(params['PARAMS_CHECKED_FOR_MINIMUM_VALUES'])

        #remove the key from the dictionary
        params['PARAMS_CHECKED_FOR_MINIMUM_VALUES'].pop(keychosentoberemoved)

#returns a key in the dictionary to be removed
def choosekeyofdicttoremove(dict):
    """
    :param dict: the dictionary
    :return: the removed key
    """

    #generate a random key index to be removed
    randomkeyindex = int(random.uniform(-1,1) * len(dict))

    #the counter for the current index
    currkeyindex = 0

    #loop through the dictionary until you reach the key
    for key, value in dict.items():

        if currkeyindex == randomkeyindex:
            return key

        currkeyindex += 1

#decide and return whether a combined parameter type or a normal parameter type will be used for the next
#minimum parameter value
def normalparameterorcombinedparameter(params):
    """
    :param params: the parameter dictionary used by the evaluators
    :return: whether we are using normal parameters or combined parameters
    """

    #if there are no combined parameters we use normal parameters by default
    if len(params['COMBINED_PARAMS']) == 0:
        return 'NORMAL_PARAMS'
    #otherwise we flip a coin
    else:
        usenormalparam = 0
        usecombinedparam = 1

        #flip a coin
        paramtypetousenumber = int(random.uniform(0, 2))

        if paramtypetousenumber == usenormalparam:
            return 'NORMAL_PARAMS'
        elif paramtypetousenumber == usecombinedparam:
            return 'COMBINED_PARAMS'
        else:
            logging.error("Not a valid decision for a param type to use {}".format(paramtypetousenumber))
            quit(-1)

#add a new parameter to the dictionary of parameters used as minimum values from either the combined parameter list
# or the normal parameter list
def addanewparametertouseasaminimum(params, normalparameterlist, listtypetogetparamfrom):
    """
    :param params: the evaluator parameters used by the bots to trade
    :param normalparameterlist: the list of the parameters considered normal parameters
    :param listtypetogetparamfrom: the decision about which type of list to add a parameter from
    :return:
    """

    if listtypetogetparamfrom == 'NORMAL_PARAMS':
        addanormaparametertouseasaminimum(params, normalparameterlist)

    elif listtypetogetparamfrom == 'COMBINED_PARAMS':
        addacombinedparametertouseasaminimum(params)

    else:
        logging.error("Not a valid kind of parameter {}".format(listtypetogetparamfrom))
        quit(-1)

#select a parameter from the list of normal parameters and add it to the dictionary of parameters used as minimum values
def addanormaparametertouseasaminimum(params, normalparameterlist):
    """
    :param params: the evaluator parameters used by the bots to trade
    :param normalparameterlist: the list of normal parameters
    :return:
    """

    #generate an index for the normal parameter to add
    indexofnormalparameter = int(random.uniform(0,1) * len(normalparameterlist))

    #get the key (name) for this normal parameter
    nameofnormalparameter = normalparameterlist[indexofnormalparameter]

    #add the normal parameter to the dictionary of parameters used as minimum values
    params['PARAMS_CHECKED_FOR_MINIMUM_VALUES'].update({nameofnormalparameter: 0.00001})


#select a parameter from the list of combined parameters and add it to the dictionary of parameters used
# as minimum values
def addacombinedparametertouseasaminimum(params):
    """
    :param params: the dictionary of parameters used by the evaluators to trade
    :return:
    """

    #generate the index of the combined parameter to add
    indexofcombinedparameter = int(random.uniform(0,1) * len(params['COMBINED_PARAMS']))

    #add the normal parameter to the dictionary of parameters used as minimum values
    params['PARAMS_CHECKED_FOR_MINIMUM_VALUES'].update({indexofcombinedparameter: 0.00001})

#loop through the dictionary of parameter data types used as minimum values and randomize each value
def randomizethevaluesofthedictionaryofdatatypeminimumvalues(params, baseparams, upperorlowervalues):
    """
    :param params: the parameter dictionary used by the evaluators to trade
    :param baseparams: the base parameter dictionary used by this trainer
    :param upperorlowervalues: determine whether the ranges used to generate random numbers
        will use the upper or lower ranges as detailed in the baseparams
    :return:
    """

    for parameterdatatype, minimumvaluefordatatype in params['PARAMS_CHECKED_FOR_MINIMUM_VALUES'].items():

        if upperorlowervalues == 'upper':
            randomizevaluewithcorrectrandomizationtype(params, baseparams['randcheckrangetwo'],
                                                       baseparams['uppercheckthreshold'], baseparams['bigrange'],
                                                       parameterdatatype)
        elif upperorlowervalues == 'lower':
            randomizevaluewithcorrectrandomizationtype(params, baseparams['randcheckrangeone'],
                                                       baseparams['lowercheckthreshold'], baseparams['smallrange'],
                                                       parameterdatatype)
        else:
            logging.error("Not a valid type of randomization {}".format(upperorlowervalues))

#randomizes the parameter datatype for the dictionary of data types to use as minimum values using the correct
# ranges according to the whether they are in the bigger range (upper) or the smaller range (lower)
def randomizevaluewithcorrectrandomizationtype(params, checkrange, checkthreshold, rangeofrandomvaluestogenerate,
                                               nameofparameterdatatypetoalter):
    """
    :param params: the parameters used by the evaluator bots
    :param checkrange: the range of random values generated to use to see if the current parameter should be changed
    :param checkthreshold: the threshold to check if the parameter should be changed
    :param rangeofrandomvaluestogenerate: the range of values to generate the number to modify the current param
    :param nameofparameterdatatypetoalter: the name of the parameter data type to change
    :return:
    """

    randcheck = int(random.uniform(0,1) * checkrange)

    if randcheck > checkthreshold:

        #generate a random value to alter the current parameter value by (we divide the range by itself here
        # because we only want to change the minimums by tiny amounts)
        randomvaluetochangetheparametervalue = int(random.uniform(-1,1) *
                                                   rangeofrandomvaluestogenerate/rangeofrandomvaluestogenerate)

        #get the value fo the current parameter from the dictionary of datatypes used as minimums
        valueofcurrentparameter = params['PARAMS_CHECKED_FOR_MINIMUM_VALUES'][nameofparameterdatatypetoalter]

        #add the random value and the current value together
        randomvalueplusthecurrentparamvalue = randomvaluetochangetheparametervalue + valueofcurrentparameter

        #update the current parameter
        params['PARAMS_CHECKED_FOR_MINIMUM_VALUES'].update\
            ({nameofparameterdatatypetoalter: randomvalueplusthecurrentparamvalue})


#remove a parameter used as a minimum
def removeparameterusedasaminimum(params):
    """
    :param params: the parameter dictionary used by the evaluators to trade
    :return:
    """

    #if there is only one minimum parameter left do nothing
    if len(params['PARAMS_CHECKED_FOR_MINIMUM_VALUES']) <= 1:
        return

    removeparam = 1
    donothing = 0

    #flip a coin
    decisiononwhethertoremove = int(random.uniform(0,2))

    if decisiononwhethertoremove == removeparam:
        keytoremove = choosekeyofdicttoremove(params['PARAMS_CHECKED_FOR_MINIMUM_VALUES'])

        params['PARAMS_CHECKED_FOR_MINIMUM_VALUES'].pop(keytoremove)

    elif decisiononwhethertoremove == donothing:
        return
    else:
        logging.error("Not a valid remove decision {}".format(decisiononwhethertoremove))
        quit(-1)

#randomize the dictionary of crypto score modifiers
def randomizeParamDictofCryptoScoreModifiers(params, baseparams, upperorlowervalues, paramspassed, homedirectory):
    """
    :param params: the parameters used by the evaluator bots
    :param baseparams: the base parameters used by this trainer
    :param upperorlowervalues: whether these are using the upper or lower range of values for randomization
    :param paramspassed: the parameters passed to this file
    :param homedirectory: the primary directory of the file
    :return:
    """

    #check to make sure all the cryptos are represented in this dictionary
    verifyintegrityoflistofcryptosymbolmodifiers(params['CRYPTO_SCORE_MODIFIERS'], paramspassed, homedirectory)

    for currencyname, currencyscoremodifier in params['CRYPTO_SCORE_MODIFIERS'].items():
        if 'upper' == upperorlowervalues:
            randomvalue = random.uniform(-1,1) * baseparams['bigrange']
        else:
            randomvalue = random.uniform(-1,1) * baseparams['smallrange']

        newvalue = currencyscoremodifier + randomvalue

        params['CRYPTO_SCORE_MODIFIERS'].update({currencyname: newvalue})

#adds any cryptos to the list of score modifiers if they are not already present
def verifyintegrityoflistofcryptosymbolmodifiers(dictofcryptosymbolsandtheirmodifiers, paramspassed, homedirectory):
    """
    :param dictofcryptosymbolsandtheirmodifiers: the dictionary of crypto symbols and their modifiers
    :param paramspassed: the parameters passed to this file
    :param homedirectory: the primary directory of the file
    :return:
    """

    storedsymbolsdict = getStoredSymbols(paramspassed['website'], homedirectory, list=False)

    for currencyname, symbol in storedsymbolsdict.items():
        if symbol not in dictofcryptosymbolsandtheirmodifiers:
            dictofcryptosymbolsandtheirmodifiers.update({symbol: 1.0})


#randomizes the special parameters. each has a special range corresponding to it.
def randomizeSpecialParam(params, paramkey, specialparameterslist, specialparametersrandomizationranges, randcheck,
                          checkthreshold):
    """
    :param params: the parameter dictionary of parameters used by the evaluator bots
    :param paramkey: the key of the current parameter to change
    :param specialparameterslist: the list of the lists of parameters that have special ranges to be randomized with
    :param specialparametersrandomizationranges: the list of ranges that each special parameter list of parameters
        is randomized using.
    :param randcheck: the random value generated to determine if this parameter will be changed
    :param checkthreshold: the value that the randcheck must be higher than in order for this parameter to be altered
    :return:
    """

    #get the index of the special param
    indexofspecialparam = getindexofspecialparam(specialparameterslist, paramkey)

    #if the random value is higher than the threshold to change it
    if randcheck > checkthreshold:

        #get the current value
        currentvalueofparam = params[paramkey]

        #generate a random value
        randomvalue = (random.uniform(-1,1) * specialparametersrandomizationranges[indexofspecialparam])

        #add them together
        randomvalueaddedtocurrentvalueofparam = currentvalueofparam + randomvalue

        #reset the original parameter value
        params.update({paramkey: randomvalueaddedtocurrentvalueofparam})


#get the index of the passed param key in the special parameters list
def getindexofspecialparam(specialparameterslist, paramkey):
    """
    :param specialparameterslist: the list of lists of special parameters
    :param paramkey: the parameter key to find in the list
    :return:
    """
    indexinlist = 0

    for list in specialparameterslist:

        if paramkey in list:

            return indexinlist

        indexinlist += 1

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
                print("REWROTE SUPER PARAMS")
                #make the super param file for this trainer
                writeParamPickle(baseparams,directory,'{}superparam.pkl'.format(paramspassed['idnum']))

        # the storage directory to write the evaluator (base) params
        storagedirectory = "{}{}/".format(directory, paramspassed['originalid'])

        if numFiles(storagedirectory) == 0 and typedirec == 'storage':
            print("REWROTE PARAMS")
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

    try:
        #scale the percent changes to make the percentages relative to 1 trade per hour for a day timeframe
        scaleby = (baseparams['INTERVAL_TO_TEST']/baseparams['MAX_CYCLES'])/(defaultbaseparams['INTERVAL_TO_TEST']/
                                                                         defaultbaseparams['MAX_CYCLES'])
    except ZeroDivisionError:
        print("Normal interval {}".format(baseparams['INTERVAL_TO_TEST']))
        print("Normal max cycles {}".format(baseparams['MAX_CYCLES']))
        print("Default interval to test".format(defaultbaseparams['INTERVAL_TO_TEST']))
        print("Default interval to test".format(defaultbaseparams['MAX_CYCLES']))


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

        print("Class {}".format(classnum))

        #read the newly updated stored parameters
        params = readParamPickle(direc, 'baseparams.pkl')

        # make sure we verify the crypto score modifiers
        verifyintegrityoflistofcryptosymbolmodifiers(params['CRYPTO_SCORE_MODIFIERS'], paramspassed, homedirectory)

        print("params {}".format(params))

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
            params = randomizeParams(params, typeOfRandom, baseparams, paramsthatcanbecombined, SPECIAL_PARAMS,
                                     SPECIAL_PARAMS_RANGE_OF_RANDOMIZATION, paramspassed, homedirectory)

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

            print("Variation {}".format(variationNum))

            #the standard output from the subprocess
            evaluatoroutput = out[0]

            print("Output {}".format(evaluatoroutput))

            #the standard error from the subprocess
            evaluatorerror = out[1]

            print("Error {}".format(evaluatorerror))

            #build the directory string for the parameter dictionary
            directory = buildDirectory(params, paramspassed, dirname, typedirec='training')

            #get the parameter file from the recently finished evaluator bot
            params = readParamPickle(directory
                                                 ,'{}param.pkl'.format(params['VARIATION_NUMBER']))

            #store the percentage change from the money started with to the money ended with
            cumulativePerentChangeStore = calcPercentChange(params['START_MONEY'], params['END_MONEY'])

            #print("Made {}".format(cumulativePerentChangeStore))

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

            #print("Cycles {}".format(params['CYCLES']))

            # if the cumulative Percent Stored is greater than the current Max store it and the parameters it was from
            if (cumulativePerentChangeStore >= current_Max and params['CYCLES'] > baseparams['MIN_CYCLES']
                and params['NUM_BUYS'] != 0):

                current_Max = cumulativePerentChangeStore
                #print("Current Max {}".format(current_Max))

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
    writeParamPickle(baseparams, trainingdirec, '{}superparam.pkl'.format(paramspassed['idnum']))

    #if this is running a simulation store the evaluator parameters
    if paramspassed['directoryprefix'] == 'CryptoTrainer':
        #print("STORED")
        writeParamPickle(bestparams, storagedirectory, '{}baseparams.pkl'.format(paramspassed['evalID']))

    print("Final made {}".format(current_Max))
    print("Final money in best bot {}".format(bestparams['END_MONEY']))
    print("Final cycles used {}".format(bestparams['CYCLES']))
    print("Final buys {}".format(bestparams['NUM_BUYS']))
if __name__ == "__main__":
    main()
