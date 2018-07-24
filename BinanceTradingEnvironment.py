# Copyright (c) 2018 A&D
# Class that encapsulates the different components necessary for the CryptoTradingManager to run multiple
# trading sessions for the Binance website
import PrivateData
import requests
import hmac
import hashlib
import os
import random


try:
    from urlib import urlencode

except ImportError:
    from urllib.parse import urlencode


from Generics import calcPercentOfTotal, calcPercentChange, defaultcryptoevaluatorparamspassed, writepickle, readpickle

class BinanceTradingEnvironment():

    def __init__(self, parameterdict, callingenvironment):

        #the parameter dictionary with all the parameters used by this environment
        self.parameterdict = parameterdict

        #the object calling this environment (CryptoTradingEnvironment)
        self.callingenvironment = callingenvironment

        #get the keys associated with this website
        self.keydict = self.getkeys(self.parameterdict['website'], self.parameterdict['userid'])

        #a list of processes of SuperTrainers
        self.supertrainerlist = []

        #a list of processes of CryptoEvaluators that are running independently
        self.cryptoevaluatorstradinglist = []


        #the dictionary of parameters passed to each CryptoEvaluator trading
        # each key lines up with the index of a CryptoEvaluator in the trading list
        self.cryptoevaluatorstradingparametersdict = {}

        #single process to run a CryptoDistribution script
        #the id is set to -1 arbitrarily
        self.cryptodistribution = self.getbinancesubprocess('CryptoDistribution.py', -1)

        #a single process to run a PseudoAPI_Datastream script
        # the id is set to -2 arbitrarily
        self.pseudoapidatastream = self.getbinancesubprocess('PseudoAPI_Datastream.py', -2)

        #the directory of this file
        self.dirname = '{}/{}'.format(os.path.dirname(os.path.realpath(__file__)),
                                      self.parameterdict['directoryprefix'])


    # the percentage of the money in the account to be used for trading at any time
    @property
    def percentageaccountmoneyinuse(self):
        return calcPercentOfTotal(self.parameterdict['currmoneyinaccount'], self.parameterdict['maxmoneyinuse'])

    # the secret key of the current account
    @property
    def secretkey(self):
        return self.keydict['secret_key']

    # the api key of the current account
    @property
    def apikey(self):
        return self.keydict['api_key']

    #return the keys associated with the specified website and user id for this trading environment
    def getkeys(self, website, userid):
        """
        :param website: the website being traded on
        :param userid: the user id corresponding to the account on the website we are trading on
        :return: the list of account keys for the website and user account
        """

        #call the correct key function
        return PrivateData.websiteaccountkeys[website][userid]

    #get a subprocess of the binance type
    def getbinancesubprocess(self, scriptname, textfileid):

        return self.callingenvironment.getsubprocess(scriptname, textfileid)

    #return the binance server time
    def getbinanceservertime(self):
        timestamp = requests.get("https://api.binance.com/api/v1/time")
        timestamp = timestamp.json()
        timestamp = timestamp['serverTime']

        return timestamp

    #build input string to be passed to a subprocess
    def getinputstring(self, listofinputvalues):
        inputstring = ''

        for value in listofinputvalues:
            inputstring = "{} {}".format(inputstring, value)

        return inputstring

    #list of the input parameters for an instance of crypto distribution
    @property
    def cryptodistributionsuprocessinputlist(self):
        #list for the CryptoDistribution subprocess
        return [self.parameterdict['website'], self.parameterdict['lossallowed']]

    #run a subprocess with CryptoDistribution script
    def runcryptodistribution(self):

        #build a string of the input
        inputstring = self.getinputstring(self.cryptodistributionsuprocessinputlist)

        self.cryptodistribution.communicate(input=inputstring)

    #check the status of the CryptoDistribution script
    def checkcryptodistribution(self):
        return self.cryptodistribution.returncode

    #kill the CryptoDistribution subprocess
    def killcryptodistribution(self):

        self.cryptodistribution.kill()

    #list of the input parameters for an instance of pseduoapi_datastream
    @property
    def pseudoapidatastreamsubproessinputlist(self):
        #list for the pseudoapi_datastream subprocess
        return [self.parameterdict['website'], self.parameterdict['minsofdatagatheredsofar'],
                self.parameterdict['maxminutestograbdata'], self.parameterdict['minutesofdatatoprimedatabase']
                , self.parameterdict['wipedatabaseatstart']]

    #run a subprocess with PseudoAPI_Datastream script
    def runpseduoapidatastream(self):

        #build a string of the input
        inputstring = self.getinputstring(self.pseudoapidatastreamsubproessinputlist)

        self.pseudoapidatastream.communicate(input=inputstring)

    #check the status of the PseudoAPI_Datastream script
    def checkpseudoapidatastream(self):
        return self.pseudoapidatastream.returncode

    #kill the PseudoAPI Datastream script
    def killpseudoapidatastream(self):

        self.pseudoapidatastream.kill()

    #list of the input parameters for an instance of super trainer
    def supertrainersubprocessinputlist(self, paramsdictforsupertrainer):
        listofvalues = []

        for key, value in paramsdictforsupertrainer.items():
            listofvalues.append(value)

        return  listofvalues

    #add a new SuperTrainer subprocess to the list
    def addnewsupertrainer(self):

        #the id to give to this supertrainer subprocess
        idforsupertrainer = len(self.supertrainerlist)

        self.supertrainerlist.append(self.getbinancesubprocess('SuperTrainer.py', idforsupertrainer))

    #get the index of the most recently created SuperTrainer
    def getnewestsupertrainerindex(self):
        return len(self.supertrainerlist) - 1

    #run a new SuperTrainer subprocess
    def runsupertrainer(self, indexofsupertrainertorun, paramsdictforsupertrainer):

        #check if the amount of money to start with is a valid amount
        #if no money is returend than you return and do not start the
        if (self.isnotvalidamountofmoney(paramsdictforsupertrainer['startmoney'])):
            return

        #the list of input variables to make an input string out of
        supertrainerinputlist = self.supertrainersubprocessinputlist(paramsdictforsupertrainer)

        #build a list for the input string for the subprocess
        inputstring = self.getinputstring(supertrainerinputlist)

        self.supertrainerlist[indexofsupertrainertorun].communicate(input=inputstring)

    # looks through the list of super trainers and removes any that have completed
    def cleanupsupertrainerlist(self):

        for supertrainersubprocessindex in range(len(self.supertrainerlist)):

            #the return code is None only when the subprocess has not terminated
            if self.checkstatusofsupertrainer(supertrainersubprocessindex) != None:
                self.killsupertrainer(supertrainersubprocessindex)

                del self.supertrainerlist[supertrainersubprocessindex]



    #check the status of the specified super trainer
    def checkstatusofsupertrainer(self, indexofsupertrainertocheck):

        return self.supertrainerlist[indexofsupertrainertocheck].returncode


    #kill the specified super trainer subprocess
    def killsupertrainer(self, indexofsupertraintokill):

        self.supertrainerlist[indexofsupertraintokill].kill()

    # add a new subprocess to run the CryptoEvaluator script
    def addnewcryptoevaluator(self):

        #the id of the crypto evaluator is the length of the list of current crypto evaluator subprocesses
        idofcryptoevaluator = len(self.cryptoevaluatorstradinglist)

        #a new subprocess to run CryptoEvalutor
        newcrytoevaluator = self.getbinancesubprocess('CryptoEvaluator.py', idofcryptoevaluator)

        self.cryptoevaluatorstradinglist.append(newcrytoevaluator)

    #get the newest crypto evaluator index
    #assumes no CryptoEvaluators have been cleaned up and removed since the addition of any new CryptoEvaluators
    def getnewestcryptoevaluatorindex(self):
        return len(self.cryptoevaluatorstradinglist) - 1

    #run the specified CryptoEvaluator script as a subprocess
    def runcryptoevaluator(self, indexofevaluatorsubprocess, paramsdictforcryptoevaluator):

        #the amount of money this evaluator wants to trade with
        desiredtradingmoney = paramsdictforcryptoevaluator['startmoney']

        #check if the desired trading money is a valid amount
        if (self.isnotvalidamountofmoney(desiredtradingmoney)):
            return
        else:
            #if it is a valid amount of money update the amount of money being used
            self.updatemoneyinuse(desiredtradingmoney)

        #get the input list of values used by a crypto evaluator
        inputvaluelist = self.evaluatorsubprocessinputlist(paramsdictforcryptoevaluator)

        #the list of the input string to run a crypto evaluator subprocess
        inputstring = self.getinputstring(inputvaluelist)

        #add the input string values into a dictionary that is then stored in a dictionary of
        # the parameters passed to each CryptoEvaluator trading
        self.storecryptoevaluatortradingparams(inputstring)

        #setup the trading directory so that there is a parameter pickle waiting for this CryptoEvaluator
        self.setparampickleforcryptoevaluator(paramsdictforcryptoevaluator)

        #run the specified crypto evalautor
        self.cryptoevaluatorstradinglist[indexofevaluatorsubprocess].communicate(input=inputstring)

    #cleanup the list of CryptoEvaluators by removing ones that have finished and returning the money they were using
    def cleanupcryptoevaluatorstrading(self):

        for cryptoevaluatorsubprocessindex in range(len(self.cryptoevaluatorstradinglist)):

            if self.checkstatusofcryptoevaluatortrading(cryptoevaluatorsubprocessindex) != None:

                self.killcryptoevaluatortrading(cryptoevaluatorsubprocessindex)

                self.returnmoneyinusebacktopoolofmoneytouse(cryptoevaluatorsubprocessindex)

                self.deletethiscryptoevaluatortrading(cryptoevaluatorsubprocessindex)

                self.deletethiscryptoevaluatortradingparameters(cryptoevaluatorsubprocessindex)

    #return the status code of the specified CryptoEvaluator trading
    def checkstatusofcryptoevaluatortrading(self, indexofcryptoevaluatortradingtocheck):

        return self.cryptoevaluatorstradinglist[indexofcryptoevaluatortradingtocheck]

    #kill the CryptoEvaluator subprocess specified
    def killcryptoevaluatortrading(self, indexofcryptoevaluatortradingtokill):

        self.cryptoevaluatorstradinglist[indexofcryptoevaluatortradingtokill].kill()

    # update the money in use by adding a negative amount of the starting money from the
    # amount of money that the current crypto evaluator started with
    def returnmoneyinusebacktopoolofmoneytouse(self, cryptoevaluatorsubprocessindex):
        self.updatemoneyinuse(-1 * self.cryptoevaluatorstradingparametersdict
                                    [cryptoevaluatorsubprocessindex]['startmoney'])

    # delete the CryptoEvaluator trading
    def deletethiscryptoevaluatortrading(self, cryptoevaluatorsubprocessindex):
        del self.cryptoevaluatorstradinglist[cryptoevaluatorsubprocessindex]

    # delete the dictionary of the parameters associated with the CryptoEvaluator index passed
    def deletethiscryptoevaluatortradingparameters(self, cryptoevaluatorsubprocessindex):
        self.cryptoevaluatorstradingparametersdict.pop(cryptoevaluatorsubprocessindex)

    #the list of input parameter values for a CryptoEvaluator script
    #if the passed amount of money is not valid then an empty list will be returned
    def evaluatorsubprocessinputlist(self, paramsdictforcryptoevaluator):

        valueslist = []

        for key, value in paramsdictforcryptoevaluator.items():
            valueslist.append(value)

        return valueslist

    # check if the amount of money passed to simulate (or trade with) is not a valid amount as set
    # by the limits given to this environment and/or the current money in the account used to trade
    def isnotvalidamountofmoney(self, desiredamountofmoneytosimulatewith):

        # update the true amount of money in the accounts
        self.updatemoneyinaccount()

        if desiredamountofmoneytosimulatewith > self.parameterdict['maxstartmoney']:
            return True
        elif desiredamountofmoneytosimulatewith < self.parameterdict['minstartmoney']:
            return True
        elif (desiredamountofmoneytosimulatewith + self.parameterdict['moneyinuse'] > self.parameterdict['maxmoneyinuse']):
            return True
        elif(self.parameterdict['maxmoneyinuse'] > self.parameterdict['currmoneyinaccount'] ):
            return True

        return False

    # updates the money being used by all of the bots
    # in reality this could be a higher or lower number depending on if the bots have lost money
    def updatemoneyinuse(self, newmoneyused):
        self.updatemoneyinaccount()

        self.parameterdict['moneyinuse'] += newmoneyused


    #update the amount of money currently in the account
    def updatemoneyinaccount(self):

        #the amount of money currently in the account using the website appropriate function
        newamountofcurrentmoney = getattr(self, self.parameterdict['website'] + 'getcurrmoneyinaccount')()

        #update the maximum amount of money allowed to be used for trading at any given time
        self.updatemaxmoneyinuse(newamountofcurrentmoney)

        self.parameterdict['currmoneyinaccount'] = newamountofcurrentmoney

    #update the amount of max money in use by the new amount of current money in the account
    def updatemaxmoneyinuse(self, newamountofcurrentmoneyinaccount):

        self.parameterdict['maxmoneyinuse'] = self.percentageaccountmoneyinuse * newamountofcurrentmoneyinaccount

    #get the amount of money currently in the account using binance
    def binancegetcurrmoneyinaccount(self):
        #the time of our request
        timestamp = self.getbinanceservertime()

        #get the query string
        querystring = self.getbinanceaccountinfoquerystring(timestamp)

        #get the list of the balances
        balanceslist = self.getbinancebalancelist(querystring)

        #make a new dictionary where the free and locked amounts of each currency are added up
        # and keyed by the symbol
        allbalancesdict = self.sumandcombinebinancebalancelist(balanceslist)

        #convert the amounts of cryptos in the balance dictionary into money
        allbalancesdictindollars = self.binancebalancedictindollars(allbalancesdict)

        #sum up the values in the dictionary of the balances in dollars for all cryptos
        totaldollarsinaccount = self.sumdollaramountsinbinancebalancesdict(allbalancesdictindollars)

        return totaldollarsinaccount

    #return a query string used to get the account info from biannce
    def getbinanceaccountinfoquerystring(self, timestamp):

        params = {'timestamp': timestamp}
        query = urlencode(sorted(params.items()))
        signature = hmac.new(self.parameterdict['secretkey'].encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
        query += "&signature=" + signature

        return query

    #return a list of the balances from a binance account
    def getbinancebalancelist(self, querystring):

        headers = {'X-MBX-APIKEY': self.parameterdict['apikey']}

        accountinfo = requests.get("https://api.binance.com/api/v3/account?" + querystring, headers=headers)

        accountinfodict = accountinfo.json()

        return accountinfodict['balances']

    #return a dictionary keyed by the crypto symbol where the value is the summation of the free
    # and locked amounts of each crypto
    def sumandcombinebinancebalancelist(self, balanceslist):

        balancesdict = {}

        for index in range(len(balanceslist)):

            #get the dictionary for the current symbol with the free and locked amounts
            assetdict = balanceslist[index]

            #the summed free and locked amounts of the current crypto
            totalcoins = float(assetdict['free']) + float(assetdict['locked'])

            #make a new entry in the dictionary of the summed up amounts of crypto
            balancesdict.update({assetdict['asset']: totalcoins})

        return balancesdict

    #convert the number of coins of each type of crypto into dollar amounts
    def binancebalancedictindollars(self, binancebalancesdict):

        #get the price of BTCUSDT to convert coins in terms of BTC to the closest metric to US Dollars
        bitcointousdollarsconversion = self.getbinanceprice('BTCUSDT')

        for cryptotype, totalcoins in binancebalancesdict.items():

            #if this is BTC convert to dollars
            if cryptotype == 'BTC':
                amountindollars = bitcointousdollarsconversion * totalcoins

                binancebalancesdict.update({cryptotype: amountindollars})

            #if this is USDT the coin amount is in dollars
            elif cryptotype == 'USDT':
                continue

            else:
                #get the current currency into bitcoins
                priceofcurrentcryptoinbtc = self.getbinanceprice("{}BTC".format(cryptotype))

                #convert the amount of crypto coins into bitcoins
                coinamountinbitcoins =  totalcoins * priceofcurrentcryptoinbtc

                #convert the bitcoins amount into dollars
                bitcoinsindollars = coinamountinbitcoins * bitcointousdollarsconversion

                binancebalancesdict.update({cryptotype: bitcoinsindollars})

        return binancebalancesdict

    # get the binance price of the specified currency
    def getbinanceprice(self, currency):
        """
        :param currency:
        :return:
        """
        # getting the aggregate trade data and finding one price to return
        parameters = {'symbol': currency}
        binData = requests.get("https://api.binance.com/api/v3/ticker/price", params=parameters)
        binData = binData.json()
        binPrice = binData['price']
        return binPrice

    #return a summation of all the dollar amounts of each crypto in an account
    def sumdollaramountsinbinancebalancesdict(self, binancebalancedictindollars):

        totalmoneyinaccount = 0

        for cryptosymbol, dollarsofcoin in binancebalancedictindollars.items():

            totalmoneyinaccount += dollarsofcoin

        return totalmoneyinaccount

    #stores the passed list of values as a new dictionary entry indexed by the CryptoEvalautor trading
    # that they correspond to
    def storecryptoevaluatortradingparams(self, inputlistofcryptoevaluatortradingparams):

        #the length of the current dictionary will be the index of the newest dictionary since the list
        # this will correspond to is indexed at 0
        lenofcurrentdict = len(self.cryptoevaluatorstradingparametersdict)

        #add a new dictioanry to the dictionary of CryptoEvaluator trading parameters
        self.cryptoevaluatorstradingparametersdict.update({lenofcurrentdict: {}})

        #index of the value to grab from the input list passed
        indexofvaluefrominputlist = 0

        #loop through the list of the default values and stored the values in the input list
        for key, value in defaultcryptoevaluatorparamspassed.items():
            currentvaluefrominputlist = inputlistofcryptoevaluatortradingparams[indexofvaluefrominputlist]

            self.cryptoevaluatorstradingparametersdict[lenofcurrentdict].update({key: currentvaluefrominputlist})

            indexofvaluefrominputlist += 1

    #store the most recently trained parameters from the storage directory in the trading directory so that
    #each CryptoEvaluator has baseparameters to use
    def setparampickleforcryptoevaluator(self, paramspassedtocryptoevaluator):
        """
        :param paramspassedtocryptoevaluator:
        :return:
        """

        variationnumber = paramspassedtocryptoevaluator['variationNum']
        classnumber = paramspassedtocryptoevaluator['classNum']

        evaluatorparamstostore = self.getrecentlytrainedevaluatorparams(paramspassedtocryptoevaluator)

        #the directory where the parameters used for trading that have already been trained are stored
        tradingdirectory = "{}/{}/{}/{}/{}/{}/{}/{}/".format(self.dirname, 'trading',
                                                             paramspassedtocryptoevaluator['website'],
                                                             paramspassedtocryptoevaluator['day'],
                                                             paramspassedtocryptoevaluator['hour'],
                                                             paramspassedtocryptoevaluator['min'],
                                                             paramspassedtocryptoevaluator['idnum'],
                                                             paramspassedtocryptoevaluator['classNum'])
        #store the CryptoEvaluator parameters
        writepickle(evaluatorparamstostore, tradingdirectory,
                    '{}param.pkl'.format(paramspassedtocryptoevaluator['variationNum']))


     #finds the most recently trained parameters and stores them
    def getrecentlytrainedevaluatorparams(self, paramspassedtocryptoevaluator):

        #the directory where the parameters are stored after training
        storagedirectory = "{}/{}/{}/{}/{}/{}/".format(self.dirname, 'storage',
                                                             paramspassedtocryptoevaluator['website'],
                                                             paramspassedtocryptoevaluator['day'],
                                                             paramspassedtocryptoevaluator['hour'],
                                                             paramspassedtocryptoevaluator['min'])

        #the dictionary of recently trained Trainers and their CryptoEvaluators
        recentlytrained = readpickle(storagedirectory, 'recentlytrained.pkl')

        #number of trainer ids that have been recently trained
        numtrainersrecentlytrained = len(recentlytrained)

        #pick a specific trainer
        trainerindex = int(random.uniform(0,1) * numtrainersrecentlytrained)

        #the number of cryptoevaluators that have been recently trained
        numcryptoevaluatorsrecentlytrained = len(recentlytrained[trainerindex])

        #pick a specific evaluator
        evaluatorindex = int(random.uniform(0,1) * numcryptoevaluatorsrecentlytrained)

        #directory of the specified CryptoEvaluator params stored
        storagedirectoryofcryptoevaluatorparams = "{}/{}/{}/{}/{}/{}/{}/".format(self.dirname, 'storage',
                                                             paramspassedtocryptoevaluator['website'],
                                                             paramspassedtocryptoevaluator['day'],
                                                             paramspassedtocryptoevaluator['hour'],
                                                             paramspassedtocryptoevaluator['min'],
                                                             trainerindex)

        #load the specified CryptoEvaluator
        cryptoevaluatorparamschosen = readpickle(storagedirectoryofcryptoevaluatorparams,
                                                 '{}baseparams.pkl'.format(evaluatorindex))

        return cryptoevaluatorparamschosen

