# Copyright (c) 2018 A&D
# Creates graphs for the passed intervals of data

import pandas as pd
import pickle
import plotClass
import time
import statistics
import os

from scipy.stats import chisquare
from CryptoStats import getOpenPrice, getClosePrice, getVolume, getLowPrice, getHighPrice
from math import exp, sqrt
from scipy.stats.stats import pearsonr
from scipy.stats import ttest_1samp, ttest_ind
from numpy import array_split


#the name of each crypto as the key and the value is the Binance ticker symbol
priceSymbols = {'bitcoin': 'BTCUSDT', 'ripple': "XRPBTC",
                'ethereum': 'ETHBTC', 'BCC': 'BCCBTC',
                'LTC': 'LTCBTC', 'Dash': 'DASHBTC',
                'Monero': 'XMRBTC', 'Qtum': 'QTUMBTC', 'ETC': 'ETCBTC',
                'Zcash': 'ZECBTC', 'ADA': 'ADABTC', 'ADX': 'ADXBTC', 'AION' : 'AIONBTC', 'AMB': 'AMBBTC', 'APPC': 'APPCBTC', 'ARK': 'ARKBTC', 'ARN': 'ARNBTC', 'AST': 'ASTBTC', 'BAT': 'BATBTC', 'BCD': 'BCDBTC', 'BCPT': 'BCPTBTC', 'BNB': 'BNBBTC', 'BNT': 'BNTBTC', 'BQX': 'BQXBTC', 'BRD': 'BRDBTC', 'BTS': 'BTSBTC', 'CDT': 'CDTBTC', 'CMT': 'CMTBTC', 'CND': 'CNDBTC', 'DGD': 'DGDBTC', 'DLT': 'DLTBTC', 'DNT': 'DNTBTC', 'EDO': 'EDOBTC', 'ELF': 'ELFBTC', 'ENG': 'ENGBTC', 'ENJ': 'ENJBTC', 'EOS': 'EOSBTC', 'EVX': 'EVXBTC', 'FUEL': 'FUELBTC', 'FUN': 'FUNBTC', 'GAS': 'GASBTC', 'GTO': 'GTOBTC', 'GVT': 'GVTBTC', 'GXS': 'GXSBTC', 'HSR': 'HSRBTC', 'ICN': 'ICNBTC', 'ICX': 'ICXBTC', 'IOTA': "IOTABTC", 'KMD': 'KMDBTC', 'KNC': 'KNCBTC', 'LEND': 'LENDBTC', 'LINK':'LINKBTC', 'LRC':'LRCBTC', 'LSK':'LSKBTC', 'LUN': 'LUNBTC', 'MANA': 'MANABTC', 'MCO': 'MCOBTC', 'MDA': 'MDABTC', 'MOD': 'MODBTC', 'MTH': 'MTHBTC', 'MTL': 'MTLBTC', 'NAV': 'NAVBTC', 'NEBL': 'NEBLBTC', 'NEO': 'NEOBTC', 'NULS': 'NULSBTC', 'OAX': 'OAXBTC', 'OMG': 'OMGBTC', 'OST': 'OSTBTC', 'POE': 'POEBTC', 'POWR': 'POWRBTC', 'PPT': 'PPTBTC', 'QSP': 'QSPBTC', 'RCN': 'RCNBTC', 'RDN': 'RDNBTC', 'REQ': 'REQBTC', 'SALT': 'SALTBTC', 'SNGLS': 'SNGLSBTC', 'SNM': 'SNMBTC', 'SNT': 'SNTBTC', 'STORJ': 'STORJBTC', 'STRAT': 'STRATBTC', 'SUB': 'SUBBTC', 'TNB': 'TNBBTC', 'TNT': 'TNTBTC', 'TRIG': 'TRIGBTC', 'TRX': 'TRXBTC', 'VEN': 'VENBTC', 'VIB': 'VIBBTC', 'VIBE': 'VIBEBTC', 'WABI': 'WABIBTC', 'WAVES': 'WAVESBTC', 'WINGS': 'WINGSBTC', 'WTC': 'WTCBTC', 'XVG': 'XVGBTC', 'XZC': 'XZCBTC', 'YOYO': 'YOYOBTC', 'ZRX': 'ZRXBTC'}

#dictionary of parameters
PARAMETERS = {'PERCENT_QUANTITY_TO_SPEND': 0.9, 'PERCENT_TO_SPEND': 1.0, 'MINIMUM_PERCENT_INCREASE': 5.0, 'MINIMUM_SCORE': 0.01, 'MINIMUM_MOVING_AVERAGE': .001, 'MAX_DECREASE': -10.0, 'MAX_TIME_CYCLE': 60.0, 'MAX_CYCLES': 24, 'MAX_PERCENT_CHANGE': 100.0, 'NEGATIVE_WEIGHT': 1.0, 'CUMULATIVE_PERCENT_CHANGE': 0.0, 'CUMULATIVE_PERCENT_CHANGE_STORE': 0.0, 'SLOT_WEIGHT': 1.0, 'TIME_INCREASING_MODIFIER': 1.0, 'VOLUME_INCREASING_MODIFIER': 1.0, 'PERCENT_BY_HOUR_MODIFIER': 1.0, 'VOLUME_PERCENT_BY_HOUR_MODIFIER': 1.0, 'FLOOR_PRICE_MODIFIER': 1.005, 'MODIFIED_VOLUME_MODIFIER': 1.0, 'CUMULATIVE_PRICE_MODIFIER': 1.0, 'PRIMARY_MODIFIED_VOLUME_SCALER': 1.0, 'WAIT_FOR_CHECK_FAILURE': 5.0, 'WAIT_FOR_CHECK_TOO_LOW': 10.0, 'VARIATION_NUMBER': 0.0, 'CLASS_NUM': -1, 'MIN_OFFSET': 120.0, 'INTERVAL_TO_TEST': 1440.0, 'MINUTES_IN_PAST': 0.0, 'START_MONEY': 100, 'END_MONEY': 0}

#setup the relative file path
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, '')


#the different kinds of stored
typesData = ['OpenPrice', 'ClosePrice', 'Volume', 'HighPrice', 'LowPrice']

#the ttable alphas for single tail
alphaonetail = [0.1, 0.05, 0.025, 0.01, 0.005, 0.001, 0.0005]

#the ttable alphas for double tail
alphatwotail = [0.2, 0.1, 0.05, 0.02, 0.01, 0.002, 0.001]


#reads pickle from a file
def readParamPickle(path):
    """
    :param path:
    :return:
    """

    pickle_in = open(path + '/' + "param.pkl", "rb")
    testDict = pickle.load(pickle_in)

    return testDict


#reads the pickle file for the tcritical value
def readttable(name='ttablesingle'):
    """
    :param name:
    :return:
    """
    picklefile = filename + '/' + name + '.pkl'

    with open(picklefile, "rb") as pickle_in:
       ttabledict = pickle.load(pickle_in)


    return ttabledict

#builds a line graph for the symbols passed using the specified kind of data
#plot object is class plot from plotClass.py,
def plotgraphlines(graphname, plotobject, stats, symbols, chosentype, mins = PARAMETERS['INTERVAL_TO_TEST'] +
            PARAMETERS['MIN_OFFSET'], runTime = -1, linetype = 'percentchanges', showlegend = False,
            figsize = (5,5), fitline = False, storedlinefitname = '', calcerrorvalues = False):
    """
    :param graphname:
    :param plotobject:
    :param stats:
    :param symbols:
    :param chosentype:
    :param mins:
    :param runTime:
    :param linetype:
    :param showlegend:
    :param figsize:
    :param fitline:
    :param storedlinefitname:
    :param calcerrorvalues:
    :return:
    """
    if type(chosentype) != type(''):
        print('Chosen type needs to be a single type string')

    typesData = ['OpenPrice', 'ClosePrice', 'Volume', 'HighPrice', 'LowPrice']

    #shaping the stats dictionary to only hold the requisite type of data
    for i in typesData:
        if i == chosentype:
            continue
        else:
            missingtype = i
        stats = stats[stats.columns.drop(list(stats.filter(regex=missingtype)))]

    method = plotobject.plotlines(graphname, stats, symbols, chosentype, mins, linetype , showlegend , figsize, fitline,
                                  storedlinefitname, calcerrorvalues )
    return method

#plots a bar chart
def plotbarchart(graphname, plotobject, stats, symbols, chosentype, showlegend=False, statistic = 'mean', barwidth=0.35,figsize=(5,5), organizebars = 'no', histogram=False):
    """
    :param graphname:
    :param plotobject:
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
    if type(chosentype) != type(''):
        print('Chosen type needs to be a single type string')

    typesData = ['OpenPrice', 'ClosePrice', 'Volume', 'HighPrice', 'LowPrice']

    #shaping the stats dictionary to only hold the requisite type of data
    for i in typesData:
        if i == chosentype:
            continue
        else:
            missingtype = i
        stats = stats[stats.columns.drop(list(stats.filter(regex=missingtype)))]


    method = plotobject.plotbar(graphname, stats, symbols, chosentype, showlegend, statistic, barwidth,figsize, organizebars, histogram)

    return method


#gets a dataframe with the statistics for each symbol
def getstatistics(stats, symbols, typed):
    """
    :param stats:
    :param symbols:
    :param typed:
    :return:
    """
    cols = getCols(symbols, typed)
    newdf = stats[cols]
    newdf = newdf.describe()
    return newdf

#sets up all the differnet dictionary data
def initializeData(realInterval, minutesinpast, typesofdata = typesData):
    """
    :param realInterval:
    :param minutesinpast:
    :param typesofdata:
    :return:
    """

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
def constructDataFrame(alldata, symbols, minutes, types = typesData, startmin = 0, minpast = 0):
    """
    :param alldata:
    :param symbols:
    :param minutes:
    :param types:
    :param startmin:
    :param minpast:
    :return:
    """

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

    #set the index of the passed values to account for this data starting earlier than other data
    df = df.set_index(keys=[list(range(startmin, minutes + startmin))])



    #make sure that the data is stored as floats
    df = df.astype('float')
    return df

# makes a list of the col headers for the type of data passed
def getCols(symbolDict, typelist, compliment=False):
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

#returns a line to fit for each column of the passed datafraame
#returned dictionary is of the form  {symbol: {b0: b0value, b1: b1value}}
#if alldata = true then each symbol dict includes sumx, sumx^2, n, sumy, sumxy, sumy^2, meanx, stdx, meany, stdy, p(Called correlation coefficient),
def estimatefiteline(data, allData = False):
    """
    :param data:
    :param allData:
    :return:
    """

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
    dataxs = list(data.index.values)
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
    """
    :param equationcoeffcients:
    :param allcalculateddata:
    :return:
    """

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
    """
    :param dictofalldata:
    :param yvalues:
    :param xvalues:
    :return:
    """
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
        xsqdvalues = getproductlist(xvalues, xvalues)
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
    """
    :param list1:
    :param list2:
    :return:
    """

    productlist = []

    if(len(list1) != len(list2)):
        print('Cannot get the product of two lists with different amount of elements')
        exit(1)

    for i in range(len(list1)):
        productlist.append(list1[i] * list2[i])

    return productlist


#the sum of the values in the passed list
def getsumlist(list):
    """
    :param list:
    :return:
    """
    sum = 0

    for value in list:
        sum+=float(value)

    return sum

#returns a list with the difference between each value in the passed lists
def getdifferencelist(list1, list2):
    """
    :param list1:
    :param list2:
    :return:
    """

    if(len(list1) != len(list2)):
        print('Pass two lists of the same size')
        exit(1)

    listdiffs = []
    for index in range(len(list1)):
        listdiffs.append(list1[index] - list2[index])

    return listdiffs

#returns a list with the difference between each memember of the list and the passed value
def getdifferencelistval(list, val):
    """
    :param list:
    :param val:
    :return:
    """
    listdiffs = []

    for value in list:
        listdiffs.append(value - val)

    return listdiffs

#gets the mean of the values in the list
def getmean(list):
    """
    :param list:
    :return:
    """

    sum = getsumlist(list)

    return sum / len(list)

def getrelativeerror(listoferror, realyvalueslist):
    """
    :param listoferror:
    :param realyvalueslist:
    :return:
    """


    relativepercenterror = []
    for index in range(len(listoferror)):
        if realyvalueslist[index] != 0:
            relativepercenterror.append((abs(listoferror[index]) / realyvalueslist[index]) * 100)
        else:
            relativepercenterror.append((abs(listoferror[index])) * 100)

    return relativepercenterror

#estimates the yvalues for all xvalues using the lines of best fit
def estimatevalues(lineequationdict, xvaluelist):
    """
    :param lineequationdict:
    :param xvaluelist:
    :return:
    """
    ydata = {}

    #loop through the dict of the equation information for the line equation
    for datacol, dictofdata in lineequationdict.items():
        ydata.update({datacol: []})
        #calculate a y value for each x value and store in a list corresponding to each column of data
        for xval in xvaluelist:
            estimatedyvalue = dictofdata['b1'] * xval + dictofdata['b0']
            ydata[datacol].append(estimatedyvalue)

    newdataframe = pd.DataFrame(data=ydata, index=xvaluelist)

    return newdataframe

#gets the chi-square of the passed distribution and the p value
def getchisquare(actualvalueslist, expectedvalueslist):
    """
    :param actualvalueslist:
    :param expectedvalueslist:
    :return:
    """

    if len(expectedvalueslist) == 0:
        chi2, p = chisquare(f_obs=actualvalueslist)
    else:
        chi2, p = chisquare(f_obs=actualvalueslist, f_exp=expectedvalueslist)

    return chi2, p

#returns a dictionary with the calculated error values for the estimatedlinedata and the dataset it estimatedfor
def errorofestimatedline(estimateddata, realdata):
    """
    :param estimateddata:
    :param realdata:
    :return:
    """

    cols = estimateddata.columns
    dictoferrorvalues = {}

    #go through each column of the dataframe and calculate and store each error value
    for colname in cols:
        dictoferrorvalues.update({colname: {'SSE': 0, 'SSR': 0, 'SST': 0, 'fstat': 0, 'MSE': 0, 'MSR': 0, 'R^2': 0, 'percentrelativeerror': [], 'error': []}})

        #store the y values for this column from both the real data and the estimated data
        yvalsestimated = estimateddata[colname].values
        yvaluesreal =  realdata[colname].values

        #get a list of the difference between each value in the lists
        differenceyyhatlist = getdifferencelist(yvaluesreal, yvalsestimated)
        dictoferrorvalues[colname]['error'] = differenceyyhatlist

        #square the difference
        sqddifferenceyyhat = getproductlist(differenceyyhatlist,differenceyyhatlist)

        #get the sum of the values in the list of squared differences between real y values and the estimated y values
        dictoferrorvalues[colname]['SSE'] = getsumlist(sqddifferenceyyhat)

        #get the mean
        realmean = getmean(yvaluesreal)

        #get the list of the differences between each real y value and the mean
        differenceyymean = getdifferencelistval(yvaluesreal, realmean)

        #square the difference
        sqddifferencyymean = getproductlist(differenceyymean, differenceyymean)

        #sum the squared difference between each real y value and the mean for y
        dictoferrorvalues[colname]['SST'] = getsumlist(sqddifferencyymean)

        #calculate and store the Sum of Square Regression
        dictoferrorvalues[colname]['SSR'] = dictoferrorvalues[colname]['SST'] - dictoferrorvalues[colname]['SSE']

        #calculate the relative percent error and store
        relerror = getrelativeerror(differenceyyhatlist, yvaluesreal)
        dictoferrorvalues[colname]['percentrelativeerror'] = relerror

        #calculate and store the mean sqyare error
        dictoferrorvalues[colname]['MSE'] = dictoferrorvalues[colname]['SSE'] / (len(yvaluesreal) - 2)

        #calculate and store the mean square  regression error
        dictoferrorvalues[colname]['MSR'] = dictoferrorvalues[colname]['SSR']

        #caculate the F-statistic
        dictoferrorvalues[colname]['fstat'] = dictoferrorvalues[colname]['MSR'] / dictoferrorvalues[colname]['MSE']

        #store coefficient of determination
        dictoferrorvalues[colname]['R^2'] = 1 - (dictoferrorvalues[colname]['SSE'] / dictoferrorvalues[colname]['SST'] )

    return dictoferrorvalues

#gets the lambda value
def getlambda(value):
    """
    :param value:
    :return:
    """

    return 1/value


#get the expected values for the exponential distribution considering the given lamba
def getexpectedexponentialpdf(lenlistofvalues, lambdavalue):
    """
    :param lenlistofvalues:
    :param lambdavalue:
    :return:
    """
    newpdf = []

    for x in range(lenlistofvalues):

        newpdf.append(lambdavalue * exp(-1 * lambdavalue * x))

    return newpdf

#get the expected value for the cumulative expondnetial distribution given lambda
def getexpectedexponentialcdf(listofintervals, lambdavalue):
    """
    :param listofintervals:
    :param lambdavalue:
    :return:
    """

    newcdf = []
    highend = len(listofintervals) - 1
    for x in range(1, highend):
        newcdf.append((1-exp(-1 * lambdavalue * listofintervals[x]))  - (1-exp(-1 * lambdavalue * listofintervals[x - 1])))

    return newcdf

#gets the actual expected values for an exponential distribution
def getexponentialvalues(exponentialprobabilities, samplesize):
    """
    :param exponentialprobabilities:
    :param samplesize:
    :return:
    """

    exponentiallist = []
    for val in exponentialprobabilities:
        exponentiallist.append(val * samplesize)

    return exponentiallist

#get the frequency of each value in the list
def getfreq(list):
    """
    :param list:
    :return:
    """
    sum = getsumlist(list)
    freqlist = []

    for val in list:
        freqlist.append(val/sum)

    return freqlist

#check if the x values are both equal to the valuespassed for two sets of data with the same sample size
def twosampleproportiontest(x1, x2, v1, v2, samplesize):
    """
    :param x1:
    :param x2:
    :param v1:
    :param v2:
    :param samplesize:
    :return:
    """

    #the means are converted to a p (not same thing as a p-value)
    p1 = x1/samplesize
    p2 = x2/samplesize

    #all 4 checks need to hold to continue
    if (checksforequalitytesting(p1,p2, samplesize)) == False:
        print('Did not pass the checks')
        exit(1)

    # special p0 value calculated for use in the z-stat calculation
    p0 = (x1, x2)/(samplesize*2)


    #calculation of z-stat
    zstat = ((p1 - p2) * (v1-v2)) /sqrt((p0) * (1-p0) * ((1/samplesize) + (1/samplesize)))

    return zstat

#the checks required to be passed when checking if two means are equal
def checksforequalitytesting(p1, p2, samplesize):
    """
    :param p1:
    :param p2:
    :param samplesize:
    :return:
    """
    firstcheck = (samplesize * p1) >= 5
    secondcheck = (samplesize * (1-p1)) >= 5
    thirdcheck = (samplesize * p2) >= 5
    fourthcheck = (samplesize * (1-p2)) >=5

    return (firstcheck and secondcheck and thirdcheck and fourthcheck)

#paired t-test, see if the two means are equal
def pairedttest(dataset1, dataset2, expectedmean1=0, expectedmean2=0, alpha = 0.05, diffpopulationmeans = 0, tails='ttablesingle'):
    """
    :param dataset1:
    :param dataset2:
    :param expectedmean1:
    :param expectedmean2:
    :param alpha:
    :param diffpopulationmeans:
    :param tails:
    :return:
    """
    if tails == 'ttablesingle':
        return ttest_1samp(a=dataset1, popmean=expectedmean1)
    else:
        return ttest_ind(a=dataset1, b=dataset2)

    #everything below is a work in progress to better understand the math!

    if(len(dataset1) != len(dataset2)):
        print('The two sets must be of equal length')
        exit(1)

    #get the list with the difference between each value
    differencelist = getdifferencelist(dataset1, dataset2)


    #get the degrees of freedom and number of elements
    numelements = len(dataset1)
    degreesoffreedom = numelements - 1

    #get the mean of the differences
    mean = getmean(differencelist)

    #get the standard deviation of the differences
    std = statistics.stdev(differencelist, mean)

    #get the t stat
    tstat = (mean - diffpopulationmeans) / (std * sqrt(numelements))

    #get the ttable from the picklefile
    ttable = readttable(tails)

    #get index of the alpha
    alphacolumn = getalphacol(tails, alpha)

    #in case the degreesof freedom are not in table
    if degreesoffreedom not in ttable:
        if tails == 'ttablesingle':
            return ttest_1samp(a=dataset1, popmean=expected1)
        else:
            return ttest_ind(a=dataset1, b=dataset2)


    #get the t critical for the signficance
    tcrit = ttable[degreesoffreedom][alphacolumn]

    #the boolean whether the tstat is significant
    #if t stat is significant then we fail to reject our hypothesis
    if tstat < tcrit and tstat > (-1) * tcrit:
        return True, 0.05
    else:
        return False, None

#gets the index of the alpha for the specific kind of t distribution
def getalphacol(tails='ttablesingle', alpha=0.05):
    """
    :param tails:
    :param alpha:
    :return:
    """

    if tails == 'ttablesingle':
        for i in range(len(alphaonetail)):
            if alpha == alphaonetail[i]:
                return i
    else:
        for i in range(len(alphatwotail)):
            if alpha == alphatwotail[i]:
                return i

    return -1

#the main file for my math project
def andrewProject(runTime, direc):
    """
    :param runTime:
    :param direc:
    :return:
    """

    #the symbols I chose for statistics on the mean
    symbolsformean = {'ripple': "XRPBTC",
                'ethereum': 'ETHBTC', 'BCC': 'BCCBTC',
                'LTC': 'LTCBTC', 'Dash': 'DASHBTC',
                'Monero': 'XMRBTC', 'Qtum': 'QTUMBTC', 'ETC': 'ETCBTC',
                'Zcash': 'ZECBTC'}

    #symbol for the 100 min line of percent change and then the 80 min guess
    symbolforlines = {'ripple': "XRPBTC"}



    #setting up the dictionary of parameters and the interval used to grab data
    PARAMETERS = readParamPickle(filename)
    firstInterval = 100
    guessInterval = 80
    firstminsinpast, openpriceindex = 80, 0
    secondminsinpast = 0

    # all the different types of data
    typesData = ['OpenPrice', 'ClosePrice', 'Volume', 'HighPrice', 'LowPrice']

    #the list with the string for the open price which is the kind of data that I want each type
    datatypechosen = [typesData[0]]

    #initialize our data for the mean calculations and for lines used to estimate a line
    alldatadict = initializeData(firstInterval, firstminsinpast, datatypechosen)

    graphname = symbolforlines['ripple'] + ' 0-99'

    #setup a dataframe
    data = constructDataFrame(alldatadict, symbolforlines, firstInterval, datatypechosen, minpast=secondminsinpast)


    #split the data into two halves
    firsthalfdata = array_split(data, 2)[0]
    secondhalfdata = array_split(data, 2)[1]

    #make the splits into lists
    firsthalflist = list(firsthalfdata[symbolforlines['ripple'] + datatypechosen[0]].values)
    secondhalflist = list(secondhalfdata[symbolforlines['ripple'] + datatypechosen[0]].values)

    #get the means of the two halves
    firsthalfmean = getmean(firsthalfdata.values)
    secondhalfmean = getmean(secondhalfdata.values)

    #our threshold of significance
    alpha = 0.05

    #a ttest to see if the means are equal
    tstat, pvalue = pairedttest(firsthalflist, secondhalflist, tails='ttablepair')

    #checking if the pvalue is above the significance (if it is then
    equal =  (pvalue > alpha)

    #print the means and whether they are the same
    print('Mean first half ' + str(firsthalfmean))
    print('Mean second half ' + str(secondhalfmean))
    print('Calculated t statisitc ' + str(tstat))
    print('Are they equal? ' + str(equal))
    print('P-value ' + str(pvalue))
    print('The difference between them ' + str(abs(firsthalfmean - secondhalfmean)))

    #intialize a plot class item
    plots = plotClass.plot(runTime, direc=direc)


    #sets a variable that will make the line graph reflect the open price's change from
    linetype = 'percentchanges'
    #plots the one crypto open price based on percent change from the starting index
    plotgraphlines(graphname, plots, data, symbolforlines, typesData[openpriceindex], firstInterval, runTime, linetype, showlegend = True, figsize=(10,10), fitline=True)

    #getting a list with the variable values calculated for the line of fit
    estimatedlinedata = estimatefiteline(data, allData=True)

    print("The data for the estimated line of fit " + str(estimatedlinedata))



    #this block below is for the guessing using the estimated line from part one to guess 80 min in part 2


    #initialize our data for line guessed over the next 80 min of one crypto
    alldataguess = initializeData(guessInterval,secondminsinpast, datatypechosen)

    #a second run time to distinguish the filename within the folder for the two picture files
    graphnameguess = symbolforlines['ripple'] + ' 100-179'
    #second dataframe
    guessdata = constructDataFrame(alldataguess, symbolforlines, guessInterval, datatypechosen, firstInterval, minpast=firstminsinpast)


    #sets a variable that will make the line graph reflect the open price's change from
    linetypeguess = 'percentchanges'
    #plots the one crypto open price based on percent change from the starting index (and get a dictionary with the calculated error values from the estimation using the first interval)
    errorofestimation = plotgraphlines(graphnameguess, plots, guessdata, symbolforlines, typesData[openpriceindex], guessInterval, runTime, linetypeguess, showlegend = True, figsize=(10,10), fitline=True, storedlinefitname=graphname, calcerrorvalues=True)

    print("The error information " + str(errorofestimation[symbolforlines['ripple'] + datatypechosen[0]]))

    print('The mean of the relative percent error ' + str(
        getmean(errorofestimation[symbolforlines['ripple'] + datatypechosen[0]]['percentrelativeerror'])))

    #all data for 9 cryptos for the mean
    #setup a dataframe
    dataforstats = constructDataFrame(alldatadict, symbolsformean, firstInterval, datatypechosen)

    cols = dataforstats.columns
    for col in cols:
        print(getmean(dataforstats[col]))

    graphname = 'MeanOPB'
    stats = {}
    #this block below is to do bar charts using the mean of the nine cryptos
    statsformeandataframe = getstatistics(dataforstats, symbolsformean, [typesData[openpriceindex]])
    statisticsformean = {typesData[openpriceindex]: statsformeandataframe}
    #optimization to grab the statistics for the open price of the data
    stats.update(statisticsformean)
    #setup bar charts for open price of the data (only using means and uses multiple cryptos)
    bardf = stats[typesData[openpriceindex]]
    plotbarchart(graphname, plots, bardf, symbolsformean , chosentype=typesData[openpriceindex], showlegend=False, figsize=(20,10), organizebars= 'highest-lowest', histogram=True)

    #data frame of the means
    meandf = bardf.loc['mean']

    #get the row with the means from the dataframe
    listmeans = list(meandf.values)

    #sort list of means
    listmeans.sort(reverse=True)

    #get frequency
    meanfreqs = getfreq(listmeans)

    #get the mean of all the means in the list
    meanofallmeans = getmean(listmeans)

    #get the lambda value for the exponential distribution
    lamba = getlambda(meanofallmeans)

    #use lambda to get the expected value probability if the distribution were exponential
    expectedvaluesprob = getexpectedexponentialpdf(len(meanfreqs), lamba)

    #get the expected values
    expectedvalues = getexponentialvalues(expectedvaluesprob, len(meanfreqs))

    print('All the means ' + str(listmeans))

    print('Mean of means ' + str(meanofallmeans))




#function used for homework
def homeworktest():
    """
    :return:
    """
    rubberdata = pd.DataFrame({'col1': [20, 20.75, 45.5, 42.5, 58, 56]}, index=[135, 135, 150, 150, 165, 165])
    pingpongdata = pd.DataFrame({'col1': [16, 13, 33, 34, 44.75, 40]}, index=[135,135,150,150,165,165])

    rubberdatacalc = estimatefiteline(rubberdata, True)
    pingpongdatacalc = estimatefiteline(pingpongdata, True)


def main():
    runTime = time.time() * 1000


if __name__ == "__main__":
    main()
