# Copyright (c) 2018 A&D
# Supertrainer runs multiple trainers for classes of bots. Each trainer uses some
# different parameters to run that are common between bots in a class

import os
import pathlib
import pickle as pkl
import sys
import random
import logging
from Generics import PARAMETERS, priceSymbols, modes, websites, superParams, unchangedSuperParams, minSuperFiles, defaultsuperparamspassed, specialSuperParams, specialRange, nonnegorzero
from subprocess import Popen, PIPE

# setup the relative file path
dirname = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dirname + '/', '')


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


def readParamsPassed():
    """
    :return: dicitonary of parameters passed from the file running that determine how the supertrainer will train
    """

    if sys.argv[1] == "Alone":
        returndict = {'website': sys.argv[2], 'day': sys.argv[3], 'numsessions': int(sys.argv[4]), 'hour': int(sys.argv[5]), 'min': int(sys.argv[6]), 'oldidnummax': int(sys.argv[7])}
    else: #TODO replace with reading sys.stdin because this will be run from a separate file
        returndict = defaultsuperparamspassed

    return returndict

# returns the number of files in a directory
# is used to tell what the next idnum will be needed to add another parameter file
# path joining version for other paths


def numFiles(directory):
    """
    :param: directory of the supertrainer files so we can see how many there are
    :return:
    """
    # makes the directorys in the path variable if they do not exist
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
    return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])

# returns the name of the directory where the desired parameter file is located


def getDirectory(website, day, hour, min, typedirec='storage'):
    """
    :param day: the day of the week that the supertrainer was trained on
    :param website: the website that the supertrainer was trained on
        :param hour: the hour of the test
    :param min: the minute the test was run
    :param typedirec: the type of directory the param file will be stored in
    :return:
    """
    directory = "{}{}/{}/{}/{}/{}".format(filename, typedirec, website, day, hour, min)
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
def runBots(procs, paramspassed, idnummax):
    """
    :param procs: the array of subprocesses
    :param paramspassed: the parameters passed to this superTrainer
    :param idnummax: the highest idnumber we can grab to use
    :return:
    """
    numprocs = 0
    # randomizes parameters and runs different instances of the bot using the different starting parameters
    for proc in procs:
        # if we exceed the number of old parameter files we want to grab we randomly pick one and randomize it
        if (numprocs > paramspassed['oldidnummax']):
            #get a random id number
            curridnum = int(random.uniform(0, 1) * idnummax)

            #the directory to look in for a param file to randomize
            storeagedirectory = getDirectory(paramspassed['website'], paramspassed['day'], paramspassed['hour'], paramspassed['min'])

            #grab the param file we chose from the stored param files
            paramstorandomize = grabParamFile(storeagedirectory ,str(curridnum)+'superparam.pkl')

            #randomize it
            randomizeParams(paramstorandomize)

            #directory to be used in writing the param pickle file below
            directory = getDirectory(paramspassed['website'], paramspassed['day'], paramspassed['hour'], paramspassed['min'],
                                     typedirec='training')

            #write it to a new file in the training directory
            writeParamPickle(paramstorandomize, directory, str(numprocs)+'superparam.pkl')

        else: #otherwise we grab a random parameter file
            curridnum = int(random.uniform(0, 1) * idnummax)

            # the directory to look in for a param file to randomize
            storeagedirectory = getDirectory(paramspassed['website'], paramspassed['day'], paramspassed['hour'],
                                             paramspassed['min'])

            #grab the file with the related id from the storage set
            paramstouse = grabParamFile(storeagedirectory, str(curridnum) + 'superparam.pkl')

            #directory to be used to write to the training directtory
            directory = getDirectory(paramspassed['website'], paramspassed['day'], paramspassed['hour'], paramspassed['min'],
                                     typedirec='training')

            #write it to a new file in the training directory
            writeParamPickle(paramstouse, directory, str(numprocs)+'superparam.pkl')



        out = proc.communicate(
            input=("{} {} {} {} {} {}").format( paramspassed['website'], paramspassed['day'],
                                                       paramspassed['hour'], paramspassed['min'], numprocs, curridnum))

        #TODO finish changing it so it reads back the super param and param file and decides if it should overwrite any stored files
        logging.info(out)
        print(out)
        numprocs+=1
    for proc in procs:
        proc.wait()

#initializes the directory with 10 default version of parameters if there are none there
#as well as folders to hold the associated evaluator parameter files
def initparamdirectory(directory, currnumparamfiles, desirednumparamfiles, paramspassed):
    """
    :param directory:
    :param currnumparamfiles: number of files in the directory
    :param desirednumparamfiles: the desired number of parameter files in the directory
    :param paramspassed:
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
            writeParamPickle(superParams, directory, str(idnum) + 'superparam.pkl')
            writeParamPickle(PARAMETERS, "{}/{}".format(directory, idnum), 'baseparams.pkl')

        #makes the directory to house the related Evaluator Parameter files for the different evaluators
        pathlib.Path("{}/{}".format(directory, idnum)).mkdir(parents=True, exist_ok=True)

        #makes the directory for any log files run related to the SuperTrainer
        pathlib.Path("{}/supertrainerlogs".format(directory)).mkdir(parents=True, exist_ok=True)
        #makes the directory for any log files run related to the Trainer
        pathlib.Path("{}/{}/trainerlogs".format(directory, idnum)).mkdir(parents=True, exist_ok=True)


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
def randomizeParams(paramDict, rangeVals=100):
    """
    :param paramDict: the dictionary of the parameters to be changed
    :param rangeVals: the range of values to choose from
    :return:
    """

    #go through the paramDict and randomize any that are not supposed to be unchanged
    for key, value in paramDict.items():
        randVal = int(random.uniform(-1, 1) * rangeVals)

        # if the current parameter does not need special changes
        # and it is not marked as unchanging
        if key not in unchangedSuperParams and checkSpecial(key) == False:
            paramDict[key] = randVal

    groupnum = 0
    for group in specialSuperParams: #change each group of special parameters together
        if group[0] not in nonnegorzero: #if this parameter is allowed  to be non-negative or zero
            randVal = int(random.uniform(-1, 1) * specialRange[groupnum])
        else:
            randVal = int(random.uniform(0, 1) * specialRange[groupnum] + 1)
        for paramkey in group:
            paramDict[paramkey] += randVal

        groupnum+=1

def main():
    paramspassed = readParamsPassed()

    directory = getDirectory(paramspassed['website'], paramspassed['day'], paramspassed['hour'], paramspassed['min'])
    trainingdirectory = getDirectory(paramspassed['website'], paramspassed['day'], paramspassed['hour'], paramspassed['min'], 'training')

    numparamfiles = numFiles(directory)
    numtrainingparamfiles = numFiles(trainingdirectory)

    #initialize the paramdirectory for storage and training
    initparamdirectory(directory, numparamfiles, minSuperFiles, paramspassed)
    initparamdirectory(trainingdirectory, numtrainingparamfiles, paramspassed['numsessions'], paramspassed)
    
    #log directory 
    superlogdirectory = trainingdirectory + '/supertrainerlogs/'
    
    #log file name
    logfilename = "supertrainer.log"
    
    #set up the logs used for this file
    setUpLog(superlogdirectory, logfilename)

    procs = setUpCryptoTrainerBots(paramspassed['numsessions'])

    runBots(procs, paramspassed, numparamfiles)

if __name__ == "__main__":
    main()
