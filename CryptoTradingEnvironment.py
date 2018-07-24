# Copyright (c) 2018 A&D
# Class that encapsulates the different components necessary for the CryptoTradingManager to run multiple
# trading sessions for separate websites

from subprocess import PIPE, Popen
from sys import executable
from BinanceTradingEnvironment import BinanceTradingEnvironment

class CryptoTradingEnvironment():

    def __init__(self, parameterdict):

        #The current Trading Environment being abstracted by this Generic Trading environment
        self.tradingenvironment = self.maketradingenvironment(parameterdict, self)

        #the parameters passed
        self.parameterdict = parameterdict


    #the website this CryptoTradingEnvironment corresponds to
    @property
    def websiterunon(self):
        return self.parameterdict['website']

    #the userid this CryptoTradingEnvironment corresponds to
    @property
    def userid(self):
        return self.parameterdict['userid']


    #makes a trading environment object that is the same as the file
    def maketradingenvironment(self, parameterdict, thistradingenvironment):

        if parameterdict['website'] == 'binance':
            return BinanceTradingEnvironment(parameterdict, thistradingenvironment)
        else:
            quit(-1)

    #return a subprocess object with the given parameters
    def getsubprocess(self, scriptname, textfileids):
        """
        :param scriptname: the name of the script to run
        :param textfileids: the number to be associated with this files output
        :return: a subprocess object
        """

        return Popen([executable, scriptname, '{}in.txt'.format(textfileids), '{}out.txt'.format(textfileids)],
                     stdout=PIPE, stdin=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True)

    # run a subprocess with CryptoDistribution script
    def runcryptodistribution(self):
        print("Run Distribution")
        #self.tradingenvironment.runcryptodistribution()

    #kill the CryptoDistribution subprocess
    def killcryptodistribution(self):

        self.tradingenvironment.killcryptodistribution()

    #check the status of the CryptoDistribution script
    def checkcryptodistribution(self):
        return self.tradingenvironment.checkcryptodistribution()

    #run a subprocess with PseudoAPI_Datastream script
    def runpseduoapidatastream(self):
        print("Run PseudoAPI_Datastream")
        #self.tradingenvironment.runpseduoapidatastream()

    #check the status of the PseudoAPI_Datastream script
    def checkpseudoapidatastream(self):

        self.tradingenvironment.checkpseudoapidatastream()

    #kill the PseudoAPI Datastream script
    def killpseudoapidatastream(self):

        self.tradingenvironment.killpseudoapidatastream()

    #add a new SuperTrainer subprocess to the list
    def addnewsupertrainer(self):

        self.tradingenvironment.addnewsupertrainer()

    #get the index of the newest supertrainer
    def getnewestsupertrainerindex(self):
        self.tradingenvironment.getnewestsupertrainerindex()

    #run a new SuperTrainer subprocess
    def runsupertrainer(self, indexofsupertrainertorun, paramsdictforsupertrainer):

        self.tradingenvironment.runsupertrainer(indexofsupertrainertorun, paramsdictforsupertrainer)

    # looks through the list of super trainers and removes any that have completed
    def cleanupsupertrainerlist(self):

        self.tradingenvironment.cleanupsupertrainerlist()

    # add a new subprocess to run the CryptoEvaluator script
    def addnewcryptoevaluator(self):

        self.tradingenvironment.addnewcryptoevaluator()

    # get the newest cryptoevaluator trading index
    def getnewestcryptoevaluatorindex(self):
        self.tradingenvironment.getnewestcryptoevaluatorindex()

    #run the specified CryptoEvaluator script as a subprocess
    def runcryptoevaluator(self, indexofevaluatorsubprocess, paramsdictforcryptoevaluator):

        self.tradingenvironment.runcryptoevaluator(indexofevaluatorsubprocess, paramsdictforcryptoevaluator)

    #cleanup the list of CryptoEvaluators by removing ones that have finished and returning the money they were using
    def cleanupcryptoevaluatorstrading(self):

        self.tradingenvironment.cleanupcryptoevaluatorstrading()

