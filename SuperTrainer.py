# Copyright (c) 2018 A&D
# Supertrainer runs multiple trainers for classes of bots. Each trainer uses some
# different parameters to run that are common between bots in a class

import os
import pathlib
import pickle as pkl
from Generics import PARAMETERS, priceSymbols, modes, websites, superParams

# setup the relative file path
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname + '/', '')

# grabs the specified param file by the website, day, and id number that
# correspond to it


def grabParamFile(idnum, website, day):
    """
    :param day: the day of the week that the params were produced from
    :param website: the website that the params were trained with data from
    :param idnum: the idnumber of the supertrainer param file
    :return:
    """
    path = filename + website + '/' + day
    # makes the directorys in the path variable if they do not exist
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    with open(path + "/{}superparam.pkl".format(idnum), "rb") as pickle_in:
        paramDict = pkl.load(pickle_in)

    return paramDict

# write parameters to a file
# if no id is provided it will overwrite the first one


def writeParamPickle(paramDict, website, day, idnum):
    """
    :param paramDict: the super trainer parameter dictionary to be written to
    :param day: the day of the week that the supertrainer was trained on
    :param website: the website that the supertrainer was trained on
    :param idnum: the id number of the super trainer parameter file
    :return:
    """
    path = filename + website + '/' + day
    # makes the directorys in the path variable if they do not exist
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    with open(path + "/{}superparam.pkl".format(idnum), "wb") as pickle_out:
        pkl.dump(paramDict, pickle_out)

# reads the parameters passed from the script running this file
# will specify what website is being used and what the day is


def readParamsPassed():
    """
    :param:
    :return: dicitonary of parameters passed from the file running that determine how the supertrainer will train
    """
    return {'website': 'binance', 'day': 'monday', 'numsessions': 1}

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


def getDirectory(website, day):
    """
    :param day: the day of the week that the supertrainer was trained on
    :param website: the website that the supertrainer was trained on
    :return:
    """
    return filename + website + '/' + day


def main():
    paramspassed = readParamsPassed()

    directory = getDirectory(paramspassed['website'], paramspassed['day'])

    idnum = numFiles(directory) + 1

    writeParamPickle(superParams, paramspassed['website'], paramspassed['day'], idnum)

    params = grabParamFile(idnum, paramspassed['website'], paramspassed['day'])


if __name__ == "__main__":
    main()
