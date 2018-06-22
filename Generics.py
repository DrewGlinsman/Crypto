# Copyright (c) 2018 A&D
# has general use versions of certain common variables


# the name of each crypto as the key and the value is the Binance ticker symbol
priceSymbols = {'bitcoin': 'BTCUSDT', 'ripple': "XRPBTC",
                'ethereum': 'ETHBTC', 'BCC': 'BCCBTC',
                'LTC': 'LTCBTC', 'Dash': 'DASHBTC',
                'Monero': 'XMRBTC', 'Qtum': 'QTUMBTC', 'ETC': 'ETCBTC',
                'Zcash': 'ZECBTC', 'ADA': 'ADABTC', 'ADX': 'ADXBTC', 'AION': 'AIONBTC', 'AMB': 'AMBBTC', 'APPC': 'APPCBTC', 'ARK': 'ARKBTC', 'ARN': 'ARNBTC', 'AST': 'ASTBTC', 'BAT': 'BATBTC', 'BCD': 'BCDBTC', 'BCPT': 'BCPTBTC', 'BNB': 'BNBBTC', 'BNT': 'BNTBTC', 'BQX': 'BQXBTC', 'BRD': 'BRDBTC', 'BTS': 'BTSBTC', 'CDT': 'CDTBTC', 'CMT': 'CMTBTC', 'CND': 'CNDBTC', 'DGD': 'DGDBTC', 'DLT': 'DLTBTC', 'DNT': 'DNTBTC', 'EDO': 'EDOBTC', 'ELF': 'ELFBTC', 'ENG': 'ENGBTC', 'ENJ': 'ENJBTC', 'EOS': 'EOSBTC', 'EVX': 'EVXBTC', 'FUEL': 'FUELBTC', 'FUN': 'FUNBTC', 'GAS': 'GASBTC', 'GTO': 'GTOBTC', 'GVT': 'GVTBTC', 'GXS': 'GXSBTC', 'HSR': 'HSRBTC', 'ICN': 'ICNBTC', 'ICX': 'ICXBTC', 'IOTA': "IOTABTC", 'KMD': 'KMDBTC', 'KNC': 'KNCBTC', 'LEND': 'LENDBTC', 'LINK': 'LINKBTC', 'LRC': 'LRCBTC', 'LSK': 'LSKBTC', 'LUN': 'LUNBTC', 'MANA': 'MANABTC', 'MCO': 'MCOBTC', 'MDA': 'MDABTC', 'MOD': 'MODBTC', 'MTH': 'MTHBTC', 'MTL': 'MTLBTC', 'NAV': 'NAVBTC', 'NEBL': 'NEBLBTC', 'NEO': 'NEOBTC', 'NULS': 'NULSBTC', 'OAX': 'OAXBTC', 'OMG': 'OMGBTC', 'OST': 'OSTBTC', 'POE': 'POEBTC', 'POWR': 'POWRBTC', 'PPT': 'PPTBTC', 'QSP': 'QSPBTC', 'RCN': 'RCNBTC', 'RDN': 'RDNBTC', 'REQ': 'REQBTC', 'SALT': 'SALTBTC', 'SNGLS': 'SNGLSBTC', 'SNM': 'SNMBTC', 'SNT': 'SNTBTC', 'STORJ': 'STORJBTC', 'STRAT': 'STRATBTC', 'SUB': 'SUBBTC', 'TNB': 'TNBBTC', 'TNT': 'TNTBTC', 'TRIG': 'TRIGBTC', 'TRX': 'TRXBTC', 'VEN': 'VENBTC', 'VIB': 'VIBBTC', 'VIBE': 'VIBEBTC', 'WABI': 'WABIBTC', 'WAVES': 'WAVESBTC', 'WINGS': 'WINGSBTC', 'WTC': 'WTCBTC', 'XVG': 'XVGBTC', 'XZC': 'XZCBTC', 'YOYO': 'YOYOBTC', 'ZRX': 'ZRXBTC'}
# the binance intervals, their symbols, and their time in milliseconds
intervalTypes = {'1m': {'symbol': '1m', 'inMS': 60000}, '3m': {'symbol': '3m', 'inMS': 180000}, '5m': {'symbol': '5m', 'inMS': 300000}, '15m': {'symbol': '15m', 'inMS': 900000}, '30m': {'symbol': '30m', 'inMS': 1800000}, '1h': {'symbol': '1h', 'inMS': 3600000}, '2h': {'symbol': '2h', 'inMS': 7200000}, '4h': {'symbol': '4h', 'inMS': 14400000}, '6h': {'symbol': '6h', 'inMS': 21600000}, '8h': {'symbol': '8h', 'inMS': 28800000}, '12h': {'symbol': '12h', 'inMS': 43200000}, '1d': {'symbol': '1d', 'inMS': 86400000}, '3d': {'symbol': '3d', 'inMS': 259200000}, '1w': {'symbol': '1w', 'inMS': 604800000}, '1M': {'symbol': '1M', 'inMS': 2629746000}}

# EXPLANATION OF THE PARAMETERS
#todo remember that the wait parameters for this one should be different from the ones in auto trader where they are in seconds not minutes

# PERCENT_QUANTITY_TO_SPEND: the amount of the balance calculated to be spent that we can spend (based on the small fee) #todo look more at why this exists
# PERCENT_TO_SPEND: the amount of the balance of bitcoin to spend. Should be calculated by how many bots are made
# MINIMUM_PERCENT_INCREASE: lowest percent increase for a cryptocurrency to be considered in the start of the bot
# MINIMUM_SCORE: the lowest score for a crypto to be addded to the list of scores to be checked for the remaineder of a run
# MINIMUM_MOVING_AVERAGE: the lowest moving average for a crypto score to be considered
# MAX_DECREASE: the maximum allowed decrease over a short (<15m) interval
# MAX_TIME_CYCLE: the maximum time the bot will run for in ticks (they are counted by a incrementing variable)
# MAX_CYCLES: the maximum amount of times the bot will buy and sell
# CYCLES: the actual number of times the bot bought and sold
# MAX_PERCENT_CHANGE: the highest % increase and the lowest % decrease a crypto can have over the life of owning it before an auto reevaluation
# NEGATIVE_WEIGHT: weight applied to negative percent price or percent volume change
# CUMULATIVE_PERCENT_CHANGE: the cumulative % change of a crypto's price over the course of owning it
# CUMULATIVE_PERCENT_CHANGE_STORE: the cumulative percent change over the course of owning several cryptos
# SLOT_WEIGHT: weight applied to each slot of the intervals being checked to see if they the crypto was increasing or decreasing
# TIME_INCREASING_MODIFIER: the unweighted time increasing modifier (time increasing is the count of intervals where the price was increasing)
# VOLUME_INCREASING_MODIFIER: the volume increasing modifier (volume increasing is the count of intervals where the volume traded increased)
# PERCENT_BY_HOUR_MODIFIER: the modifier for the total percent change of a crypto over a longer interval (> 1hr)
# VOLUME_PERCENT_BY_HOUR_MODIFIER: the modifier for the volume percent change over a longer interval (> 1hr)
# FLOOR_PRICE_MODIFIER: the lowest % change above the original price the crypto was bought at before the bot auto sells it (calculated later than the other failure conditions to catch a decreasing price)
# MODIFIED_VOLUME_MODIFIER: the cumulative volume change based on the % change by interval scale
# CUMULATIVE_PRICE_MODIFIER: the cumulative price change modifier for the weighted moving average
# PRIMARY_MODIFIED_VOLUME_SCALER: the scaler to make more volume traded have the same sign as the percent change in the price than the amount that is counted as having the opposite sign
# WAIT_FOR_CHECK_FAILURE: the number of ticks before the failure condition is checked (the crypto is decreasing over the past 10 minutes)
# WAIT_FOR_CHECK_TOO_LOW: the number of ticks before ethe program checks to see if a crypto has decreased too low to its starting point
# VARIATION_NUMBER: number stored for what variation on the bot this is, 0 base
# CLASS_NUM: number stored for the class, 0 means no class, 1 and up are the actual classes
# MINOFFSET: the number of minutes before the beginning of the interval of data that the bot can look back to
# INTERVAL_TO_TEST: the interval over which the bot will be tested (think hour, day, week etc...); used with the crypto evaluator
# MINUTES_IN_PAST: how far back you want the end point of the test to be
# START_MONEY: the amount of money in $ the bot starts with
# END_MONEY: the amount of money in $ the bot ends with
PARAMETERS = {'PERCENT_QUANTITY_TO_SPEND': 0.9, 'PERCENT_TO_SPEND': 1.0, 'MINIMUM_PERCENT_INCREASE': 5.0, 'MINIMUM_SCORE': 0.01,
              'MINIMUM_MOVING_AVERAGE': .001, 'MAX_DECREASE': -10.0, 'MAX_TIME_CYCLE': 60.0, 'MAX_CYCLES': 24, 'CYCLES': 0,
              'MAX_PERCENT_CHANGE': 100.0, 'NEGATIVE_WEIGHT': 1.0, 'CUMULATIVE_PERCENT_CHANGE': 0.0, 'CUMULATIVE_PERCENT_CHANGE_STORE': 0.0,
              'SLOT_WEIGHT': 1.0, 'TIME_INCREASING_MODIFIER': 1.0, 'VOLUME_INCREASING_MODIFIER': 1.0, 'PERCENT_BY_HOUR_MODIFIER': 1.0,
              'VOLUME_PERCENT_BY_HOUR_MODIFIER': 1.0, 'FLOOR_PRICE_MODIFIER': 1.005, 'MODIFIED_VOLUME_MODIFIER': 1.0,
              'CUMULATIVE_PRICE_MODIFIER': 1.0, 'PRIMARY_MODIFIED_VOLUME_SCALER': 1.0, 'WAIT_FOR_CHECK_FAILURE': 5.0,
              'WAIT_FOR_CHECK_TOO_LOW': 10.0, 'VARIATION_NUMBER': 0.0, 'CLASS_NUM': -1, 'MIN_OFFSET': 120.0, 'INTERVAL_TO_TEST': 1440.0,
              'MINUTES_IN_PAST': 0.0, 'START_MONEY': 100, 'END_MONEY': 0}

UNCHANGED_PARAMS = ['PERCENT_QUANTITY_TO_SPEND', 'PERCENT_TO_SPEND', 'MAX_TIME_CYCLE', 'MAX_CYCLES', 'CYCLES', 'CUMULATIVE_PERCENT_CHANGE',
                    'CUMULATIVE_PERCENT_CHANGE_STORE', 'WAIT_FOR_CHECK_FAILURE', 'WAIT_FOR_CHECK_TOO_LOW', 'VARIATION_NUMBER', 'CLASS_NUM',
                    'MIN_OFFSET', 'INTERVAL_TO_TEST', 'MINUTES_IN_PAST', 'START_MONEY', 'END_MONEY', 'MAX_PERCENT_CHANGE', 'MAX_DECREASE']


# dictionaires for the modes this can be run in
modes = {'SoloEvaluator': {'string': 'SoloEvaluator', 'value': 0}, 'SoloTrainer': {'string': 'SoloTrainer', 'value': 1}, 'MultiTrainer': {'string': 'MultiTrainer', 'value': 2}}

# website names that we can run the bot to train on and trade on
websites = {'binance': 'binance'}

"""
Trainers test the current set of params, and then all other variations of the params using a large spread and small
spread method of changing params (i.e. one might change them with numbers between 10 and 20 while the other tries
1000 and 2000). Each has a possible % chance of resulting in a particular parameter being changed. 
smallrange: the smaller range of values in magnitude 
bigrange: the bigger range of values in magnitude
lowoffirstrange: the lower bound of the small range
lowofsecondrange: the lower bound of the big range
randcheckrangeone: the random number that we will use to create a number that we will generate as the bet for each param (say 10) 
randcheckrangetwo: the random number (for the second kind of randomization) that we will use to create a number for the bet 
lowercheckthreshold: the integer that the bet for the first parameter has to be higher than for the change to happen
uppercheckthreshold: the integer that the bet for the second parameter has to be higher thna for the change to happen
classes: the number of classes of bots that will be trained by the trainer that uses this parameter file
variations: the number of variations of bots that will be in each class trained
mode: the mode used for the log system so that error logs are stored properly
modevalue: the numeric value associated with the mode (also used for logs)
percentpositivebots: the percentage of the bots produced using this supertrainer parameter set that ended with positive results
worstbotreturnsaved: the return % of the worst bot that was saved
bestbotreturnsaved: the return % of the best bot that was saved
maxbotsstored: the number of bots that will be stored from this trainer's class (so if =10 then the top ten are stored)
MAX_TIME_CYCLE: the maximum minutes a cycle (one trade) can run for
MAX_CYCLES: the maximum number of cycles that will occur before the bot quits trading
MIN_CYCLES: the minimum number of cycles for a bot variation to be chosen over the current best bot variation
WAIT_FOR_CHECK_FAILURE: the time in minutes before we check if the currency has incured too much loss in the specified time
WAIT_FOR_CHECK_TOO_LOW: the time in minutes before we check if the item purchased is too near its starting value
MAX_PERCENT_CHANGE: the percentage that will set off this failure flag (corresponds to a positive value reached or a low value reached at any point in the life of holding an item)
MIN_OFFSET: the minutes in the past we will collect data for high and low prices to be checked against (useful when we have to check an x number of minutes in past and cannot because the simulation just started running and there is no data gathered)
INTERVAL_TO_TEST: the number of minutes that we will train the bot on
MINUTES_IN_PAST: the number of minutes that the bot will go back in the past to mark as the end point of the simulation (so =0 means that the simulation ends at the most recent minute passsed)
MAX_DECREASE: the maximum percent decrease allowed before the bot auto stops trading
"""
# the parameters used by the supertrainer given to each trainer
superParams = {'smallrange': 10,'bigrange': 100, 'lowoffirstrange': 0, 'lowofsecondrange': 50, 'randcheckrangeone': 10,'randcheckrangetwo': 50, 'lowercheckthreshold': 5,
                'uppercheckthreshold': 7, 'classes': 1, 'variations': 1, 'mode': 'MultiTrainer', 'modevalue': 2,
               'percentpositivebots': 0, 'worstbotreturnsaved': 0, 'bestbotreturnedsaved': 0, 'maxbotsstored': 1,
               'MAX_TIME_CYCLE': 60.0, 'MAX_CYCLES': 24, 'MIN_CYCLES': 4, 'WAIT_FOR_CHECK_FAILURE': 5.0, 'WAIT_FOR_CHECK_TOO_LOW': 10.0,
               'MAX_PERCENT_CHANGE': 100.0, 'MIN_OFFSET': 120.0, 'INTERVAL_TO_TEST': 1440.0, 'MINUTES_IN_PAST': 0.0,
               'MAX_DECREASE': -10.0}

# parameters that the superTrainer should not change
unchangedSuperParams = ['MIN_OFFSET', 'INTERVAL_TO_TEST', 'MINUTES_IN_PAST']

maxVolume = 7000

#superparameters that have to be changed specially (the inner lists are the groups that get changed by the same value at the same time)
specialSuperParams = [['smallrange', 'bigrange', 'lowoffirstrange', 'lowofsecondrange', 'randcheckrangeone', 'randcheckrangetwo',
                      'lowercheckthreshold', 'uppercheckthreshold'],['classes'],['variations'], ['MIN_CYCLES', 'MAX_CYCLES']]

#each group of special params has the range that is used to vary them here
specialRange = [10,10,10,2]

#special parameters used by the trainers that can be neither negative nor zero
nonnegorzero = ['classes', 'variations']

#the minimum amount of superTrainer files
minSuperFiles = 10

#the default values for the passed supertrainer params
defaultsuperparamspassed = {'website': 'binance', 'day': 'monday', 'numsessions': 10, 'oldidnummax': 10, 'hour': 9, 'min': 00}

#default values for the passsed parameters to a cryptotrainer file
defaulttrainerparamspassed = {'website': 'binance', 'day': 'monday', 'hour': 9, 'min': 0, 'idnum': 1, 'originalid': 1}

#TODO implement a stored param for ALL levels that is 'lossallowed'
#input values that are stored for each evaluator (other than parameters)
storedInput = {'website': 'binance', 'day': 'monday', 'hour': 9, 'min': 0, 'classNum': -1, 'variationNum': -1,  'idnum': 0}

#parameters passed to the datastream pseudo api
datastreamparamspassed = {'website': 'binance',  'mins': 0, 'minmax': 1440, 'hourstoprime': 0, 'freshrun': False}

################################# GENERIC FUNCTIONS ##########################################
#just calculates the percent change between two values
def calcPercentChange(startVal, endVal):
    """
    :param startVal:
    :param endVal:
    :return:
    """
    if(float(startVal) == 0.0):
        return float(endVal) * 100.0

    return (((float(endVal) - float(startVal))/float(startVal) ) * 100)

#set either the key to lower case, the values to lower case, or both

def getLowerCaseDict(dict, key=True, value = True):
    """
    :param dict: the dictionary to be made lower case
    :param key: whether the key will be made lowercase
    :param value: whether the value will be made lowercase
    :return: the new lowercase dictionary
    """

    lowercase = {}
    if(key and value):
        for k, v in dict.items():
            lowercase.update({k.lower(): v.lower()})
    elif(key and value == False):
        for k, v in dict.items():
            lowercase.update({k.lower(): v})
    elif(key == False and value):
        for k, v in dict.items():
            lowercase.update({k: v.lower()})
    else:
        return dict

    return lowercase

