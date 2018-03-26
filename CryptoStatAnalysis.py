# Copyright (c) 2018 A&D
# Class to store decisions from each bot and then evaluate those decisions

import os
import datetime
import pathlib
import calendar

from CryptoEvaluator import calcPercentChange

#dictionary that contains all the symbols for the binance API calls
priceSymbols = {'bitcoin': 'BTCUSDT', 'ripple': "XRPBTC",
                'ethereum': 'ETHBTC', 'BCC': 'BCCBTC',
                'LTC': 'LTCBTC', 'Dash': 'DASHBTC',
                'Monero': 'XMRBTC', 'Qtum': 'QTUMBTC', 'ETC': 'ETCBTC',
                'Zcash': 'ZECBTC', 'ADA': 'ADABTC', 'ADX': 'ADXBTC', 'AION' : 'AIONBTC', 'AMB': 'AMBBTC', 'APPC': 'APPCBTC', 'ARK': 'ARKBTC', 'ARN': 'ARNBTC', 'AST': 'ASTBTC', 'BAT': 'BATBTC', 'BCD': 'BCDBTC', 'BCPT': 'BCPTBTC', 'BNB': 'BNBBTC', 'BNT': 'BNTBTC', 'BQX': 'BQXBTC', 'BRD': 'BRDBTC', 'BTS': 'BTSBTC', 'CDT': 'CDTBTC', 'CMT': 'CMTBTC', 'CND': 'CNDBTC', 'CTR':'CTRBTC', 'DGD': 'DGDBTC', 'DLT': 'DLTBTC', 'DNT': 'DNTBTC', 'EDO': 'EDOBTC', 'ELF': 'ELFBTC', 'ENG': 'ENGBTC', 'ENJ': 'ENJBTC', 'EOS': 'EOSBTC', 'EVX': 'EVXBTC', 'FUEL': 'FUELBTC', 'FUN': 'FUNBTC', 'GAS': 'GASBTC', 'GTO': 'GTOBTC', 'GVT': 'GVTBTC', 'GXS': 'GXSBTC', 'HSR': 'HSRBTC', 'ICN': 'ICNBTC', 'ICX': 'ICXBTC', 'IOTA': "IOTABTC", 'KMD': 'KMDBTC', 'KNC': 'KNCBTC', 'LEND': 'LENDBTC', 'LINK':'LINKBTC', 'LRC':'LRCBTC', 'LSK':'LSKBTC', 'LUN': 'LUNBTC', 'MANA': 'MANABTC', 'MCO': 'MCOBTC', 'MDA': 'MDABTC', 'MOD': 'MODBTC', 'MTH': 'MTHBTC', 'MTL': 'MTLBTC', 'NAV': 'NAVBTC', 'NEBL': 'NEBLBTC', 'NEO': 'NEOBTC', 'NULS': 'NULSBTC', 'OAX': 'OAXBTC', 'OMG': 'OMGBTC', 'OST': 'OSTBTC', 'POE': 'POEBTC', 'POWR': 'POWRBTC', 'PPT': 'PPTBTC', 'QSP': 'QSPBTC', 'RCN': 'RCNBTC', 'RDN': 'RDNBTC', 'REQ': 'REQBTC', 'SALT': 'SALTBTC', 'SNGLS': 'SNGLSBTC', 'SNM': 'SNMBTC', 'SNT': 'SNTBTC', 'STORJ': 'STORJBTC', 'STRAT': 'STRATBTC', 'SUB': 'SUBBTC', 'TNB': 'TNBBTC', 'TNT': 'TNTBTC', 'TRIG': 'TRIGBTC', 'TRX': 'TRXBTC', 'VEN': 'VENBTC', 'VIB': 'VIBBTC', 'VIBE': 'VIBEBTC', 'WABI': 'WABIBTC', 'WAVES': 'WAVESBTC', 'WINGS': 'WINGSBTC', 'WTC': 'WTCBTC', 'XVG': 'XVGBTC', 'XZC': 'XZCBTC', 'YOYO': 'YOYOBTC', 'ZRX': 'ZRXBTC'}

#dictionaires for the modes this can be run in
modes = {'SoloEvaluator': {'string': 'SoloEvaluator', 'value': 0}, 'SoloTrainer': {'string': 'SoloTrainer', 'value': 1}, 'MultiTrainer': {'string': 'MultiTrainer', 'value': 2}}

class CryptoStatsAnalysis:


    #place data attributes in here that you do not want stored by different instances of the bot
    #or redefine them using the parameter list passed
    def __init__(self, variationNum, classNum,  training, startMinute, endMinute, PARAMS, timestamp, openPrices, closePrices, volumes, runTime):
        #the timestamp of the run of cryptoTrainer
        self.runTime = runTime

        #the parameters the bot used
        self.params = PARAMS

        #store timestamp
        self.timestamp = timestamp

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

        ###### SETTING PATHS FOR SAVING ANALYSIS IN FILES #######
        #used in opening the appropriate file for this
        self.variationNum = variationNum
        self.classNum = classNum

        #count of the time the program chose not to buy
        self.numAbstain = 0

        #training = T will make the analysis files get stored with the other training
        #training = NT will make the analysis files get stored with the normal trading
        self.training = training

        # Directory path (r makes this a raw string so the backslashes do not cause a compiler issue
        #logPaths = r'C:\Users\katso\Documents\GitHub\Crypto\'
        logPaths = r'C:\Users\katso\Documents\GitHub\Crypto\Logs'

        #concatenates the logpath with a autotrader vs crypto evalutor distinction
        withMode = logPaths + '\\Mode-' + training

        # datetime object that holds the date
        date = datetime.date.today()
        day = date.day
        month = date.month
        year = date.year

        # concatenates the logpath with a date so each analysis log set is in its own file by day
        withDate = withMode + '\\Year-' + str(year) + '\\Month-' + str(calendar.month_name[month] + '\\Day-' + str(day))


        #concatenates the timestamp of the crypto trainer
        withRunTime = withDate  + '\\RunTime-'+  str(runTime)

        #concatenates with the class of the run included
        withClass = withRunTime + '\\Class-' + str(int(classNum))

        #concatenates with the variation number
        withVarNum = withClass + '\\Variation-' +str(int(variationNum))

        #creates a directory if one does not exist
        pathlib.Path(withVarNum).mkdir(parents=True, exist_ok=True)

        #file name concatentation with runNum
        fileName = "Time=" + str(timestamp) + '_Analysis.txt'

        # log file name + path
        logCompletePath = os.path.join(withVarNum, fileName)


        # open a file for appending (a). + creates file if does not exist
        self.file = open(logCompletePath, "a+")

        #Storage Variables: variables used for storing different attributes for the cryptos from each successive buy/sell period

        # Each successive iteration uses a different dictionary, each dictionary has a timestamp and a list of crypto objects with their stored data,should also include buy and sell times
        self.runStats = []

        #Each cycle has its own set of basic information
        self.runsInfo = []


        #overall interval the bot trained on
        self.startMinute = startMinute
        self.endMinute = endMinute




    #adds a dictionary where every crypto has a special holder object assigned to it with all important information to it from that moment when the dictionary was made
    # this method is called each time a crypto has been bought, as well as when the cryptos decide to keep the same crypto currency, and when they choose not to buy one
    def newStats(self, statsDict, minute, didBuy, didSell, bought, sold, decisions, decisionNum, timeHeld, didNotBuy):
        self.runStats.append({decisionNum: self.newCryptoDict()})
        self.runsInfo.append({decisionNum: cyrptoRunInfo(statsDict, minute, didBuy, didSell, bought, sold, decisions, timeHeld)})



        if didNotBuy == 1:
            self.addDidNotBuy()

        self.addMin(minute - timeHeld)


        for key, value in decisions.items():
            count = 0.0
            posCryptos = 0.0




            if len(value) == 0 or  value[0] == '' :
                self.file.write("HEY CHECK THIS" + '\n')
                self.file.write('Did buy ' + str(didBuy)  + '\n')
                self.file.write('Did sell ' + str(didSell)  + '\n')
                self.file.write('Bought ' + str(bought)  + '\n')
                self.file.write('Sold ' + str(sold)  + '\n')
                self.file.write('KEY' + str(key)  + '\n')
                self.file.write('VALUE ' + str(value)  + '\n')
                continue
            for i in value:

                change = self.caclulatePercentChange(minute, timeHeld, i)


                if change > 0.0:
                    posCryptos += 1.0
                count += 1.0


            if count == 0.0:
                self.runsInfo[decisionNum][decisionNum].setPosOverInterval(0.0, key)
            else:
                average = posCryptos / count
                self.runsInfo[decisionNum][decisionNum].setPosOverInterval(average, key)


    #adds more minutes to the minutes counter
    def addMin(self, min):
        self.minPast += min

    #add one to the number of times the program did not buy
    def addDidNotBuy(self):
        self.numAbstain += 1

    #returns a dictionary with one holder object for each crypto
    def newCryptoDict(self):
        newDict = {}
        for key, value in priceSymbols.items():
            newDict.update({value: CryptoHolder(value)})

        return newDict

    #sets the value passed to be whatever value num is specified
    def setVal(self, value, valueNum):
        if valueNum == 0:
            self.numBuys = value
        elif valueNum == 1:
            self.numSells = value
        elif valueNum == 2:
            self.allOwnedPercentChanges = value

    #calculates the percentage change over the interval for the currency
    def caclulatePercentChange(self, minute, timeHeld, currency):
        change = calcPercentChange(self.openPriceData[currency][minute - timeHeld], self.closePriceData[currency][minute])

        return change

    #calls the functions in order to format the analysis file correctly
    def writeToFile(self):
        self.basicInfo()
        self.buysAndSales()
        self.posCorrelations()

        self.file.close()

    #prints the date and timestamp
    def basicInfo(self):
        self.file.write('----------------------------------------- \n')
        self.file.write('Run was at ' + str(self.timestamp) + '\n')
        self.file.write('Number of times chose not to buy ' + str(self.numAbstain))
        self.file.write('Time Simulated ' + str(self.minPast) + '\n')
        self.file.write('The Parameters \n')
        for key, value in self.params.items():
            self.file.write(str(key) + ':' + str(value) +'\n')



    #writes the buys and sale numbers to the analysis file
    def buysAndSales(self):
        self.file.write('----------------------------------------- \n')
        self.file.write('Number of buys ' + str(self.numBuys) + '\n')
        self.file.write('Number of sales ' + str(self.numSells) + '\n')

    #print out the positive correlation for each crypto for every decision made
    def posCorrelations(self):
        count = 0
        self.file.write('----------------------------------------- \n')
        for i in self.runsInfo:
            self.file.write('\n')
            self.file.write('Decision ' + str(count) + ': \n')

            for key, value in i[count].posOverInterval.items():
                self.file.write(str(key) + ': ' + str(value) + '\n')
            count += 1

#stores the information calculated for each cryptocurrency at each decision point
class CryptoHolder():

    #decision can be B for bought, C for chosen, or NC for not chosen
    def __init__(self, cryptoName):
        self.symbol = cryptoName
        self.score = 0.0
        self.mean = 0.0
        self.decision = 'NC'

#stores the basic information about the period being evaluated
class cyrptoRunInfo():

    def __init__(self, statsDict, minute, didBuy, didSell, bought, sold, decisions, timeHeld):
        self.statsDict = statsDict
        self.minute = minute
        self.didBuy = didBuy
        self.didSell = didSell
        self.bought = bought
        self.sold = sold
        self.decisions = decisions
        self.timeHeld = timeHeld
        self.posOverInterval = {'Disregarded': 0.0, 'Chosen': 0.0, 'chosenButCut': 0.0, 'chosenNotCut': 0.0, 'theMax': 0.0}

    def setPosOverInterval(self, average, key):
        self.posOverInterval[key] = average * 100