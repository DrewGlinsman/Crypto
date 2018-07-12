# Copyright (c) 2018 A&D
# Different functions to fill priceSymbols with the right symbol list from the specified website

import os
import requests
from Generics import readpickle, writepickle

from Generics import priceSymbols

#setup the relative file path
dirname = os.path.dirname(os.path.realpath(__file__))

#grab the latest symbols for available cryptos from Binance
def updatePriceSymbolsBinance(list=False, store=False):
    """
    :param list: if you want a list or not
    :param store: if you want to store the pricesymbols
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

        if store:
            writepickle(newsymbolslist, dirname, 'binancelist.pkl')

        return newsymbolslist

    else:
        count = 0
        for individualsymbol in symboltable:
            if('BTC' in individualsymbol['symbol'] ):
                newsymbols.update({individualsymbol['symbol']:individualsymbol['symbol']})
                count+=1

        if store:
            writepickle(newsymbols, dirname, 'binancedict.pkl')

        return newsymbols

def chooseUpdate(websitename, list=False, store=False):
    """
    :param websitename: the name of the website we want the price symbols from
    :param list: whether you want just a list of strings or a dict
    :param store: whether you want to store the newest symbols as a picklefile
    :return: the priceSymbols returned by the right updater
    """

    if (websitename == 'binance'):
        return updatePriceSymbolsBinance(list=list, store=store)
    else:
        print("Not implemented website")

def getStoredSymbols(websitename, directory, list=False):
    """
    :param websitename: the name of the website symbols you want to retrieve
    :param directory: the directory where the pickle files are stored
    :param list: whether these are list or dictionary stored symbols
    :return: the stored symbols for the specified website
    """

    if list:
        symbols = readpickle(directory, "{}list.pkl".format(websitename))
    else:
        symbols = readpickle(directory, "{}dict.pkl".format(websitename))

    return symbols

def main():
    chooseUpdate('binance')




if __name__ == '__main__':
    main()