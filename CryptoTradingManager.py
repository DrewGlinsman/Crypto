# Copyright (c) 2018 A&D
# Script to create CryptoTradingEnvironments as needed and simultaneously run all the data updating
# as well general trading for each environment

import os
import sys
import time
import datetime

from Generics import defaultcryptotradingmanagerparamspassed, defaultcryptotradingenvironmentparams, \
    defaultbinancetradingenvironmentparams, secondsinmin, mininhour, defaultsuperparamspassed, \
    defaultcryptoevaluatorparamspassed, weekdays, daysinweek, hourinday, weekdaytonum
from CryptoTradingEnvironment import CryptoTradingEnvironment

#reads any parameters that were passed in
def readparamspassed():

    if len(sys.argv) == 1 :
        return defaultcryptotradingmanagerparamspassed
    elif sys.argv[1] != 'CryptoTradingManager':
        return defaultcryptotradingmanagerparamspassed
    elif sys.argv[1] == 'CryptoTradingManager':
        index = 0
        for param, paramvalue in defaultcryptotradingmanagerparamspassed.items():
            defaultcryptotradingmanagerparamspassed.update({param: sys.argv[index]})
            index += 1

#sets up trading environments
def setuptradingenvironments(paramspassed, dictoftradingenvironments):
    """
    :param paramspassed: parameters passed to this script
    :param dictoftradingenvironments: the dictionary of trading environments
    :return:
    """

    websiteindex = 0

    for websitename in paramspassed['websites']:

        for useridindices in paramspassed['accounts'][websiteindex]:

            if websitename not in dictoftradingenvironments:
                dictoftradingenvironments.update({websitename: {}})

            tradingenvironment = maketradingenvironment(websitename, useridindices, paramspassed)

            dictoftradingenvironments[websitename].update({useridindices: tradingenvironment})

        websiteindex += 1

#return a trading envionrment
def maketradingenvironment(websitename, useridindex, paramspassed):
    """
    :param websitename: the name of the website to use
    :param useridindex: the user id associated with a website account
    :param paramspassed: the parameters passed to this script
    :return: a CryptoTradingEnvironment
    """

    paramsdict = makecryptotradingenvironmentparameterdict(websitename, useridindex, paramspassed)

    return CryptoTradingEnvironment(paramsdict)


#make a parameter dictionary for a CryptoTradingEnvironment
def makecryptotradingenvironmentparameterdict(websitename, userid, paramspassed):
    """
    :param websitename: the name of the website to use
    :param useridindex: the user id associated with a website account
    :param paramspassed: the parameters passed to this script
    :return: a parameter dictionary
    """

    defaultparamsfortradingenvironmenttype = getdefaulttradingenvironmentparams(websitename)

    for param, paramvalue in defaultparamsfortradingenvironmenttype.items():

        #if this parameter is one from the passed parameters
        if param in defaultcryptotradingmanagerparamspassed:

            valuepassed = paramspassed[param]

            defaultparamsfortradingenvironmenttype.update({param: valuepassed})

    #the two parameters that have to be pulled individualy from the
    # passed parameters because they are stored with others in lists
    defaultparamsfortradingenvironmenttype.update({'website': websitename})
    defaultparamsfortradingenvironmenttype.update({'userid': userid})

    return defaultparamsfortradingenvironmenttype

#return a dictionary with the default parameters for the specified trading environment
def getdefaulttradingenvironmentparams(websitename):
    """
    :param websitename: the website name
    :return: the trading environment parameters
    """

    if websitename == 'binance':
        return defaultbinancetradingenvironmentparams
    else:
        return defaultcryptotradingenvironmentparams

#run the CryptoDistribution scripts
def runcryptodistributions(dictoftradingenvironments):
    """
    :param dictoftradingenvironments:
    :return:
    """

    for website, useriddict in dictoftradingenvironments.items():
        for useridnum in useriddict:
            dictoftradingenvironments[website][useridnum].runcryptodistribution()

#run the PseudoAPI_Datastream scripts
def runpseudoapidatastreams(dictoftradingenvironments):
    """
    :param dictoftradingenviornments:
    :return:
    """

    for website, useriddict in dictoftradingenvironments.items():
        for useridnum in useriddict:
            dictoftradingenvironments[website][useridnum].runpseduoapidatastream()

#runs the trading enviornments
def runenviornments(paramspassed, dictoftradingenvironments):
    """
    :param paramspassed: parameters passed
    :param dictoftradingenvironments: the dictionary of the trading environments
    :return:
    """

    #run all the Crypto Distributions
    runcryptodistributions(dictoftradingenvironments)

    #run all the PseduoAPI_Datastreams
    runpseudoapidatastreams(dictoftradingenvironments)

    #wait until the start of the hour
    starttime, currtime = waituntiltopofthehour()


    while(True):

        #if we are 20 minutes ahead of a multiple of when we want to trade(used to train supertrainers)
        if int(currtime) + secondsinmin * 20 % paramspassed['timebetweentrading'] == 0:

            #only run when the second and millisecond are 0
            #otherwise this will run for the entire minute that
            #the current time is an hour from when the function started
            if(timeisrighttorun() == False):
                continue


            currentdatedict = getcurrentdatedict()

            #advance the super trainers by 20 minutes so that they simulate up to 20 minutes from now
            #which is when their associated crypto evaluators will run
            advancedatedict(currentdatedict, minutes=20)

            """
            cleanupsupertrainers(dictoftradingenvironments)
            addsupertrainers(dictoftradingenvironments)
            runsuptertrainer(dictoftradingenvironments, paramspassed, datedict)
            """

        #if we are not at a  multiple of the minutes of time specified between trading
        elif int(currtime) % paramspassed['timebetweentrading'] != 0:
            time.sleep(30)

        else:
            #only run when the second and millisecond are 0
            #otherwise this will run for the entire minute that
            #the current time is an hour from when the function started
            if(timeisrighttorun() == False):
                continue

            currentdatedict = getcurrentdatedict()

            """

            cleanupcryptoevaluators(dictoftradingenvironments)
            cryptoevaluatorindicies = addcryptoevaluatorstotrade(dictoftradingenvironments, paramspassed)
            runcryptoevaluatorstotrade(dictoftradingenvironments, cryptoevaluatorindicies, paramspassed, datedict)
            """
            print("Here {}".format(currtime/mininhour))

        currtime = time.time() / secondsinmin

#waits until the top of the hour and returns the time in seconds
def waituntiltopofthehour():

    checktime = datetime.datetime.now()

    checktimeminute = checktime.minute

    # get the current time in minutes before looping in case we are already at the top of the hour
    starttime = time.time() / secondsinmin
    currtime = starttime

    while(checktimeminute != 0):

        #get the current time in minutes
        starttime = time.time() / secondsinmin
        currtime = starttime

    return starttime, currtime

#return True if the second and millisecond are both 0
def timeisrighttorun():

    currentdatetime = datetime.datetime.now()

    seconds = currentdatetime.second

    milliseconds = currentdatetime.microsecond

    if seconds == 0 and milliseconds == 0:
        return True

    return False


#return a dictionary with the day of the week, the hour, and the minute
def getcurrentdatedict():
    currentdatetime = datetime.datetime.now()

    currentdatetimedayofweeknum = datetime.datetime.today().weekday()

    currentdatetimedayofweek = weekdays[currentdatetimedayofweeknum]

    currentdatetimehour = currentdatetime.hour

    currentdatetimeminute = currentdatetime.minute

    datedict = {'day': currentdatetimedayofweek,'hour': currentdatetimehour, 'min': currentdatetimeminute}

    return datedict

#identifies and removes any supertrainer no longer running from each trading environment
def cleanupsupertrainers(dictoftradingenvironments):
    """
    :param dictoftradingenvironments:
    :return:
    """

    for website, useriddict in dictoftradingenvironments.items():
        for useridnum in useriddict:
            dictoftradingenvironments[website][useridnum].cleanupsupertrainerlist()

#adds a supertrainer for each trading environment
def addsupertrainers(dictoftradingenvironments):
    """
    :param dictoftradingenvironments:
    :return:
    """


    for website, useriddict in dictoftradingenvironments.items():
        for useridnum in useriddict:
            dictoftradingenvironments[website][useridnum].addnewsupertrainer()

#run the super trainer
def runsupertrainer(dictoftradingenvironments, paramspassed, datedict):
    """
    :param dictoftradingenvironments:
    :param paramspassed:
    :param datedict:
    :return:
    """

    for website, useriddict in dictoftradingenvironments.items():
        for useridnum in useriddict:
            paramstopasstosupertrainer = getsupertrainerparams(paramspassed, website, datedict)

            indexofsupertrainertorun = dictoftradingenvironments[website][useridnum].getnewestsupertrainerindex()

            dictoftradingenvironments[website][useridnum].runsupertrainer(indexofsupertrainertorun, paramstopasstosupertrainer)


#advances the date in the date dict by the specified amount of minutes
def advancedatedict(datedict, minutes):

    weekdaynum = weekdaytonum[datedict['day']]

    minutesindatedict = datedict['min']

    hourindatedict = datedict['hour']

    if minutes + minutesindatedict < mininhour:

        newminvalue = minutes + minutesindatedict
        datedict.update({'min': newminvalue})
    else:

        additionalhour = int((minutes + minutesindatedict) / mininhour)

        if additionalhour + hourindatedict < hourinday:

            leftoverminutes = (minutes + minutesindatedict) % mininhour

            datedict.update({'min': leftoverminutes})

            newhourvalue = additionalhour + hourindatedict

            datedict.update({'hour': newhourvalue})

        else:

            leftoverminutes = (minutes + minutesindatedict) % mininhour

            datedict.update({'min': leftoverminutes})

            leftoverhours = (additionalhour + hourindatedict) % hourinday

            datedict.update({'hour': leftoverhours})

            daystoadd = int((additionalhour + hourindatedict) / hourinday)

            nextdaynum = weekdaynum + daystoadd

            nextday = weekdays[nextdaynum % daysinweek]

            datedict.update({'day': nextday})


#return a dictionary with the parameters used by a super trainer
def getsupertrainerparams(paramspassed, websitename, datedict):
    """
    :param paramspassed:
    :param websitename:
    :param datedict:
    :return:
    """

    for key, value in paramspassed.items():
        if key in defaultsuperparamspassed:
            defaultsuperparamspassed.update({key: value})
    for datekey, datekeyinfo in datedict.items():
        if datekey in defaultsuperparamspassed:
            defaultsuperparamspassed.update({datekey: datekeyinfo})

    defaultsuperparamspassed.update({'website': websitename})


#identifies and removes any crypto evaluators from the trading environments
def cleanupcryptoevaluators(dictoftradingenvironments):
    """
    :param dictoftradingenvironments:
    :return:
    """

    for website, useriddict in dictoftradingenvironments.items():
        for useridnum in useriddict:
            dictoftradingenvironments[website][useridnum].cleanupcryptoevaluatorstrading()

#adds a specified number of CryptoEvaluators to trade for each trading environment
def addcryptoevaluatorstotrade(dictoftradingenvironments, paramspassed):
    """
    :param dictoftradingenvironments:
    :param paramspassed:
    :return: dict of crypto evaluator indicies just created
    """

    cryptoevaluatorindices = {}

    for website, useriddict in dictoftradingenvironments.items():
        for useridnum in useriddict:
            for tradernum in range(paramspassed['numberofbotsrunpertimeslottrading']):
                dictoftradingenvironments[website][useridnum].addnewcryptoevaluator()

                if website not in cryptoevaluatorindices:
                    cryptoevaluatorindices.update({website: {}})

                elif useridnum not in cryptoevaluatorindices[website]:
                    cryptoevaluatorindices[website].update({useridnum: []})

                newestindex = dictoftradingenvironments[website][useridnum].getnewestcryptoevaluatorindex()

                cryptoevaluatorindices[website][useridnum].append(newestindex)

    return cryptoevaluatorindices

#runs the CryptoEvaluators stored in each trading environment that have not been started
def runcryptoevaluatorstotrade(dictoftradingenvironments, cryptoevaluatorindicies, paramspassed, datedict):
    """
    :param dictoftradingenvironments:
    :param cryptoevaluatorindicies:
    :param paramspassed:
    :param datedict:
    :return:
    """

    for website, useriddict in dictoftradingenvironments.items():
        for useridnum in useriddict:
            paramstopasstocryptoevaluator = getcrytoevaluatorparams(paramspassed, website, datedict)

            #counter used to give each crypto evaluator trading a class number/variation number so they are
            #stored separately
            classnumandvariationforcryptoevaluator = 0

            for cryptoevaluatorindex in cryptoevaluatorindicies[website][useridnum]:
                paramstopasstocryptoevaluator.update({'classNum': classnumandvariationforcryptoevaluator})
                paramstopasstocryptoevaluator.update({'variationNum': classnumandvariationforcryptoevaluator})

                dictoftradingenvironments[website][useriddict].runcryptoevaluators(cryptoevaluatorindex,
                                                                                   paramstopasstocryptoevaluator)

                classnumandvariationforcryptoevaluator += 1

#return a dictionary with the parameters from the parameters passed dictionary
# that are to be used by the crypto evaluators
def getcrytoevaluatorparams(paramspassed, website, datedict):
    """
    :param paramspassed:
    :param website:
    :param datedict:
    :return:
    """

    for key, value in paramspassed.items():
        if key in defaultcryptoevaluatorparamspassed:
            defaultcryptoevaluatorparamspassed.update({key: paramspassed[key]})
    for datekey, datekeyinfo in datedict.items():
        if datekey in defaultcryptoevaluatorparamspassed:
            defaultcryptoevaluatorparamspassed.update({datekey: datekeyinfo})


    defaultcryptoevaluatorparamspassed.update({'website': website})

def main():
    homedirectory = os.path.dirname(os.path.realpath(__file__))

    paramspassed = readparamspassed()

    dictoftradingenvironments = {}

    setuptradingenvironments(paramspassed, dictoftradingenvironments)

    runenviornments(paramspassed, dictoftradingenvironments)


if __name__ == "__main__":
    main()