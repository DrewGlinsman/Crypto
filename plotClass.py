# Copyright (c) 2018 A&D
# Class of different kinds of plotting functions

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import pathlib
import numpy as np


#a class that contains different kinds of plots
class plot():

    def __init__(self, runTime, direc = r'C:\Users\katso\Documents\GitHub\Crypto\\', style = 'fivethirtyeight'):
        self.runTime = runTime
        self.style = style
        self.direc = direc  + '\\' + str(runTime) + '\\'
        pathlib.Path(self.direc).mkdir(parents=True, exist_ok=True)


    # plots a graph with the type of data, for the specified symbols over the whole time
    def plotlines(self, stats, symbols, type, mins, linetype = 'percentchanges', showlegend = False, figsize = (5,5)):
        #make a new figure and add it to the list of figures
        fig = plt.figure(figsize=figsize)

        #using the stored style
        style.use(self.style)

        #the linetype is either the percent change, correlation between the different types, or their normal values
        if linetype == 'percentchanges':
            stats = self.topercentchange(stats, symbols, type)

        elif linetype == 'correlation':
            stats = stats.corr()

        #construct axis with just the correlation lines or percent change plotted,
        #if  volume put volume on top
        ax = plt.subplot2grid((1, 1), (0, 0))
        stats.plot(ax= ax)

        plt.legend().remove()
        plt.savefig(self.direc + type + linetype + '.png')



    #converts all the data into percent changes indexed at the beginning
    def topercentchange(self, data, symbols, type, start = 0):
        for key, value in symbols.items():
            name = value + type
            data[name] = (data[name] - data[name][start]) / data[name][start] * 100.0

        return data

    # makes a list of the col headers for the type of data passed
    def getCols(self, symbolDict, typelist, compliment =False):
        cols = []
        if type(typelist) != type([]):
            typelist = [typelist]

        if compliment == False:
            for key, value in symbolDict.items():
                for i in typelist:
                    cols.append(str(value + i))

        else:
            alltypes = ['OpenPrice', 'ClosePrice', 'Volume', 'HighPrice', 'LowPrice']
            for key, value in symbolDict.items():
                for i in alltypes:
                    if i not in typelist:
                        cols.append((str(value) + i))

        return cols

    #makes a bar chart displaying the different statistics gathered on each crypto, can isolate one kind
    def plotbar(self, stats, symbols, chosentype, showlegend = False, statistic = 'mean', barwidth = 0.35, figsize = (5,5)):
        statisticchoices = ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']

        #makes sure that the stats given are only those with the right symbol and type and statistic row
        cols = self.getCols(symbols, chosentype)
        statsdf = stats[cols]
        #get only the row corresponding to the chosen statistic
        statsdf = statsdf.loc[statistic]
        fig = plt.figure(figsize=figsize)

        #get the number of bars we will need
        y_pos = np.arange(len(stats.columns))

        #setup the subplot for the graph
        ax = plt.subplot2grid((1,1),(0,0))

        plt.bar(y_pos, statsdf.values, align='center')

        #get the crypto names in a list
        cryptos = self.getcryptonameslist(symbols)
        #set the x labels to the column names
        ax.set_xticklabels(labels=cryptos)

        #set the y label
        ax.set_ylabel(statistic)

        #set the title
        title = statistic + ' of ' + str(len(stats.columns)) + ' cryptos'
        ax.set_title(title)

        plt.savefig(self.direc + chosentype + statistic + str(len(stats.columns)) + 'bar' + '.png')


    #returns a list of the names of the cryptos
    def getcryptonameslist(self, symbolsdict):
        list = []
        for key, value in symbolsdict.items():
            list.append(value)
        return list


