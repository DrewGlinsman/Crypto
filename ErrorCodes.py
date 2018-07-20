# Copyright (c) 2018 A&D
#Class with error codes for each script that needs them

from ErrorCodesCryptoEvaluator import ErrorCodesCryptoEvaluator

class ErrorCodes:

    def __init__(self, scriptname):
        """
        :param scriptname:
        """
        self.errocodesclass = self.geterrorcodesclass(scriptname)


    @property
    def errorflags(self):
        return self.geterrorflagsdict()

    def geterrorcodesclass(self, scriptname):
        return self.possibleerrorcodesclasses[scriptname]

    @property
    def possibleerrorcodesclasses(self):
        return {'CryptoEvaluator': ErrorCodesCryptoEvaluator()}

    def geterrorflagsdict(self):

        return self.errocodesclass.errorflagsdict

    def setflag(self, flagname, setval):
        self.errocodesclass.setflag(flagname, setval)

    def getvalueofflag(self, flagname):
        return self.errocodesclass.getvalueofflag(flagname)

    def resetflags(self):
        self.errocodesclass.resetflags()

    def printflags(self):
        self.errocodesclass.printflags()