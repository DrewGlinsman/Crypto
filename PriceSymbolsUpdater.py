# Copyright (c) 2018 A&D
# Different functions to fill priceSymbols with the right symbol list from the specified website

import os
import requests

from Generics import priceSymbols

#setup the relative file path
dirname = os.path.dirname(os.path.realpath(__file__))

def updatePriceSymbolsBinance(list=False):
    """
    :param list: if you want a list or not
    :return: the update priceSymbols
    """
    newsymbols = {}
    newsymbolslist = []

    data = requests.get("https://api.binance.com/api/v1/exchangeInfo")

    data = data.json()

    #grab the symbols
    symboltable = data['symbols']

    if(list):
        count = 0
        for individualsymbol in symboltable:
            if('BTC' in individualsymbol['symbol'] ):
                newsymbolslist.append(individualsymbol['symbol'])
                count+=1
        return newsymbolslist

    else:
        count = 0
        for individualsymbol in symboltable:
            if('BTC' in individualsymbol['symbol'] ):
                newsymbols.update({individualsymbol['symbol']:individualsymbol['symbol']})
                count+=1

        return newsymbols

def chooseUpdate(websitename, list=False):
    """
    :param websitename: the name of the website we want the price symbols from
    :param list: whether you want just a list of strings or a dict
    :return: the priceSymbols returned by the right updater
    """

    if (websitename == 'binance'):
        return updatePriceSymbolsBinance(list=list)
    else:
        print("Not implemented website")


def main():
    chooseUpdate('binance')




if __name__ == '__main__':
    main()