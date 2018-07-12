# Copyright (c) 2018 A&D
# Class to store decisions from each bot and then evaluate those decisions

import os
import logging

from Generics import calcPercentChange, percenttodecimal

#setup the relative file path
dirname = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dirname + '/', '')


class CryptoStatsAnalysis:

    #place data attributes in here that you do not want stored by different instances of the bot
    #or redefine them using the parameter list passed
    def __init__(self, variationNum, classNum, startMinute, endMinute, PARAMS, openPrices, closePrices, volumes, highPrices,
                 lowPrices,  directory, passedparams, pricesymbols):
        """
        :param directory: the directory this log file will be stored in
        :param variationNum: the number of the variation of the corresponding evaluator
        :param classNum: the number of the class the corresponding evaluator belonged to
        :param startMinute: the minute the evaluator started trading on
        :param endMinute: the minute the evaluator stopped trading on
        :param PARAMS: the parameters used by the evaluator
        :param openPrices: the dictionary of open prices
        :param closePrices: the dictionary of close prices
        :param volumes: the dictionary of volumes
        :param highPrices: the dictionary of high prices
        :param lowPrices: the dictionary of low prices
        :param directory: the directory this log will be stored in
        :param passedparams: the parameters passed to the evaluator
        :param pricesymbols: the price symbols used by the evaluator
        """
        global priceSymbols

        #store the passed parameters
        self.passedparams = passedparams

        priceSymbols = pricesymbols

        #set the log file up
        self.setUpLogging(directory, str(int(variationNum)) + 'analysis.log')

        #the parameters the bot used
        self.params = PARAMS

        #initialize values to be set later
        self.numBuys = 0
        self.numSells = 0

        #variable to keep track of the time passed
        self.minPast = 0

        #initalize the list that will hold each consecutively owned crypto and the percent changes over the periods it is held
        self.allOwnedPercentChanges = []

        #initialize the dictionariies that will hold the open and close price data as well as the volume data used
        self.openPriceData = openPrices
        self.closePriceData = closePrices
        self.volumeData = volumes
        self.highPriceData = highPrices
        self.lowPriceData = lowPrices

        ###### SETTING PATHS FOR SAVING ANALYSIS IN FILES #######
        #used in opening the appropriate file for this
        self.variationNum = variationNum
        self.classNum = classNum

        #count of the time the program chose not to buy
        self.numAbstain = 0

        #Storage Variables: variables used for storing different attributes for the cryptos from each successive buy/sell period

        # Each successive iteration uses a different dictionary, each dictionary has a timestamp and a list of crypto objects with their stored data,should also include buy and sell times
        self.runStats = []

        #Each cycle has its own set of basic information
        self.runsInfo = []

        #a list of all the minutes each crypto was held for
        self.timeHeld = []

        #overall interval the bot trained on
        self.startMinute = startMinute
        self.endMinute = endMinute


    #set up the logging system this file will use
    def setUpLogging(self, directory, filename):
        """
        :param directory: the directory it is stored in
        :param filename: the name of the logging file to use
        :return:
        """

        logging.basicConfig(filename=directory+filename, level=logging.DEBUG)


    #adds a dictionary where every crypto has a special holder object assigned to it with all important information to it from that moment when the dictionary was made
    # this method is called each time a crypto has been bought, as well as when the cryptos decide to keep the same crypto currency, and when they choose not to buy one
    def newStats(self, statsDict, minute, didBuy, didSell, bought, sold, decisions, decisionNum, timeHeld ,
                 didNotBuy, owned):
        """
        :param statsDict:
        :param minute:
        :param didBuy:
        :param didSell:
        :param bought:
        :param sold:
        :param decisions:
        :param decisionNum:
        :param timeHeld:
        :param didNotBuy:
        :param owned:
        :return:
        """

        self.runStats.append({decisionNum: self.newCryptoDict()})
        self.runsInfo.append({decisionNum: cyrptoRunInfo(statsDict, minute, didBuy, didSell, bought, sold, decisions,
                                                         timeHeld, owned)})

        indexOf = len(self.runsInfo)

        if didNotBuy == 1:
            self.addDidNotBuy()

        self.addMin(timeHeld)
        self.calcPosCorrelations(timeHeld, decisions, decisionNum, minute, indexOf)

    #calculates and returns the true change in the money
    def calcMoneyChange(self):
        """
        :return:
        """
        startMoney = int(self.params['START_MONEY'])
        newEndMoney = int(startMoney)
        lossallowed = int(self.passedparams['lossallowed'])

        #the number of times we buy and sell
        totalDecisions = len(self.runsInfo)

        numDecision = 0

        #print('-----------------------------------------------------')

        for i in range(totalDecisions):

            startmon = newEndMoney

            currentDecision = self.runsInfo[numDecision][numDecision]

            currentCrypto = currentDecision.owned

            #print("decision {}".format(i))

            #if this decision including actually buying and selling
            if currentDecision.didBuy:
                #assume a lossallowed is removed for buying
                buyloss = newEndMoney * (lossallowed / percenttodecimal)

                #assume a lossallowed is removed for selling
                sellloss = newEndMoney * (lossallowed / percenttodecimal)

                #print("did buy")
            else:
                buyloss = 0
                sellloss = 0

                #print("did not buy")

            #calculate what money would be left after buying/selling loss
            cryptoMoneyMinusAssumedLoss = newEndMoney + buyloss + sellloss

            #print("money minus assumed loss {}".format(cryptoMoneyMinusAssumedLoss))

            # the money made over holding the crypto (but only considering it after the loss from buy/sell is removed)
            addMoney = cryptoMoneyMinusAssumedLoss * (
                        float(currentDecision.percentChanges[currentCrypto]) / percenttodecimal)

            #print("add money {}".format(addMoney))


            #alter the new end money by appreciation/depreciation from holding the crypto
            #and any loss from buying and selling
            newEndMoney += addMoney

            truechange = calcPercentChange(startmon, newEndMoney)

            #print("{} {}".format(float(currentDecision.percentChanges[currentCrypto]) / percenttodecimal, truechange))

            numDecision += 1


        return newEndMoney

    #calcualtes and stores all the positive percent changes
    def calcPercentChanges(self, decisionNum, minute, timeHeld):
        """
        :param decisionNum:
        :param minute:
        :param timeHeld:
        :return:
        """

        for key, currencyname in priceSymbols.items():
            change = self.caclulatePercentChange(minute, timeHeld, currencyname)
            # store the percent changes
            self.storePosCorrelations(change, currencyname, decisionNum)

    # calculating the positive correlation for the different decision groups
    def calcPosCorrelations(self, timeHeld, decisions, decisionNum, minute, indexOf):
        """
        :param timeHeld:
        :param decisions:
        :param decisionNum:
        :param minute:
        :param indexOf:
        :return:
        """

        self.calcPercentChanges(decisionNum, minute, timeHeld)

        #iterate through different segments of the cryptos
        for key, value in decisions.items():
            #initialize the count of cryptos
            count = 0.0

            #initialzise the count of the number of cryptos that had a positive change
            posCryptos = 0.0

            #initialize the total percentage change in the price
            totalChange = 0

            #iterate through each crypto in that segement
            for i in value:
                if i == '': #if this segement is empty skip over this
                    continue
                change = self.caclulatePercentChange(minute, timeHeld, i)

                #if the percent change was negative increment our count of poisitve cryptos
                if change > 0.0:
                    posCryptos += 1.0

                #add the current percent change to the total
                totalChange += change
                count += 1.0

            #if there was no crypto from that segment (the segments are what we are implicitly classifying things as)
            if count == 0.0:
                self.runsInfo[decisionNum][decisionNum].setPosOverInterval(0.0, key)

            else:
                average = posCryptos / count
                self.runsInfo[decisionNum][decisionNum].setPosOverInterval(average, key)

            if count != 0.0:
                averageChange = totalChange / count

            else:
                averageChange = totalChange
            self.runsInfo[decisionNum][decisionNum].setAveragePercentChange(averageChange, key)

    #stores the positive correlations for each crypto
    def storePosCorrelations(self, percentChange, key, decisionNum):
        """
        :param percentChange:
        :param key:
        :param decisionNum:
        :return:
        """
        self.runsInfo[decisionNum][decisionNum].percentChanges.update({key: percentChange})


    #adds more minutes to the minutes counter
    def addMin(self, min):
        """
        :param min:
        :return:
        """
        self.minPast += min
        self.timeHeld.append(min)

    #add one to the number of times the program did not buy
    def addDidNotBuy(self):
        """
        :return:
        """
        self.numAbstain += 1

    #returns a dictionary with one holder object for each crypto
    def newCryptoDict(self):
        """
        :return:
        """
        newDict = {}
        for key, currencyname in priceSymbols.items():
            newDict.update({currencyname: CryptoHolder(currencyname)})

        return newDict

    #gets the average minutes held
    def getAverageMin (self, timeHeld):
        """
        :param timeHeld:
        :return:
        """
        lenList = len(timeHeld)
        sumMin = 0

        for i in range(lenList):
            sumMin += self.timeHeld[i]

        averageMin = sumMin / lenList

        return averageMin

    #sets the value passed to be whatever value num is specified
    def setVal(self, value, valueNum):
        """
        :param value:
        :param valueNum:
        :return:
        """
        if valueNum == 0:
            self.numBuys = value
        elif valueNum == 1:
            self.numSells = value
        elif valueNum == 2:
            self.allOwnedPercentChanges = value

    #calculates the percentage change over the interval for the currency
    def caclulatePercentChange(self, minute, timeHeld, currency):
        """
        :param minute:
        :param timeHeld:
        :param currency:
        :return:
        """

        change = calcPercentChange(self.closePriceData[currency][minute - timeHeld],
                                   self.closePriceData[currency][minute])
        return change

    #works through all calculations that cover changes over the whole bot
    def finalCalculations(self):
        """
        :return:
        """
        endMoney = self.calcMoneyChange()

        return endMoney

    #calls the functions in order to format the analysis file correctly
    def writeToFile(self):
        """
        :return:
        """
        self.basicInfo()
        self.buysAndSales()
        self.diferentDecisions()

    #prints the date and timestamp
    def basicInfo(self):
        """
        :return:
        """
        logging.info('----------------------------------------- \n')
        logging.info('Number of times chose not to buy ' + str(self.numAbstain))
        logging.info('Time Simulated ' + str(self.minPast) + '\n')
        logging.info('Average Time Held ' + str(self.getAverageMin(self.timeHeld)) + '\n')
        logging.info('The Parameters \n')
        for key, value in self.params.items():
            logging.info(str(key) + ':' + str(value) +'\n')

    #writes the buys and sale numbers to the analysis file
    def buysAndSales(self):
        """
        :return:
        """
        logging.info('----------------------------------------- \n')
        logging.info('Number of buys ' + str(self.numBuys) + '\n')
        logging.info('Number of sales ' + str(self.numSells) + '\n')
        logging.info('Crypto chose not to buy ' + str(self.numAbstain) + '\n')

    #print out different information for each decision made
    def diferentDecisions(self):
        """
        :return:
        """

        count = 0
        logging.info('----------------------------------------- \n')
        for i in self.runsInfo:
            logging.info('\n')
            logging.info('Decision ' + str(count) + ': \n')
            self.transactionInfo(i, count)
            logging.info('Percent that Gained Over the Interval \n')
            self.printPosCorrelations(i, count)
            logging.info('Average Percent Change  \n')
            self.printAveragePercentChange(i, count)
            count += 1

    #prints the transaction information
    def transactionInfo(self, i, count):
        """
        :param i:
        :param count:
        :return:
        """

        logging.info("Held crypto " + str(i[count].timeHeld) + '\n')
        logging.info("Start minute " + str(i[count].minute - i[count].timeHeld) + '\n')
        logging.info("End minute " + str(i[count].minute) + '\n')
        if i[count].didBuy == 1:
            logging.info("Bought " + str(i[count].bought) + '\n')
        else:
            logging.info("Bought nothing" + '\n')
        if i[count].didSell == 1:
            logging.info("Sold " + str(i[count].sold) + '\n')
        else:
            logging.info("Sold nothing" + '\n')

    #prints the positive correlations between each of the decision groups and the % that gained money
    def printPosCorrelations(self, i, count):
        """
        :param i:
        :param count:
        :return:
        """

        for key, value in i[count].posOverInterval.items():
            logging.info(str(key) + ': ' + str(value) + '\n')


    #prints out all the average percent Changes
    def printAveragePercentChange(self, i, count):
        """
        :param i:
        :param count:
        :return:
        """

        for key, value in i[count].averagePercent.items():
            logging.info(str(key) + ': ' + str(value) + '\n')

    #prints out the list of percent Changes with each crypto

#stores the information calculated for each cryptocurrency at each decision point
class CryptoHolder():

    #decision can be B for bought, C for chosen, or NC for not chosen
    def __init__(self, cryptoName):
        """
        :param cryptoName:
        """
        self.symbol = cryptoName
        self.score = 0.0
        self.mean = 0.0
        self.decision = 'NC'

#stores the basic information about the period being evaluated
class cyrptoRunInfo():

    def __init__(self, statsDict, minute, didBuy, didSell, bought, sold, decisions, timeHeld, owned):
        """
        :param statsDict:
        :param minute:
        :param didBuy:
        :param didSell:
        :param bought:
        :param sold:
        :param decisions:
        :param timeHeld:
        :param owned:
        """
        self.statsDict = statsDict
        self.minute = minute
        self.didBuy = didBuy
        self.didSell = didSell
        self.bought = bought
        self.sold = sold
        self.decisions = decisions
        self.timeHeld = timeHeld
        self.owned = owned
        self.posOverInterval = {'Disregarded': 0.0, 'Chosen': 0.0, 'chosenButCut': 0.0,
                                'chosenNotCut': 0.0, 'theMax': 0.0}

        self.percentChanges = {}
        self.averagePercent = {'Disregarded': 0.0, 'Chosen': 0.0, 'chosenButCut': 0.0,
                               'chosenNotCut': 0.0, 'theMax': 0.0}

    def setPosOverInterval(self, average, key):
        """
        :param average:
        :param key:
        :return:
        """
        self.posOverInterval[key] = average * 100

    def setAveragePercentChange(self, averageChange, key):
        """
        :param averageChange:
        :param key:
        :return:
        """
        self.averagePercent[key] = averageChange