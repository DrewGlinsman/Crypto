# Copyright (c) 2018 A&D
#Class with error codes for the CryptoEvaluator

from Generics import defaulterrorflagsforcryptoevaluator

class ErrorCodesCryptoEvaluator:


    def __init__(self):
        #the dictionary with the error flags
        self.errorflagsdict = self.setuperrorflagsdict()

    def setuperrorflagsdict(self):
        return defaulterrorflagsforcryptoevaluator

    def printflags(self):
        for errorflagname, errorflagvalue in self.errorflagsdict.items():
            print("Error flag: {}".format(errorflagname))
            print("Error flag value: {}".format(errorflagvalue))


    def setflag(self, flagname, setval):
        self.errorflagsdict.update({flagname: setval})

    def getvalueofflag(self, flagname):
        return self.errorflagsdict[flagname]

    def resetflags(self):
        for flagname, flagvalue in self.errorflagsdict.items():
            self.errorflagsdict.update({flagname: False})
