# Copyright (c) 2018 A&D
# Supertrainer runs multiple trainers for classes of bots. Each trainer uses some
# different parameters to run that are common between bots in a class

import os
import pathlib
import pickle as pkl
import sys
import random
import logging
from Generics import PARAMETERS, priceSymbols, modes, websites, superParams, unchangedSuperParams, minSuperFiles, \
    defaultsuperparamspassed, specialSuperParams, specialRange, nonnegorzero, minEvaluatorFiles, calcPercentChange, addRandVal\
    , numFiles, nonnegative
from subprocess import Popen, PIPE



#setup the log file for this
def setUpLog(directory, filename):
    logging.basicConfig(filename=directory+filename, level='DEBUG')

# grabs the specified param file by the website, day, and id number that
# correspond to it


def grabParamFile(directory, picklefilename):
    """
    :param directory: the directory where the file is
    :param picklefilename: the pickle file name
    :return: the param dict
    """

    # makes the directorys in the path variable if they do not exist
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
    with open("{}/{}".format(directory, picklefilename), "rb") as pickle_in:
        paramDict = pkl.load(pickle_in)

    return paramDict

# write parameters to a file
# if no id is provided it will overwrite the first one


def writeParamPickle(paramDict, directory, picklefilename):
    """
    :param paramDict: the parameter dictionary to write
    :param directory: the directory desired to be written to
    :param picklefilename: the name of the pickleifile
    :return:
    """

    # makes the directorys in the path variable if they do not exist
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
    with open("{}/{}".format(directory, picklefilename), "wb") as pickle_out:
        pkl.dump(paramDict, pickle_out)

# reads the parameters passed from the script running this file
# will specify what website is being used and what the day is


def readParamsPassed(dirname):
    """
    :param dirname: the base directory relative to the file system
    :return: dicitonary of parameters passed from the file running that determine how the supertrainer will train
    and the true relative directory that accounts for which file is being run
    """

    if sys.argv[1] == "SuperTrainer": #parameters have been passed through console or run configuration (i.e. this is run on its own)
        returndict = {'directoryprefix': sys.argv[1],'website': sys.argv[2], 'day': sys.argv[3], 'numsessions': int(sys.argv[4]), 'hour': int(sys.argv[5]),
                      'min': int(sys.argv[6]), 'oldidnummax': int(sys.argv[7]), 'lossallowed': int(sys.argv[8])}

        #true directory accounts for what script is running the entire set of scripts
        truedirectory = "{}/{}/".format(dirname, sys.argv[1])
    elif len(sys.argv) != 3: #there are no paramters passed so use default
        returndict = defaultsuperparamspassed

        #true directory accounts for what script is running the entire set of scripts
        truedirectory = "{}/SuperTrainer/".format(dirname)
    else: #the parameters have been passed from another script that is running this one
        returndict = {}
        #loop through each line of the passed values
        for line in sys.stdin:
            if line != '': #only count the lines that have text
                paramvalues = line.split() #split the line into strings based on the spaces between each value
                count = 0
                for key, value in defaultsuperparamspassed.items(): #loop through the default param dict
                    returndict.update({key: paramvalues[count]}) #assign the values in order
                    count += 1

        truedirectory = "{}/{}/".format(dirname, returndict['directoryprefix'])

    return returndict, truedirectory



# returns the name of the directory where the desired parameter file is located


def getDirectory(website, day, hour, min, relativedirectory, typedirec='storage'):
    """
    :param day: the day of the week that the supertrainer was trained on
    :param website: the website that the supertrainer was trained on
        :param hour: the hour of the test
    :param min: the minute the test was run
    :param relativedirectory: the relative directory
    :param typedirec: the type of directory the param file will be stored in
    :return:
    """
    directory = "{}{}/{}/{}/{}/{}/".format(relativedirectory, typedirec, website, day, hour, min)
    # makes the directorys in the path variable if they do not exist
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

    return directory

#set up an array of subprocesses to run separate instances of CryptoTrainer
def setUpCryptoTrainerBots(botnum):
    """
    :param: botnum: number of processes we want to have for this run
    :return: an array of subprocesses
    """
    procs = []
    # creates botnum amounts of processes
    for j in range(botnum):
        proc = Popen([sys.executable, 'CryptoTrainer.py', '{}in.txt'.format(j), '{}out.txt'.format(j)], stdout=PIPE,
                     stdin=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True)
        procs.append(proc)
    return procs

#run the bots
def runBots(procs, paramspassed, idnummax, relativedirectory):
    """
    :param procs: the array of subprocesses
    :param paramspassed: the parameters passed to this superTrainer
    :param idnummax: the highest idnumber we can grab to use
    :param relativedirectory: the relative directory
    :return: the dictionary of trainers and their evaluators that got recently trained
    """
    numprocs = 0

    #dicitonary that has each trainerid : evaluatorid to indicate which have been trained recently
    recentlytrained = {}

    # randomizes parameters and runs different instances of the bot using the different starting parameters
    for proc in procs:


        ############################SETUP THE BOT AND TRAINING DIRECTORY ##############################################
        # if we exceed the number of old parameter files we want to grab we randomly pick one and randomize it
        if (numprocs > paramspassed['oldidnummax']):
            while True:
                #get a random id number
                curridnum = int(random.uniform(0, 1) * idnummax)
                if(curridnum != idnummax):
                    break

            #the directory to look in for a param file to randomize
            storagedirectory = getDirectory(paramspassed['website'], paramspassed['day'], paramspassed['hour'],
                                             paramspassed['min'], relativedirectory)

            #grab the param file we chose from the stored param files
            paramstorandomize = grabParamFile(storagedirectory, '{}superparam.pkl'.format(curridnum))

            #randomize it
            paramstouse = randomizeParams(paramstorandomize)

            #directory to be used in writing the param pickle file below
            directory = getDirectory(paramspassed['website'], paramspassed['day'], paramspassed['hour'],
                                     paramspassed['min'], relativedirectory, typedirec='training')

            #write it to a new file in the training directory
            writeParamPickle(paramstouse, directory, '{}superparam.pkl'.format(numprocs))


            #the number of evaluator parameter files in the storage directory
            numevaluatorfiles = numFiles('{}/{}'.format(storagedirectory, curridnum))

            #generate a random id for the evaluator file that is not the number of total files
            while True:
                #get a random evaluator id number
                evaluatorusedid = int(random.uniform(0,1) * (numevaluatorfiles))
                if(evaluatorusedid != numevaluatorfiles):
                    break

        else: #otherwise we grab a random parameter file
            while True:
                #get a random id number
                curridnum = int(random.uniform(0, 1) * idnummax)
                if(curridnum != idnummax):
                    break

            # the directory to look in for a param file to randomize
            storeagedirectory = getDirectory(paramspassed['website'], paramspassed['day'], paramspassed['hour'],
                                             paramspassed['min'], relativedirectory)

            #grab the file with the related id from the storage set
            paramstouse = grabParamFile(storeagedirectory, '{}superparam.pkl'.format(curridnum))

            #directory to be used to write to the training directory
            directory = getDirectory(paramspassed['website'], paramspassed['day'], paramspassed['hour'],
                                     paramspassed['min'], relativedirectory, typedirec='training')

            #write it to a new file in the training directory
            writeParamPickle(paramstouse, directory, '{}superparam.pkl'.format(numprocs))

            # the number of evaluator parameter files in the storage directory
            numevaluatorfiles = numFiles('{}/{}'.format(storeagedirectory, curridnum))

            # generate a random id for the evaluator file that is not the number of total files
            while True:
                # get a random evaluator id number
                evaluatorusedid = int(random.uniform(0, 1) * (numevaluatorfiles))
                if (evaluatorusedid != numevaluatorfiles):
                    break

        ###############################START THIS BOT##################################################################
        #start this bot
        out = proc.communicate(
            input=("{} {} {} {} {} {} {} {} {}").format(paramspassed['directoryprefix'], paramspassed['website'], paramspassed['day'],
                                                   paramspassed['hour'], paramspassed['min'], numprocs, curridnum,
                                                   evaluatorusedid, paramspassed['lossallowed']))

        #add the trainer and evaluator id as a key: value pair where the value is a list of evaluator files that have
        # been trained because multiple versions of the same trainer can be used with different evaluator use ids
        if curridnum in recentlytrained:
            recentlytrained[curridnum].append(evaluatorusedid)
        else:
            recentlytrained.update({curridnum: []})
            recentlytrained[curridnum].append(evaluatorusedid)

        print("Bot number {} output: {}".format(numprocs, out))

        #######################################AFTER THE BOT IS RUN ####################################################
        #get the original storage trainer file
        storedtrainerparams = grabParamFile(storeagedirectory, '{}superparam.pkl'.format(curridnum))

        #get the trainer file used
        usedtrainerparams = grabParamFile(directory, '{}superparam.pkl'.format(numprocs))

        #get the original storage evaluator file
        storedevaluatorparams = grabParamFile('{}/{}'.format(storeagedirectory, curridnum),
                                               '{}baseparams.pkl'.format(evaluatorusedid))

        #get the associated evaluator file used
        usedevaluatorparams = grabParamFile('{}/{}'.format(directory, numprocs), 'baseparams.pkl')

        #compare the trainer to its original and replace the original file if it produced worse bots
        savetrainerparams = compareParams(storedtrainerparams, usedtrainerparams, type='trainer')

        #store the returned trainer parameters
        writeParamPickle(savetrainerparams, storeagedirectory, '{}superparam.pkl'.format(numprocs))

        #compare the evaluator to its original and replace the original file if it traded poorly
        saveevaluatorparams = compareParams(storedevaluatorparams, usedevaluatorparams, type='evaluator')

        #store the returned evaluator parameters
        writeParamPickle(saveevaluatorparams , '{}/{}'.format(storeagedirectory, curridnum),
                         '{}baseparams.pkl'.format(evaluatorusedid))

        logging.info(out)
        print(out)
        numprocs += 1

    for proc in procs:
        proc.wait()

    return recentlytrained

#compare the parameters of the trainer/evaluator files with their stored counterpart and if the new versions are better
#return those
def compareParams(storedparams, usedparams, type='trainer'):
    """
    :param storedparams: the parameters stored in the system
    :param usedparams: the parameters used in the training
    :param type: the type of parameters used (trainer or evaluator)
    :return: the parameters that produced better results
    """
    #if the stored and used parameters are the same return the stored params
    if storedparams == usedparams:
        return storedparams

    #use a specific comparison method if the type is identifiable
    if type == 'trainer':
        return compareTrainerParams(storedparams, usedparams)
    elif type == 'evaluator':
        return compareEvaluatorParams(storedparams, usedparams)
    else:
        logging.error("improper type")

#compare the trainer parameters with their stored counterparts to see which made better trading bots
def compareTrainerParams(storedparams, usedparams):
    """
    :param storedparams: the parameters stored in the system
    :param usedparams: the parametes used in the training
    :return: the parameters that produced more exact bots
    """

    #the number of categories the new trainer is better than the original trainer
    #used to determine if this trainer should be adopted
    numcheckpassed = 0

    #check if each of the check values is greater in the parameters used
    for key, value in storedparams.items():
        if usedparams[key] > storedparams[key]:
            numcheckpassed += 1

    #if the used parameters were better in the correct amount of categories
    if numcheckpassed >= storedparams['replacementvalue']:
        return usedparams

    return storedparams

#compare the evaluator parameters with their stored counterparts to see if it traded better
def compareEvaluatorParams(storedparams, usedparams):
    """
    :param storedparams: the parameters stored in the system
    :param usedparams: the parametes used in the training
    :return: the parameters that traded more effectively
    """

    #the percent change of the stored evaluator
    storedpercentchange = calcPercentChange(storedparams['START_MONEY'], storedparams['END_MONEY'])

    #the percent change of the used evaluator
    usedpercentchange = calcPercentChange(usedparams['START_MONEY'], usedparams['END_MONEY'])

    if usedpercentchange > storedpercentchange:
        return usedparams

    return storedparams

#initializes the directory with a min number of default version of parameters if there are none there
#as well as folders to hold the associated evaluator parameter files
def initparamdirectory(directory, currnumparamfiles, desirednumparamfiles,  paramstowrite):
    """
    :param directory:
    :param currnumparamfiles: number of files in the directory
    :param desirednumparamfiles: the desired number of parameter files in the directory
    :param paramstowrite: the parameter dictionary to write if we do not have the adequate number of files in the directory
    :return:
    """
    for idnum in range(desirednumparamfiles):
        if currnumparamfiles > idnum:
            continue
        # makes the directory to house the Trainer Parameter files for the different crytpoTrainers
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

        #if the directory path name is storage (training mode does not start with writing params because that is guaranteed
        # to happen when we start the training)
        if 'storage' in directory:
            print("writing params")
            writeParamPickle(paramstowrite, directory,  '{}superparam.pkl'.format(idnum))


        #makes the directory to house the related Evaluator Parameter files for the different evaluators
        pathlib.Path("{}/{}".format(directory, idnum)).mkdir(parents=True, exist_ok=True)

        #makes the directory for any log files run related to the SuperTrainer
        pathlib.Path("{}/supertrainerlogs".format(directory)).mkdir(parents=True, exist_ok=True)
        #makes the directory for any log files run related to the Trainer
        pathlib.Path("{}/{}/trainerlogs".format(directory, idnum)).mkdir(parents=True, exist_ok=True)


#initilaize the directory with the minimum number of evaluator param files if there are not the desired amount
def setupevaluatordirectory(directory, currnumevaluatorfiles, desirednumevaluatorfiles, paramstowrite):
    """
    :param directory: the directory where the evaluator files are
    :param currnumevaluatorfiles: the current number of evaluator files
    :param desirednumevaluatorfiles: the desired number of evaluator files
    :param paramstowrite: the parameters to be written if there are not enough files in the system
    :return:
    """

    for idnum in range(desirednumevaluatorfiles):
        if(currnumevaluatorfiles  < idnum + 1):
            writeParamPickle(paramstowrite, "{}".format(directory), '{}baseparams.pkl'.format(idnum))

#returns true if the parameter is not listed as a special one
def checkSpecial(keyname):
    """
    :param keyname: name of the dict key to check
    :return: true if it is in the dictionary
    """
    for group in specialSuperParams:
        for name in group:
            if keyname == name:
                return True

    return False

#randomize the parameters passed of the given parameter dictionary
def randomizeParams(paramDict, rangeVals = 100):
    """
    :param paramDict: the dictionary of the parameters to be changed
    :param rangeVals: the range of values to choose from
    :return: the dictionary of parameters after they are randomized
    """

    #go through the paramDict and randomize any that are not supposed to be unchanged
    for key, value in paramDict.items():
        randVal = int(random.uniform(-1, 1) * rangeVals)

        # if the current parameter does not need special changes
        # and it is not marked as unchanging
        if key not in unchangedSuperParams and checkSpecial(key) == False:
            if key in addRandVal:
                paramDict[key] += randVal
            else:
                paramDict[key] = randVal

    groupnum = 0
    for group in specialSuperParams: #change each group of special parameters together
        # if this parameter is allowed to be non-negative or zero
        if group[0] not in nonnegorzero and group[0] not in nonnegative:
            randVal = int(random.uniform(-1, 1) * specialRange[groupnum])
        #if these special parameters can be zero but not negative
        elif group[0] in nonnegative:
            randVal = int(random.uniform(0, 1) * specialRange[groupnum])
        #if these special parameters cannot be negative or zero
        else:
            randVal = int(random.uniform(0, 1) * specialRange[groupnum] + 1)

        #go through each parameter key in that special param group list and change all the values by the same amount
        for paramkey in group:
            # if we identify that we only want to add to this random value instead of just setting the value to the rand value
            if group[0] in addRandVal:
                paramDict[paramkey] += randVal
            else:
                paramDict[paramkey] = randVal
        #advance to the next group
        groupnum+=1

    return paramDict

def main():
    # setup the relative file path
    homedirectory = os.path.dirname(os.path.realpath(__file__))

    #read in the params passed and get the true directory (the directory that includes a prefix of what script is
    # running this stack of scripts)
    paramspassed, dirname = readParamsPassed(homedirectory)

    #the stprage directory for the set of trainer params
    directory = getDirectory(paramspassed['website'], paramspassed['day'], paramspassed['hour'], paramspassed['min'],
                             dirname)
    #the training directory for the set of trainer params
    trainingdirectory = getDirectory(paramspassed['website'], paramspassed['day'], paramspassed['hour'],
                                     paramspassed['min'], dirname, typedirec='training')


    #the number of parameter files in both the training and the storage directories
    numparamfiles = numFiles(directory)
    numtrainingparamfiles = numFiles(trainingdirectory)


    #initialize the paramdirectory for storage and training
    initparamdirectory(directory, numparamfiles, minSuperFiles, superParams)
    initparamdirectory(trainingdirectory, numtrainingparamfiles, paramspassed['numsessions'], superParams)

    #update the number in case more param files were added
    numparamfiles = numFiles(directory)

    #loop through all the trainer param folders and make sure they have the correct number of
    #evaluator param files
    for id in range(numparamfiles):
        #the directory for the trainer param that houses the evlautor params
        evaluatorparamdirectory = '{}/{}'.format(directory, id)

        #the number of evaluator files in the storage directory
        numevaluatorparamfiles = numFiles(evaluatorparamdirectory)

        #initialize the evaluator dictionary with additional param files
        setupevaluatordirectory(evaluatorparamdirectory, numevaluatorparamfiles, minEvaluatorFiles, PARAMETERS)


    #log directory
    superlogdirectory = trainingdirectory + '/supertrainerlogs/'
    
    #log file name
    logfilename = "supertrainer.log"
    
    #set up the logs used for this file
    setUpLog(superlogdirectory, logfilename)

    #setup the right number of processes to numsessions number of training bots
    procs = setUpCryptoTrainerBots(paramspassed['numsessions'])

    #run the bots and get a dictionary identifying which trainer/evaluator files have been recently trained
    recentlytrained = runBots(procs, paramspassed, numparamfiles, dirname)

    #update the stored pickle file for the recently trained parameters
    writeParamPickle(recentlytrained, directory, "recentlytrained.pkl")


if __name__ == "__main__":
    main()
