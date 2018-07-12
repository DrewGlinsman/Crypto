# Copyright (c) 2018 A&D
# has general use versions of certain common variables

import os
import pathlib
import pickle as pkl

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
"""
 PERCENT_QUANTITY_TO_SPEND: the amount of the balance calculated to be spent that we can spend (based on the small fee) #todo look more at why this exists
 PERCENT_TO_SPEND: the amount of the balance of bitcoin to spend. Should be calculated by how many bots are made
 MINIMUM_PERCENT_INCREASE: lowest percent increase for a cryptocurrency to be considered in the start of the bot
 MINIMUM_SCORE: the lowest score for a crypto to be addded to the list of scores to be checked for the remaineder of a run
 MINIMUM_MOVING_AVERAGE: the lowest moving average for a crypto score to be considered
 MAX_DECREASE: the maximum allowed decrease over a short (<15m) interval
 MAX_TIME_CYCLE: the maximum time the bot will run for in ticks (they are counted by a incrementing variable)
 MAX_CYCLES: the maximum amount of times the bot will buy and sell
 CYCLES: the actual number of times the bot bought and sold
 MAX_PERCENT_CHANGE: the highest % increase and the lowest % decrease a crypto can have over the life of owning it 
    before an auto reevaluation
 NUM_TIMES_INCREASING_MIN_FAILURE_FLAG_VALUE: the number of times that an crypto price must be increasing  (at least)
    or a failure flag is set off and it is auto sold
 MODIFIED_VOLUME_NEGATIVE_MODIFIER: weight applied to negative modified volume values  
 PRICE_TIME_INCREASING_NEGATIVE_WEIGHTED_MODIFIER: the weight applied to negative price time increasing slots 
    (for weighted calculation)
 PRICE_TIME_INCREASING_NEGATIVE_UNWEIGHTED_MODIFIER: the weight applied to negative price time increasing slots 
    (for unweighted calculations)
 VOLUME_TIME_INCREASING_NEGATIVE_WEIGHTED_MODIFIER: the weight applied to negative volume time increasing slots 
    (for weighted calculations)
 VOLUME_TIME_INCREASING_NEGATIVE_UNWEIGHTED_MODIFIER: the weight applied to negative volume time increasing slots 
    (for unweighted calculations)
 CUMULATIVE_PERCENT_CHANGE: the cumulative % change of a crypto's price over the course of owning it
 CUMULATIVE_PERCENT_CHANGE_STORE: the cumulative percent change over the course of owning several cryptos
 PRICE_TIME_INCREASING_SLOT_WEIGHTED_MODIFIER:: weight applied to each slot of the intervals being checked to see if  
    price was increasing or decreasing (for weighted calculations)
 PRICE_TIME_INCREASING_SLOT_UNWEIGHTED_MODIFIER:: weight applied to each slot of the intervals being checked to see 
    if price was increasing or decreasing (for unweighted calculations)
 VOLUME_TIME_INCREASING_SLOT_WEIGHTED_MODIFIER:: the weight applied to each slot of the intervals being checked to see 
    if the volume was increasing or decreasing (for weighted calculations)
 VOLUME_TIME_INCREASING_SLOT_UNWEIGHTED_MODIFIER:: the weight applied to each slot of the intervals being checked to 
    see if the volume was increasing or decreasing (for unweighted calculations)
 PRICE_TIME_INCREASING_WEIGHTED_MODIFIER: the weighted time increasing modifier 
    (time increasing is the count of intervals where the price was increasing) 
 PRICE_TIME_INCREASING_UNWEIGHTED_MODIFIER: the unweighted time increasing modifier
 VOLUME_TIME_INCREASING_WEIGHTED_MODIFIER: the volume increasing modifier for weighted calculations 
    (volume increasing is the count of intervals where the volume traded increased) 
 VOLUME_TIME_INCREASING_UNWEIGHTED_MODIFIER: the volume increasing modifier for unweighted calculations
 PERCENT_BY_HOUR_OPEN_CLOSE_MODIFIER: the modifier for the total percent change between the open and close price
 PERCENT_BY_HOUR_HIGH_LOW_MODIFIER: the modifier for the total percent change between the high and low price
 PERCENT_BY_HOUR_OPEN_HIGH_MODIFIER: the modifier for the total percent change between open and high prices 
 PERCENT_BY_HOUR_OPEN_LOW_MODIFIER: the modifier for the total percent change between open and low prices
 PERCENT_BY_HOUR_HIGH_CLOSE_MODIFIER: the modifier for the total percent change between high and close prices
 PERCENT_BY_HOUR_LOW_CLOSE_MODIFIER: the modifier for the total percent change between close and low prices
 VOLUME_PERCENT_BY_HOUR_MODIFIER: the modifier for the volume percent change 
 MINS_SINCE_LAST_HIGH_PRICE_MODIFIER: the modifier for the number of minutes since the highest high price was found
 MINS_SINCE_LAST_LOW_PRICE_MODIFIER: the modifier for the number of minutes since the lowest low price was found
 TIMES_REACH_OR_SURPASS_HIGH_PRICE_MODIFIER: the modifier for the number of times the high price has been matched or surpassed
 TIMES_REACH_OR_FALL_BELOW_LOW_PRICE_MODIFIER: the modifier for the number of times the low price has been matched or fallen below
 DIFF_HIGH_AND_LOW_PRICE_OVERALL_MODIFIER: the modifier for the relative difference between the highest high price and the lowest low price
 FLOOR_PRICE_MODIFIER: the lowest % change above the original price the crypto was bought at before the bot auto sells it 
    (calculated later than the other failure conditions to catch a decreasing price)
 MODIFIED_VOLUME_MODIFIER: the cumulative volume change based on the % change by interval scale
 CUMULATIVE_PRICE_MODIFIER: the cumulative price change modifier for the weighted moving average
 PRIMARY_MODIFIED_VOLUME_SCALER: the scaler to make more volume traded have the same sign as the percent change in the 
    price than the amount that is counted as having the opposite sign
 WAIT_FOR_CHECK_FAILURE: the number of ticks before the failure condition is checked (the crypto is decreasing over 
    the past 10 minutes)
 WAIT_FOR_CHECK_TOO_LOW: the number of ticks before ethe program checks to see if a crypto has decreased too low to 
    its starting point
 VARIATION_NUMBER: number stored for what variation on the bot this is, 0 base
 CLASS_NUM: number stored for the class, 0 means no class, 1 and up are the actual classes
 MINOFFSET: the number of minutes before the beginning of the interval of data that the bot can look back to
 INTERVAL_TO_TEST: the interval over which the bot will be tested (think hour, day, week etc...); used with the 
    crypto evaluator
 MINUTES_IN_PAST: how far back you want the end point of the test to be
 START_MONEY: the amount of money in $ the bot starts with
 END_MONEY: the amount of money in $ the bot ends with #TODO ADD IN MODIFIERS FOR OPEN PRICE AND CLOSE PRICE
"""
PARAMETERS = {'PERCENT_QUANTITY_TO_SPEND': 0.9, 'PERCENT_TO_SPEND': 1.0, 'MINIMUM_PERCENT_INCREASE': 5.0,
              'MINIMUM_SCORE': 0.000001,'MINIMUM_MOVING_AVERAGE': .000001, 'MAX_DECREASE': -10.0, 'MAX_TIME_CYCLE': 60.0,
              'MAX_CYCLES': 24, 'CYCLES': 0, 'MAX_PERCENT_CHANGE': 100.0,
              'NUM_TIMES_INCREASING_MIN_FAILURE_FLAG_VALUE': 0,
              'MODIFIED_VOLUME_NEGATIVE_MODIFIER': 1.0,
              'PRICE_TIME_INCREASING_NEGATIVE_WEIGHTED_MODIFIER': 1.0,
              'PRICE_TIME_INCREASING_NEGATIVE_UNWEIGHTED_MODIFIER': 1.0,
              'VOLUME_TIME_INCREASING_NEGATIVE_WEIGHTED_MODIFIER': 1.0,
              'VOLUME_TIME_INCREASING_NEGATIVE_UNWEIGHTED_MODIFIER': 1.0,
              'CUMULATIVE_PERCENT_CHANGE': 0.0, 'CUMULATIVE_PERCENT_CHANGE_STORE': 0.0,
              'PRICE_TIME_INCREASING_SLOT_WEIGHTED_MODIFIER': 1.0,
              'PRICE_TIME_INCREASING_SLOT_UNWEIGHTED_MODIFIER': 1.0,
              'VOLUME_TIME_INCREASING_SLOT_WEIGHTED_MODIFIER': 1.0,
              'VOLUME_TIME_INCREASING_SLOT_UNWEIGHTED_MODIFIER': 1.0,
              'PRICE_TIME_INCREASING_WEIGHTED_MODIFIER': 1.0, 'PRICE_TIME_INCREASING_UNWEIGHTED_MODIFIER': 1.0,
              'VOLUME_TIME_INCREASING_WEIGHTED_MODIFIER': 1.0, 'VOLUME_TIME_INCREASING_UNWEIGHTED_MODIFIER': 1.0,
              'PERCENT_BY_HOUR_OPEN_CLOSE_MODIFIER': 1.0, 'PERCENT_BY_HOUR_HIGH_LOW_MODIFIER': 1.0,
              'PERCENT_BY_HOUR_OPEN_HIGH_MODIFIER': 1.0, 'PERCENT_BY_HOUR_OPEN_LOW_MODIFIER': 1.0,
              'PERCENT_BY_HOUR_HIGH_CLOSE_MODIFIER': 1.0, 'PERCENT_BY_HOUR_LOW_CLOSE_MODIFIER': 1.0,
              'VOLUME_PERCENT_BY_HOUR_MODIFIER': 1.0, 'MINS_SINCE_LAST_HIGH_PRICE_MODIFIER': 1.0,
              'MINS_SINCE_LAST_LOW_PRICE_MODIFIER': 1.0, 'TIMES_REACH_OR_SURPASS_HIGH_PRICE_MODIFIER': 1.0,
              'TIMES_REACH_OR_FALL_BELOW_LOW_PRICE_MODIFIER': 1.0, 'DIFF_HIGH_AND_LOW_PRICE_OVERALL_MODIFIER': 1.0,
              'FLOOR_PRICE_MODIFIER': 1.005, 'MODIFIED_VOLUME_MODIFIER': 1.0,
              'CUMULATIVE_PRICE_MODIFIER': 1.0, 'PRIMARY_MODIFIED_VOLUME_SCALER': 1.0, 'WAIT_FOR_CHECK_FAILURE': 5.0,
              'WAIT_FOR_CHECK_TOO_LOW': 10.0, 'VARIATION_NUMBER': 0.0, 'CLASS_NUM': -1, 'MIN_OFFSET': 120.0, 
              'INTERVAL_TO_TEST': 1440.0, 'MINUTES_IN_PAST': 0.0, 'START_MONEY': 100, 'END_MONEY': 100,
              'COMBINED_PARAMS': [], 'COMBINED_PARAMS_MODIFIERS': []}


#any lists stored in the parameters that have to be iterated through and randomized individually
listparms = ['COMBINED_PARAMS', 'COMBINED_PARAMS_MODIFIERS']

#parameters used by CryptoEvaluator that are specifically ignored when randomizing
UNCHANGED_PARAMS = ['PERCENT_QUANTITY_TO_SPEND', 'PERCENT_TO_SPEND' , 'MAX_DECREASE', 'MAX_TIME_CYCLE', 'MAX_CYCLES', 
                    'CYCLES','MAX_PERCENT_CHANGE', 'NUM_TIMES_INCREASING_MIN_FAILURE_FLAG_VALUE',
                    'CUMULATIVE_PERCENT_CHANGE','CUMULATIVE_PERCENT_CHANGE_STORE',
                    'WAIT_FOR_CHECK_FAILURE', 'WAIT_FOR_CHECK_TOO_LOW','VARIATION_NUMBER', 'CLASS_NUM','MIN_OFFSET', 
                    'INTERVAL_TO_TEST', 'MINUTES_IN_PAST', 'START_MONEY', 'END_MONEY']

#names for different calculations to be stored and used to find the max in the bots with each update
#the max of each of these values is used to normalize each value for scoring (and for the scores themselves)
#any new calculation to be included in the score for a crypto MUST be added here so that they can be normalized
#i.e. make each value relative to the maximum value for each calculation
#TODO if not work add 'Score' back in (should not be necessary)
normalizationValuesToStore = ['PERCENT_BY_HOUR_OPEN_CLOSE', 'PERCENT_BY_HOUR_HIGH_LOW', 
                              'PERCENT_BY_HOUR_OPEN_HIGH', 'PERCENT_BY_HOUR_OPEN_LOW',
                              'PERCENT_BY_HOUR_HIGH_CLOSE', 'PERCENT_BY_HOUR_LOW_CLOSE',
                              'VOLUME_PERCENT_BY_HOUR', 'PRICE_TIME_INCREASING_UNWEIGHTED',
                              'PRICE_TIME_INCREASING_WEIGHTED', 'VOLUME_TIME_INCREASING_WEIGHTED', 
                              'VOLUME_TIME_INCREASING_UNWEIGHTED', 'MINS_SINCE_LAST_HIGH_PRICE',
                              'MINS_SINCE_LAST_LOW_PRICE', 'TIMES_REACH_OR_SURPASS_HIGH_PRICE',
                              'TIMES_REACH_OR_FALL_BELOW_LOW_PRICE', 'DIFF_HIGH_AND_LOW_PRICE_OVERALL',
                              'MODIFIED_VOLUME']

#parameters that can be combined and considered (set to the normalization values stored for the score because
# those should be the only ones that can be combined)
paramsthatcanbecombined = normalizationValuesToStore

#the list of data types to be persistently stored between updateCrypto runs, because the data is normally overwritten after
#it is passed to CryptoStatAnalysis
persistentdataforscoretypenames = ['HIGHEST_HIGH_PRICE', 'LOWEST_LOW_PRICE', 'MINS_SINCE_LAST_HIGH_PRICE',
                                   'MINS_SINCE_LAST_LOW_PRICE', 'TIMES_REACH_OR_SURPASS_HIGH_PRICE',
                                   'TIMES_REACH_OR_FALL_BELOW_LOW_PRICE']

# cryptos seperated by decision into those disregarded, those chosen but not making final cut because of their mean,
# those selected that have the appropriate mean, and the crypto that is chosen, has the right mean, and is the max
implicitcryptodivisions = {'Disregarded': [], 'Chosen': [], 'chosenButCut': [], 'chosenNotCut': [], 'theMax': []}


# dictionaires for the modes this can be run in (At the moment not used)
modes = {'SoloEvaluator': {'string': 'SoloEvaluator', 'value': 0}, 'SoloTrainer': {'string': 'SoloTrainer', 'value': 1},
         'MultiTrainer': {'string': 'MultiTrainer', 'value': 2}}

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
randcheckrangeone: the random number that we will use to create a number that we will generate as the bet for each param 
    (say 10) 
randcheckrangetwo: the random number (for the second kind of randomization) that we will use to create a number for the 
    bet 
lowercheckthreshold: the integer that the bet for the first parameter has to be higher than for the change to happen
uppercheckthreshold: the integer that the bet for the second parameter has to be higher than for the change to happen
upperstopcheckthreshold: the integer set that a random value must be above to add/remove parameters from the set of 
combined parameters if the first type of randomization is chosen
upperremovecheckthreshold: the integer set that a random value must be above to add a parameter to the set of combined
    parameters if the first type of randomization is chosen (if below then the parameter is removed)
lowerstopcheckthreshold: the integer set that a random value must be above to add/remove parameters from the set of 
    combined parameters if the second type of randomization is chosen
lowerremovecheckthreshold: the integer set that a random value must be above to add a parameter to the set of combined
    parameters if the second type of randomization is chosen (if below then the parameter is removed)
classes: the number of classes of bots that will be trained by the trainer that uses this parameter file
variations: the number of variations of bots that will be in each class trained
percentpositivebots: the percentage of the bots produced using this trainer parameter set that ended 
    with positive results
percentnegativebots: the percentage of the bots produced using this trainer parameter set that ended 
    with negative results
worstbotreturnsaved: the return % of the worst bot produced in the last run
bestbotreturnsaved: the return % of the best bot produced in the last run
averagebotreturnsaved: the return % of the average bot produced in the last run
MAX_TIME_CYCLE: the maximum minutes a cycle (one trade) can run for
MAX_CYCLES: the maximum number of cycles that will occur before the bot quits trading
MIN_CYCLES: the minimum number of cycles for a bot variation to be chosen over the current best bot variation
WAIT_FOR_CHECK_FAILURE: the time in minutes before we check if the currency has incured too much loss in the 
    specified time
WAIT_FOR_CHECK_TOO_LOW: the time in minutes before we check if the item purchased is too near its starting value
MAX_PERCENT_CHANGE: the percentage that will set off this failure flag (corresponds to a positive value reached or 
    a low value reached at any point in the life of holding an item)
MIN_OFFSET: the minutes in the past we will collect data for high and low prices to be checked against (useful when 
    we have to check an x number of minutes in past and cannot because the simulation just started running and 
    there is no data gathered)
INTERVAL_TO_TEST: the number of minutes that we will train the bot on
MINUTES_IN_PAST: the number of minutes that the bot will go back in the past to mark as the end point of the simulation 
    (so =0 means that the simulation ends at the most recent minute passsed)
MAX_DECREASE: the maximum percent decrease allowed before the bot auto stops trading
replacementvalue: the number of the checks that a trainer needs to be better than its predecessor to
    replace its predecesssor
NUM_TIMES_INCREASING_MIN_FAILURE_FLAG_VALUE: the number of times that an crypto price must be increasing  (at least)
    or a failure flag is set off and it is auto sold
maxcombinedparams: the maximum number of combined parameters
maxparameterscombinedpercombinedparam:the maximum number of parameters that can be combined per combined parameter
"""
# the parameters used by the supertrainer given to each trainer
superParams = {'smallrange': 2,'bigrange': 15, 'lowoffirstrange': 0, 'lowofsecondrange': 0, 'randcheckrangeone': 10,
               'randcheckrangetwo': 50, 'lowercheckthreshold': 5,'uppercheckthreshold': 7, 'upperstopcheckthreshold': 2,
               'upperremovecheckthreshold' : 4, 'lowerstopcheckthreshold' : 2, 'lowerremovecheckthreshold' : 4,
               'classes': 1, 'variations': 1, 'percentpositivebots': 0, 'percentnegativebots': 0,
               'worstbotreturnsaved': 0, 'bestbotreturnsaved': 0, 'averagebotreturnsaved': 0, 'MAX_TIME_CYCLE': 60.0,
               'MAX_CYCLES': 24, 'MIN_CYCLES': 4, 'WAIT_FOR_CHECK_FAILURE': 5.0, 'WAIT_FOR_CHECK_TOO_LOW': 10.0,
               'MAX_PERCENT_CHANGE': 100.0, 'MIN_OFFSET': 120.0, 'INTERVAL_TO_TEST': 1440.0, 'MINUTES_IN_PAST': 0.0,
               'MAX_DECREASE': -10.0, 'replacementvalue': 0, 'NUM_TIMES_INCREASING_MIN_FAILURE_FLAG_VALUE': 0,
               'maxcombinedparams': 3, 'maxparameterscombinedpercombinedparam': 3}

# parameters that the superTrainer should not change
unchangedSuperParams = ['MIN_OFFSET', 'INTERVAL_TO_TEST', 'MINUTES_IN_PAST', 'percentpositivebots',
                        'percentnegativebots','worstbotreturnsaved', 'bestbotreturnsaved', 'averagebotreturnsaved']

#the parameters checked to determine which cryptoTrainer is better between a set of two
checkCryptoTrainerPerformance = [ 'percentpositivebots',
                        'percentnegativebots','worstbotreturnsaved', 'bestbotreturnsaved', 'averagebotreturnsaved']

maxVolume = 7000

#superparameters that have to be changed specially (the inner lists are the groups that get changed by the same value at the same time)
specialSuperParams = [['smallrange', 'bigrange', 'lowoffirstrange', 'lowofsecondrange', 'randcheckrangeone', 'randcheckrangetwo',
                      'lowercheckthreshold', 'uppercheckthreshold', 'upperstopcheckthreshold', 'upperremovecheckthreshold',
                       'lowerstopcheckthreshold', 'lowerremovecheckthreshold'],['classes'],['variations'], ['MIN_CYCLES', 'MAX_CYCLES'],
                      ['replacementvalue'], ['NUM_TIMES_INCREASING_MIN_FAILURE_FLAG_VALUE']]

#each group of special params has the range that is used to vary them here
specialRange = [10,10,10,2,5,10]

#special parameters used by the trainers that can be neither negative nor zero (only need to identify the first
# parameter in the corresponding inner list within the specialSuperParams list)
nonnegorzero = ['classes', 'variations', 'replacementvalue']

#special parameters used by the trainers that cannot be negative (only need to identify the first parameter
# in the corresponding inner list within the specialSuperParams list)
nonnegative = ['NUM_TIMES_INCREASING_MIN_FAILURE_FLAG_VALUE']

#parameters identified to add the random value when randomizing instead of setting the new value to the random value
#(only need to identify the first parameter in the corresponding inner list within the specialSuperParams list)
addRandVal = ['smallrange', 'MIN_CYCLES']

#the minimum amount of Trainer files (superParams)
minSuperFiles = 10

#the minimum amount of Evaluator files (baseparams)
minEvaluatorFiles = 20

#The default values for the passed supertrainer params
#website: the website used to gather data, train on, and buy/sell on
#day: the day of the week this was TRAINED on
#numsessions: the number of trainers we want to use (think of this like the number of classrooms in a school)
#oldidnummax: the number of trainers that will be used and not randomized before training
#hour: the hour this was trained on
#min: the min this was trained on
#lossallowed: the percentage loss allowed for every buy/sell decision
defaultsuperparamspassed = {'directoryprefix': 'SuperTrainer','website': 'binance', 'day': 'monday', 'numsessions': 10,
                            'oldidnummax': 5, 'hour': 9, 'min': 00, 'lossallowed': -1}

#Default values for the passsed parameters to a cryptotrainer file
#website: the website used to gather data, train on, and buy/sell on
#day: the day of the week this was TRAINED on
#hour: the hour this was trained on
#min: the min this was trained on
#idnum: the id number that this trainer is stored with IN THE TRAINING DIRECTORY (so this could differ from its original id
# since trainers are essentially grabbed at random by the super trainer)
#originalid: the id number that this trainer came from (i.e. the id its original version is stored under in the STORAGE DIRECTORY)
#evalID: the id number of the evaluator that this trainer will use to generate its classes and variations for training
# so essentially in the storage each trainer gets a set of evaluator parameter files and with each training session it will
# choose one to vary and optimize
#lossallowed: the percentage loss allowed for every buy/sell decision
defaulttrainerparamspassed = {'directoryprefix': 'CryptoTrainer','website': 'binance', 'day': 'monday', 'hour': 9,
                              'min': 0, 'idnum': 1, 'originalid': 1,'evalID': 0, 'lossallowed': -1}


#Input values that are stored for each evaluator (other than parameters)
#website: the website used to gather data, train on, and buy/sell on
#day: the day of the week this was TRAINED on
#hour: the hour this was trained on
#min: the min this was trained on
#classNum: the class number that this bot is stored in THE TRAINING DIRECTORY
#variationNum: the number indicating what number has been assigned to it in the TRAINING DIRECTORY within a particular class
#idnum: the id number that this trainer is stored with IN THE TRAINING DIRECTORY (so this could differ from its original id
# since trainers are essentially grabbed at random by the super trainer), used by the evaluators to help store them under
# the right trainer file
#lossallowed: the percentage loss allowed for every buy/sell decision
storedInput = {'directoryprefix': 'CryptoEvaluator', 'website': 'binance', 'day': 'monday', 'hour': 9, 'min': 0,
               'classNum': -1, 'variationNum': -1,  'idnum': 0,
               'lossallowed': -1}

#parameters passed to the datastream pseudo api
datastreamparamspassed = {'website': 'binance',  'mins': 0, 'minmax': 1440, 'hourstoprime': 0, 'freshrun': False}

#divide by this to turn a percent into a decimal
percenttodecimal = 100

######################VALUES RELATED TO TIME

#two hours in ms
TWO_HOURS = 7200000

#two hours in min
TWO_HOURS_MIN = 120

#one day in ms
ONE_DAY = 86400000

#one third day in ms
ONE_THIRD_DAY = 28800000

#one third day in min
ONE_THIRD_MIN = 480

#one minute in ms
ONE_MIN_MS = 60000

#one second in ms
ONE_SEC_MS = 1000

#minutes in an hour
mininhour = 60

#hours in a day
hourinday = 24

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

#return the next day from the day passed
def nextDay(daystring):
    """
    :param daystring: the current day
    :return: the next day
    """

    #dictionary keyed by the current day to get the next day
    dayandnextdaydict = {'monday': 'tuesday', 'tuesday': 'wednesday', 'wednesday': 'thursday', 'thursday': 'friday',
                         'friday': 'saturday', 'saturday': 'sunday', 'sunday': 'monday'}

    return dayandnextdaydict[daystring]

#pass a list of lists and remove only the empty lists  (only works with a list of lists)
#takes care of multiple empty inner lists
def removeEmptyInnerLists(listoflists, listtomirrorremoves = []):
    """
    :param listoflists: the list of lists
    :param listtomirrorremoves: a normal list to remove whatever value is at each index in conjunction with the listsoflists
    if nothing is specified then nothing is done
    :return:
    """
    #if we found an empty inner list
    foundanemptylist = True

    #if there are no empty lists then presumably we do not need to remove anything
    if len(listoflists) == 0:
        foundanemptylist = False

    #while there was no empty list found
    while(foundanemptylist):

        # list index reset
        listindex = 0

        #go through each list in the list of lists
        for list in listoflists:

            #if there is nothing in the list remove it, set that an empty list has been found and break out of the iteration
            if len(list) == 0:
                listoflists.remove(list)

                #if there is a passed list to remove at the same time remove the corresponding item at the same index
                # as the inner list from our lists of lists to be removed
                if len(listtomirrorremoves) != 0:
                    del listtomirrorremoves[listindex]

                foundanemptylist = True
                break
            #if no empty list is found set the value to false
            else:
                foundanemptylist = False

            #incremenet the list index
            listindex += 1

# returns the number of files in a directory
# is used to tell what the next idnum will be needed to add another parameter file
# path joining version for other paths


def numFiles(directory):
    """
    :param: directory of the supertrainer files so we can see how many there are
    :return:
    """
    # makes the directorys in the path variable if they do not exist
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
    return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])


#dump some object to a pickle file


def writepickle (object, directory, picklefilename):
    """
    :param object: the object to pickle
    :param directory: the directory desired to be written to
    :param picklefilename: the name of the pickleifile
    :return:
    """

    # makes the directorys in the path variable if they do not exist
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
    with open("{}/{}".format(directory, picklefilename), "wb") as pickle_out:
        pkl.dump(object, pickle_out)

#read the pickle file in
def readpickle(directory, picklefilename):
    """
    :param directory: the directory where the file is
    :param picklefilename: the pickle file name
    :return: the unpickled object
    """

    # makes the directorys in the path variable if they do not exist
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
    with open("{}/{}".format(directory, picklefilename), "rb") as pickle_in:
        object = pkl.load(pickle_in)

    return object