# Copyright (c) 2018 A&D
# Class of different kinds of plotting functions

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import pathlib
import numpy as np
from random import randint
from CryotoGraphs import estimatefiteline, estimatevalues, errorofestimatedline
from matplotlib import colors
import os


#list of colors that can be copied into the fivethirtyeightfile
colorshex = ['008fd5', 'fc4f30', 'e5ae38', '6d904f', '8b8b8b', '810f7c', 'f2d4b6', 'f2ae1b', 'f4bbc2', '1209e0', 'dd1d36', '55b4d4', 'ff8f40', 'd35058', '252a8b', '623b19', 'b8962e', 'ff66be', '35679a', '7fffd4', '458b74', '8a2be2', 'ff4040', '8b2323', 'ffd39b', '98f5ff', '53868b', '7fff00', '458b00', 'd2691e', 'ff7256', '6495ed', 'fff8dc', '00ffff', '008b8b', 'ffb90f', '006400', 'caff70', 'ff8c00', 'cd6600', '9932cc', 'bf3eff', '8fbc8f', 'c1ffc1', '9bcd9b', '97ffff', '00ced1', '9400d3', 'ff1493', '8b0a50', '00bfff', 'b22222', 'ff3030', '228b22', 'ffd700', 'adff2f', 'ff69b4', 'ff6a6a', '7cfc00', 'bfefff', 'ee9572', '20b2aa', 'ff00ff', '66cdaa', '0000cd', 'e066ff', '00fa9a', '191970', 'b3ee3a', 'ff4500', 'ff83fa', 'bbffff', 'ff0000', '4169e1', '54ff9f', '87ceeb', 'a0522d', '836fff', '00ff7f', '008b45', '63b8ff', 'd2b48c', 'ffe1ff', 'ff6347', '8b3626', '00f5ff', '00868b', 'ee82ee', 'ff3e96', 'f5deb3', 'd02090', 'ffff00', '9acd32', '00c5cd', 'ff7256', '00cdcd', 'eead0e', '6e8b3d', 'ee7800', 'b23aee', '483d8b', '00b2ee', 'ee2c2c', 'ffc125', '00cd00', 'ee6aa7', 'ee6363', 'f08080', 'eedd82', 'ffb6c1', '87cefa', 'b03060', '3cb371', '191970', 'c0ff3e', 'db7093', '98fb98', 'ff82ab', 'cdaf95', 'ffbbff', 'b0e0e6' ]

#setup the relative file path
dirname = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dirname + '/', '')

#a class that contains different kinds of plots
class plot():

    def __init__(self, runTime, direc = filename, style = 'fivethirtyeight'):
        """
        :param runTime:
        :param direc:
        :param style:
        """
        self.runTime = runTime
        self.style = style
        self.direc = direc  + '\\' + str(runTime) + '\\'
        self.estimatedlinedict = {}
        pathlib.Path(self.direc).mkdir(parents=True, exist_ok=True)


    # plots a graph with the type of data, for the specified symbols over the whole time
    def plotlines(self, graphname, stats, symbols, type, mins, linetype = 'percentchanges', showlegend = False, figsize = (5,5), fitline = False, storedfitlinename = '', calcerrorvals = False):
        """
        :param graphname:
        :param stats:
        :param symbols:
        :param type:
        :param mins:
        :param linetype:
        :param showlegend:
        :param figsize:
        :param fitline:
        :param storedfitlinename:
        :param calcerrorvals:
        :return:
        """

        #calculated error values in case you want lines of best fit
        errorvals = {}

        #make a new figure and add it to the list of figures
        fig = plt.figure(figsize=figsize)

        #using the stored style
        style.use(self.style)

        #the linetype is either the percent change, correlation between the different types, or their normal values
        if linetype == 'percentchanges':
            stats = self.topercentchange(stats, symbols, type, start=stats.index.values[0])

        elif linetype == 'correlation':
            stats = stats.corr()

        #construct axis with just the correlation lines or percent change plotted,
        ax = plt.subplot2grid((1, 1), (0, 0))

        #if you want an estimated line of fit
        if fitline == True:
            if storedfitlinename == '':
                linesoffit = estimatefiteline(stats)

                # get the number og hex colors stored
                numcolors = len(colorshex) - 1

                # get a random value for the color
                randnum = randint(0, numcolors)

                # getting the rgba from the hex
                colorrgba = colors.to_rgba(colors.to_hex('#' + (colorshex[randnum])))

                self.estimatedlinedict.update({graphname: linesoffit, graphname + 'color': colorrgba})

                fitname = graphname + ' calculated line of best fit '

            else:
                linesoffit = self.estimatedlinedict[storedfitlinename]
                colorrgba = self.estimatedlinedict[storedfitlinename + 'color']
                fitname = storedfitlinename + ' calculated line of best fit for ' + graphname

            valuesforlines = estimatevalues(linesoffit, stats.index.values)
            linesdata = pd.DataFrame(data=valuesforlines, index=stats.index.values)
            ax_new = ax.twinx()

            ax_new.plot(linesdata, color=colorrgba, label= fitname)
            ax_new.legend(loc = 0)

        #plot the graph
        stats.plot(ax= ax, label = graphname)

        ax.legend(loc = 'upper right')

        plt.savefig(self.direc + graphname + '.png')

        if calcerrorvals:
            errorvals = errorofestimatedline(linesdata, stats)

        return errorvals

    #converts all the data into percent changes indexed at the beginning
    def topercentchange(self, data, symbols, type, start = 0):
        """
        :param data:
        :param symbols:
        :param type:
        :param start:
        :return:
        """
        for key, value in symbols.items():
            name = value + type
            data[name] = (data[name] - data[name][start]) / data[name][start] * 100.0

        return data

    # makes a list of the col headers for the type of data passed
    def getCols(self, symbolDict, typelist, compliment =False):
        """
        :param symbolDict:
        :param typelist:
        :param compliment:
        :return:
        """

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
    #bars can be organized higherst-lowest, lowest-highest, no
    def plotbar(self, graphname, stats, symbols, chosentype, showlegend = False, statistic = 'mean', barwidth = 0.35, figsize = (5,5), organizebars = 'no', histogram = False):
        """
        :param graphname:
        :param stats:
        :param symbols:
        :param chosentype:
        :param showlegend:
        :param statistic:
        :param barwidth:
        :param figsize:
        :param organizebars:
        :param histogram:
        :return:
        """

        statisticchoices = ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']

        #makes sure that the stats given are only those with the right symbol and type and statistic row
        cols = self.getCols(symbols, chosentype)
        statsdf = stats[cols]

        #get only the row corresponding to the chosen statistic
        statsdf = statsdf.loc[statistic]

        fixedsymbolslist = []
        if organizebars == 'highest-lowest':
            statsdf.sort_values( ascending=False, inplace= True)
            for col in statsdf.index.values:
                name = col.split('BTC')[0]
                fixedsymbolslist.append(name)
        elif organizebars == 'lowest-highest':
            statsdf.sort_values( ascending=True, inplace=True)
            for col in statsdf.index.values:
                name = col.split('BTC')[0]
                fixedsymbolslist.append(name)
        else:
            fixedsymbolslist = self.getcryptonameslist(symbols)

        fig = plt.figure(figsize=figsize)

        #get the number of bars we will need
        y_pos = np.arange(len(stats.columns))

        #setup the subplot for the graph
        ax = plt.subplot2grid((1,1),(0,0))


        if histogram == False:
            barlist = plt.bar(y_pos, statsdf.values, align='center', width=0.5)
        else:
            barlist = plt.bar(y_pos, statsdf.values, width=1.0)


        #get the number og hex colors stored
        numcolors = len(colorshex) - 1

        #iterate through each bar and give it a random color
        for i in range(len(barlist)):
            randnum = randint(0, numcolors)
            #hexcode string colors must be decoded
            barlist[i].set_color(colors.to_rgba(colors.to_hex('#' + (colorshex[randnum]))))

        #get the crypto names in a list
        cryptos = fixedsymbolslist

        #set the x labels to the column names
        plt.xticks(range(len(cryptos)), cryptos, size='small')

        #set the y label
        ax.set_ylabel(statistic)

        #set the title
        title = statistic + ' of ' + str(len(stats.columns)) + ' cryptos'
        ax.set_title(title)

        plt.savefig(self.direc + graphname + '.png')


    #returns a list of the names of the cryptos
    def getcryptonameslist(self, symbolsdict):
        """
        :param symbolsdict:
        :return:
        """
        list = []
        for key, value in symbolsdict.items():
            list.append(value)
        return list


