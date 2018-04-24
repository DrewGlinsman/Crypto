# Copyright (c) 2018 A&D
# Creates graphs for the passed intervals of data

import pandas as pd
import pickle
from CryptoStats import getOpenPrice, getClosePrice, getVolume, getLowPrice, getHighPrice
import plotClass
import time
import statistics

from scipy.stats.stats import pearsonr

#the name of each crypto as the key and the value is the Binance ticker symbol
priceSymbols = {'bitcoin': 'BTCUSDT', 'ripple': "XRPBTC",
                'ethereum': 'ETHBTC', 'BCC': 'BCCBTC',
                'LTC': 'LTCBTC', 'Dash': 'DASHBTC',
                'Monero': 'XMRBTC', 'Qtum': 'QTUMBTC', 'ETC': 'ETCBTC',
                'Zcash': 'ZECBTC', 'ADA': 'ADABTC', 'ADX': 'ADXBTC', 'AION' : 'AIONBTC', 'AMB': 'AMBBTC', 'APPC': 'APPCBTC', 'ARK': 'ARKBTC', 'ARN': 'ARNBTC', 'AST': 'ASTBTC', 'BAT': 'BATBTC', 'BCD': 'BCDBTC', 'BCPT': 'BCPTBTC', 'BNB': 'BNBBTC', 'BNT': 'BNTBTC', 'BQX': 'BQXBTC', 'BRD': 'BRDBTC', 'BTS': 'BTSBTC', 'CDT': 'CDTBTC', 'CMT': 'CMTBTC', 'CND': 'CNDBTC', 'CTR':'CTRBTC', 'DGD': 'DGDBTC', 'DLT': 'DLTBTC', 'DNT': 'DNTBTC', 'EDO': 'EDOBTC', 'ELF': 'ELFBTC', 'ENG': 'ENGBTC', 'ENJ': 'ENJBTC', 'EOS': 'EOSBTC', 'EVX': 'EVXBTC', 'FUEL': 'FUELBTC', 'FUN': 'FUNBTC', 'GAS': 'GASBTC', 'GTO': 'GTOBTC', 'GVT': 'GVTBTC', 'GXS': 'GXSBTC', 'HSR': 'HSRBTC', 'ICN': 'ICNBTC', 'ICX': 'ICXBTC', 'IOTA': "IOTABTC", 'KMD': 'KMDBTC', 'KNC': 'KNCBTC', 'LEND': 'LENDBTC', 'LINK':'LINKBTC', 'LRC':'LRCBTC', 'LSK':'LSKBTC', 'LUN': 'LUNBTC', 'MANA': 'MANABTC', 'MCO': 'MCOBTC', 'MDA': 'MDABTC', 'MOD': 'MODBTC', 'MTH': 'MTHBTC', 'MTL': 'MTLBTC', 'NAV': 'NAVBTC', 'NEBL': 'NEBLBTC', 'NEO': 'NEOBTC', 'NULS': 'NULSBTC', 'OAX': 'OAXBTC', 'OMG': 'OMGBTC', 'OST': 'OSTBTC', 'POE': 'POEBTC', 'POWR': 'POWRBTC', 'PPT': 'PPTBTC', 'QSP': 'QSPBTC', 'RCN': 'RCNBTC', 'RDN': 'RDNBTC', 'REQ': 'REQBTC', 'SALT': 'SALTBTC', 'SNGLS': 'SNGLSBTC', 'SNM': 'SNMBTC', 'SNT': 'SNTBTC', 'STORJ': 'STORJBTC', 'STRAT': 'STRATBTC', 'SUB': 'SUBBTC', 'TNB': 'TNBBTC', 'TNT': 'TNTBTC', 'TRIG': 'TRIGBTC', 'TRX': 'TRXBTC', 'VEN': 'VENBTC', 'VIB': 'VIBBTC', 'VIBE': 'VIBEBTC', 'WABI': 'WABIBTC', 'WAVES': 'WAVESBTC', 'WINGS': 'WINGSBTC', 'WTC': 'WTCBTC', 'XVG': 'XVGBTC', 'XZC': 'XZCBTC', 'YOYO': 'YOYOBTC', 'ZRX': 'ZRXBTC'}

#dictionary of parameters
PARAMETERS = {'PERCENT_QUANTITY_TO_SPEND': 0.9, 'PERCENT_TO_SPEND': 1.0, 'MINIMUM_PERCENT_INCREASE': 5.0, 'MINIMUM_SCORE': 0.01, 'MINIMUM_MOVING_AVERAGE': .001, 'MAX_DECREASE': -10.0, 'MAX_TIME_CYCLE': 60.0, 'MAX_CYCLES': 24, 'MAX_PERCENT_CHANGE': 100.0, 'NEGATIVE_WEIGHT': 1.0, 'CUMULATIVE_PERCENT_CHANGE': 0.0, 'CUMULATIVE_PERCENT_CHANGE_STORE': 0.0, 'SLOT_WEIGHT': 1.0, 'TIME_INCREASING_MODIFIER': 1.0, 'VOLUME_INCREASING_MODIFIER': 1.0, 'PERCENT_BY_HOUR_MODIFIER': 1.0, 'VOLUME_PERCENT_BY_HOUR_MODIFIER': 1.0, 'FLOOR_PRICE_MODIFIER': 1.005, 'MODIFIED_VOLUME_MODIFIER': 1.0, 'CUMULATIVE_PRICE_MODIFIER': 1.0, 'PRIMARY_MODIFIED_VOLUME_SCALER': 1.0, 'WAIT_FOR_CHECK_FAILURE': 5.0, 'WAIT_FOR_CHECK_TOO_LOW': 10.0, 'VARIATION_NUMBER': 0.0, 'CLASS_NUM': -1, 'MIN_OFFSET': 120.0, 'INTERVAL_TO_TEST': 1440.0, 'MINUTES_IN_PAST': 0.0, 'START_MONEY': 100, 'END_MONEY': 0}

#the final part of the directory base
addOnPath = 'Crypto\\'

#the different kinds of stored
typesData = ['OpenPrice', 'ClosePrice', 'Volume', 'HighPrice', 'LowPrice']


#reads pickle from a file
def readParamPickle(path):
    logPaths = r'C:\Users\katso\Documents\GitHub\\' + path
    pickle_in = open(logPaths + '\\' + "param.pkl", "rb")
    testDict = pickle.load(pickle_in)

    return testDict

#builds a graph for the symbols passed using the specified kind of data
#plot object is class plot from plotClass.py
#graphtype options are 'lines', 'bar' (look the params statements to see which ones they each need)
def plotData(graphname, plotobject, stats, symbols, chosentype, mins = PARAMETERS['INTERVAL_TO_TEST'] + PARAMETERS['MIN_OFFSET'], runTime = -1, linetype = 'percentchanges', showlegend = False, graphtype = 'lines', statistic = 'mean', barwidth = 0.35, figsize = (5,5)):
    params = []

    if type(chosentype) != type(''):
        print('Chosen type needs to be a single type string')

    #setting up the name of the
    func = 'plot' + graphtype

    typesData = ['OpenPrice', 'ClosePrice', 'Volume', 'HighPrice', 'LowPrice']

    #shaping the stats dictionary to only hold the requisite type of data
    for i in typesData:
        if i == chosentype:
            continue
        else:
            missingtype = i
        stats = stats[stats.columns.drop(list(stats.filter(regex=missingtype)))]

    if graphtype == 'lines':
        params = [graphname, stats, symbols, chosentype, mins, linetype, showlegend, figsize]
    elif graphtype == 'bar':
        params = [graphname, stats, symbols, chosentype, showlegend, statistic, barwidth,figsize]

    #make and call the method using the class, function name, and the list of parameters
    method = getattr(plotobject, func)(*params)

#gets a dataframe with the statistics for each symbol
def getstatistics(stats, symbols, typed):
    cols = getCols(symbols, typed)
    newdf = stats[cols]
    newdf = newdf.describe()
    return newdf

#sets up all the differnet dictionary data
def initializeData(realInterval, minutesinpast, typesofdata = typesData):

    #go thorugh all the kinds of data that can be chosen, if the datatype was chosen then call the appropriate statsfunction
    listofdata = {}
    for i in range(len(typesData)):
        #if the data type passed is the same as the type of data in this index of the list of all data then
        #construct a call name for its Cryptostats get function and then call it and set it in the dictionary
        #of return data
        if typesData[i] in typesofdata:
            callname = 'get' + typesData[i]
            newdata = globals()[callname](realInterval, minutesinpast, {})
            listofdata.update({typesData[i]: newdata})

    return listofdata
#creates dataframe only for the dataframe that is passed
def constructDataFrame(alldata, symbols, minutes, types = typesData):

    cols = getCols(symbols, types)
    df = pd.DataFrame(columns=cols)
    rowlist = []

    #getting each row of data and appending it to the bottom of the dataframe
    for i in range(int(minutes)):
        rowlist[:] = []
        for key, value in symbols.items():
            for dataname in types:
                try:
                    rowlist.append(alldata[dataname][value][i])
                except KeyError:
                    print('That was not a valid key. Make sure all types of data in types are stored in allData')
                    exit(1)

        newrow = pd.Series(data=rowlist, index=cols)
        df = df.append(newrow, ignore_index=True)

    #make sure that the data is stored as floats
    df = df.astype('float')
    return df

# makes a list of the col headers for the type of data passed
def getCols(symbolDict, typelist, compliment=False):
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

#returns a line to fit for each column of the passed datafraame
#returned dictionary is of the form  {symbol: {b0: b0value, b1: b1value}}
#if alldata = true then each symbol dict includes sumx, sumx^2, n, sumy, sumxy, sumy^2, meanx, stdx, meany, stdy, p(Called correlation coefficient),
def estimatefiteline(data, allData = False):
    #the list of the different normally stored equation data
    listofequations = {}
    #the list of different equation data plus the extra data if allData = True
    equationsandintermediatedata = {}

    #list of columns in the passed dataframe
    collist = data.columns

    #the number of columns
    colnum = len(collist)

    #the stored x and y values for all data
    #all xs are the same!
    dataxs = range(len(data.index.values))
    datays = {}

    #setting up a dictionary entry for each column of data from the dataframe passed in the y data dict, the basic data
    # stored dictionary and the dictionary of all the data calculated
    for colname in collist:
        datays.update({colname: []})
        listofequations.update({colname: {'b0': 0, 'b1':0}})
        equationsandintermediatedata.update({colname: {'b0': 0, 'b1':0, 'sumx':0, 'sumx^2': 0, 'n': 0, 'sumy': 0, 'sumxy': 0, 'sumy^2': 0,
                                                       'meanx': 0 , 'stdx': 0, 'meany': 0, 'stdy': 0, 'correlationcoefficient': 0 , 'pvalue': 0}})

    #iterate through each row and index
    for index, row in data.iterrows():
        currentcol = 0
        #iterate through the values in the row
        for val in row:
            #add the values as y data to each of the y data list of the columns they corresponded to
            datays[collist[currentcol]].append(val)
            currentcol+=1


    #calculate and populate the dictionary with all intermediate data
    populatecalculatedvaluesdict(equationsandintermediatedata, datays, dataxs)

    #calculate and make the b0 and b1 values for the systems of equations
    calculateb0andb1(listofequations, equationsandintermediatedata)

    if allData:
        return equationsandintermediatedata

    return listofequations

#calcualates and stores b0 and b1 for each estimated line
# of the form y = b0 + b1x for the data
def calculateb0andb1(equationcoeffcients, allcalculateddata):

    for currencyname, dicofdata in equationcoeffcients.items():
        #set local variables equal to the corresponding variables in allcalculateddata for clarity
        correlationcoefficient = allcalculateddata[currencyname]['correlationcoefficient']
        standarddeviationx = allcalculateddata[currencyname]['stdx']
        standarddeviationy = allcalculateddata[currencyname]['stdy']
        meanx = allcalculateddata[currencyname]['meanx']
        meany = allcalculateddata[currencyname]['meany']

        #calculate b0 and b1
        b1 =((correlationcoefficient) * (standarddeviationy / standarddeviationx))
        b0 = meany - b1 * meanx

        #store b0 and b1 in both dicitonariesthat have been passed
        equationcoeffcients[currencyname]['b0'] = b0
        allcalculateddata[currencyname]['b0'] = b0

        equationcoeffcients[currencyname]['b1'] = b1
        allcalculateddata[currencyname]['b1'] = b1

#populates the dictionaries of calculated equation values with the correct calulations
def populatecalculatedvaluesdict(dictofalldata, yvalues, xvalues):

    #iterate through the dictionary that contains all the calculated stats for the estimation of a line
    for currencyname, dictofdata in dictofalldata.items():

        #get sum of x values
        dictofdata['sumx'] = getsumlist(xvalues)

        #get sum of y values
        dictofdata['sumy'] = getsumlist(yvalues[currencyname])

        #get sum of xyvalues
        xyvalues = getproductlist(yvalues[currencyname], xvalues)
        dictofdata['sumxy'] = getsumlist(xyvalues)

        #get sum of x^2 values
        xsqdvalues = getproductlist(xyvalues, xyvalues)
        dictofdata['sumx^2']  = getsumlist(xsqdvalues)

        #get sum of y^2 values
        ysqdvalues = getproductlist(yvalues[currencyname], yvalues[currencyname])
        dictofdata['sumy^2'] = getsumlist(ysqdvalues)

        #get the number of datapoints
        dictofdata['n'] = len(xvalues)

        #get the mean of the x values
        dictofdata['meanx']  = (dictofdata['sumx'] / dictofdata['n'])

        #get the mean of the y values
        dictofdata['meany'] = (dictofdata['sumy'] / dictofdata['n'])

        #get standard deviation of the x values
        dictofdata['stdx'] = statistics.stdev(xvalues, xbar=dictofdata['meanx'])

        #get standard deviation of the y values
        dictofdata['stdy'] = statistics.stdev(yvalues[currencyname], xbar=dictofdata['meany'])

        #get the correlation coefficient
        dictofdata['correlationcoefficient'], dictofdata['pvalue'] = pearsonr(xvalues, yvalues[currencyname])


#get product of two lists past and return
def getproductlist(list1, list2):
    productlist = []

    if(len(list1) != len(list2)):
        print('Cannot get the product of two lists with different amount of elements')
        exit(1)

    for i in range(len(list1)):
        productlist.append(list1[i] * list2[i])

    return productlist


#the sum of the values in the passed list
def getsumlist(list):
    sum = 0

    for value in list:
        sum+=value

    return sum


#the main file for my math project
def andrewProject(runTime, direc):
    #the symbols I chose for statistics on the mean
    symbolsformean = {'ripple': "XRPBTC",
                'ethereum': 'ETHBTC', 'BCC': 'BCCBTC',
                'LTC': 'LTCBTC', 'Dash': 'DASHBTC',
                'Monero': 'XMRBTC', 'Qtum': 'QTUMBTC', 'ETC': 'ETCBTC',
                'Zcash': 'ZECBTC'}

    #symbol for the 100 min line of percent change and then the 80 min guess
    symbolforlines = {'ripple': "XRPBTC"}



    #setting up the dictionary of parameters and the interval used to grab data
    PARAMETERS = readParamPickle(addOnPath)
    firstInterval = 100
    guessInterval = 80
    firstminsinpast, openpriceindex = 0, 0
    secondminsinpast = 100

    # all the different types of data
    typesData = ['OpenPrice', 'ClosePrice', 'Volume', 'HighPrice', 'LowPrice']

    #the list with the string for the open price which is the kind of data that I want each type
    datatypechosen = [typesData[0]]


    #initialize our data for the mean calculations and for lines used to estimate a line
    alldatadict = initializeData(firstInterval, firstminsinpast, datatypechosen)

    graphname = 'realOPPC'

    #setup a dataframe
    data = constructDataFrame(alldatadict, symbolforlines, firstInterval, datatypechosen)

    #intialize a plot class item
    plots = plotClass.plot(runTime, direc=direc)


    #sets a variable that will make the line graph reflect the open price's change from
    linetype = 'percentchanges'
    #plots the one crypto open price based on percent change from the starting index
    plotData(graphname, plots, data, symbolforlines, typesData[openpriceindex], firstInterval, runTime, linetype, showlegend = True, figsize=(10,10))

    #getting a list with the variable values calculated for the line of fit
    estimatedlinedata = estimatefiteline(data, symbolforlines)


    #this block below is for the guessing using the estimated line from part one to guess 80 min in part 2


    #initialize our data for line guessed over the next 80 min of one crypto
    alldataguess = initializeData(guessInterval,secondminsinpast, datatypechosen)

    #a second run time to distinguish the filename within the folder for the two picture files
    graphname = 'GuessOPPC'
    #second dataframe
    guessdata = constructDataFrame(alldataguess, symbolforlines, guessInterval, datatypechosen)


    #sets a variable that will make the line graph reflect the open price's change from
    linetypeguess = 'percentchanges'
    #plots the one crypto open price based on percent change from the starting index
    plotData(graphname, plots, guessdata, symbolforlines, typesData[openpriceindex], guessInterval, runTime, linetypeguess, showlegend = True, figsize=(10,10))


    #all data for 9 cryptos for the mean
    #setup a dataframe
    dataforstats = constructDataFrame(alldatadict, symbolsformean, firstInterval, datatypechosen)

    graphname = 'MeanOPB'
    stats = {}
    #this block below is to do bar charts using the mean of the nine cryptos
    statsformeandataframe = getstatistics(dataforstats, symbolsformean, [typesData[openpriceindex]])
    statisticsformean = {typesData[openpriceindex]: statsformeandataframe}
    #optimization to grab the statistics for the open price of the data
    stats.update(statisticsformean)
    #setup bar charts for open price of the data (only using means and uses multiple cryptos)
    bardf = stats[typesData[openpriceindex]]
    plotData(graphname, plots, bardf, symbolsformean , chosentype=typesData[openpriceindex], showlegend=False, graphtype='bar', figsize=(10,10))


def main():
    runTime = time.time() * 1000

    andrewProject(runTime, direc = r'C:\Users\katso\Documents\GitHub\Crypto\Andrewproj\\')

if __name__ == "__main__":
    main()
