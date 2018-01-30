import sys
import subprocess
import random

# EXPLANATION OF THE PARAMETERS


#PERCENT_TO_SPEND: the amount of the balance of bitcoin to spend. Should be calculated by how many bots are made
#MINIMUM_PERCENT_INCREASE: lowest percent increase for a cryptocurrency to be considered in the start of the bot
#MINIMUM_SCORE: the lowest score for a crypto to be addded to the list of scores to be checked for the remaineder of a run
#MINIMUM_MOVING_AVERAGE: the lowest moving average for a crypto score to be considered
#MAX_DECREASE: the maximum allowed decrease over a short (<15m) interval
#MAX_TIME_CYCLE: the maximum time the bot will run for in ticks (they are counted by a incrementing variable)
#MAX_CYCLES: the maximum amount of times the bot will buy and sell
#MAX_PERCENT_CHANGE: the highest % increase and the lowest % decrease a crypto can have over the life of owning it before an auto reevaluation
#NEGATIVE_WEIGHT: weight applied to negative percent price or percent volume change
#CUMULATIVE_PERCENT_CHANGE: the cumulative % change of a crypto's price over the course of owning it
#CUMULATIVE_PERCENT_CHANGE_STORE: the cumulative percent change over the course of owning several cryptos
#SLOT_WEIGHT: weight applied to each slot of the intervals being checked to see if they the crypto was increasing or decreasing
#TIME_INCREASING_MODIFIER: the unweighted time increasing modifier (time increasing is the count of intervals where the price was increasing)
#VOLUME_INCREASING_MODIFIER: the volume increasing modifier (volume increasing is the count of intervals where the volume traded increased)
#PERCENT_BY_HOUR_MODIFIER: the modifier for the total percent change of a crypto over a longer interval (> 1hr)
#VOLUME_PERCENT_BY_HOUR_MODIFIER: the modifier for the volume percent change over a longer interval (> 1hr)
#FLOOR_PRICE_MODIFIER: the lowest % change above the original price the crypto was bought at before the bot auto sells it (calculated later than the other failure conditions to catch a decreasing price)
#CUMULATIVE_PRICE_MODIFIER: the cumulative price change modifier for the weighted moving average
#PRIMARY_MODIFIED_VOLUME_SCALER: the scaler to make more volume traded have the same sign as the percent change in the price than the amount that is counted as having the opposite sign
#WAIT_FOR_CHECK_FAILURE: the number of ticks before the failure condition is checked (the crypto is decreasing over the past 10 minutes)
#WAIT_FOR_CHECK_TOO_LOW: the number of ticks before ethe program checks to see if a crypto has decreased too low to its starting point

PARAMETERS = {'PERCENT_TO_SPEND': 1, 'MINIMUM_PERCENT_INCREASE': 5.0, 'MINIMUM_SCORE': 1.0, 'MINIMUM_MOVING_AVERAGE': .6, 'MAX_DECREASE': -10, 'MAX_TIME_CYCLE': 3600, 'MAX_CYCLES': 24, 'MAX_PERCENT_CHANGE': 15
, 'NEGATIVE_WEIGHT': 1.5, 'CUMULATIVE_PERCENT_CHANGE_STORE': 0.0, 'SLOT_WEIGHT': 1, 'TIME_INCREASING_MODIFIER': 10, 'VOLUME_INCREASING_MODIFIER': .01, 'PERCENT_BY_HOUR_MODIFIER': 1,
'VOLUME_INCREASING_MODIFIER': .01, 'PERCENT_BY_HOUR_MODIFIER': 1, 'VOLUME_PERCENT_BY_HOUR_MODIFIER': .1, 'FLOOR_PRICE_MODIFIER': 1.005, 'CUMULATIVE_PRICE_MODIFIER': 100, 'PRIMARY_MODIFIED_VOLUME_SCALER': 2, 'WAIT_FOR_CHECK_FAILURE': 300, 'WAIT_FOR_CHECK_TOO_LOW': 600}

priceSymbols = {'bitcoin': 'BTCUSDT', 'ripple': "XRPBTC",
                'ethereum': 'ETHBTC', 'BCC': 'BCCBTC',
                'LTC': 'LTCBTC', 'Dash': 'DASHBTC',
                'Monero': 'XMRBTC', 'Qtum': 'QTUMBTC', 'ETC': 'ETCBTC',
                'Zcash': 'ZECBTC', 'ADA': 'ADABTC', 'ADX': 'ADXBTC', 'AION' : 'AIONBTC', 'AMB': 'AMBBTC', 'APPC': 'APPCBTC', 'ARK': 'ARKBTC', 'ARN': 'ARNBTC', 'AST': 'ASTBTC', 'BAT': 'BATBTC', 'BCD': 'BCDBTC', 'BCPT': 'BCPTBTC', 'BNB': 'BNBBTC', 'BNT': 'BNTBTC', 'BQX': 'BQXBTC', 'BRD': 'BRDBTC', 'BTS': 'BTSBTC', 'CDT': 'CDTBTC', 'CMT': 'CMTBTC', 'CND': 'CNDBTC', 'CTR':'CTRBTC', 'DGD': 'DGDBTC', 'DLT': 'DLTBTC', 'DNT': 'DNTBTC', 'EDO': 'EDOBTC', 'ELF': 'ELFBTC', 'ENG': 'ENGBTC', 'ENJ': 'ENJBTC', 'EOS': 'EOSBTC', 'EVX': 'EVXBTC', 'FUEL': 'FUELBTC', 'FUN': 'FUNBTC', 'GAS': 'GASBTC', 'GTO': 'GTOBTC', 'GVT': 'GVTBTC', 'GXS': 'GXSBTC', 'HSR': 'HSRBTC', 'ICN': 'ICNBTC', 'ICX': 'ICXBTC', 'IOTA': "IOTABTC", 'KMD': 'KMDBTC', 'KNC': 'KNCBTC', 'LEND': 'LENDBTC', 'LINK':'LINKBTC', 'LRC':'LRCBTC', 'LSK':'LSKBTC', 'LUN': 'LUNBTC', 'MANA': 'MANABTC', 'MCO': 'MCOBTC', 'MDA': 'MDABTC', 'MOD': 'MODBTC', 'MTH': 'MTHBTC', 'MTL': 'MTLBTC', 'NAV': 'NAVBTC', 'NEBL': 'NEBLBTC', 'NEO': 'NEOBTC', 'NULS': 'NULSBTC', 'OAX': 'OAXBTC', 'OMG': 'OMGBTC', 'OST': 'OSTBTC', 'POE': 'POEBTC', 'POWR': 'POWRBTC', 'PPT': 'PPTBTC', 'QSP': 'QSPBTC', 'RCN': 'RCNBTC', 'RDN': 'RDNBTC', 'REQ': 'REQBTC', 'SALT': 'SALTBTC', 'SNGLS': 'SNGLSBTC', 'SNM': 'SNMBTC', 'SNT': 'SNTBTC', 'STORJ': 'STORJBTC', 'STRAT': 'STRATBTC', 'SUB': 'SUBBTC', 'TNB': 'TNBBTC', 'TNT': 'TNTBTC', 'TRIG': 'TRIGBTC', 'TRX': 'TRXBTC', 'VEN': 'VENBTC', 'VIB': 'VIBBTC', 'VIBE': 'VIBEBTC', 'WABI': 'WABIBTC', 'WAVES': 'WAVESBTC', 'WINGS': 'WINGSBTC', 'WTC': 'WTCBTC', 'XVG': 'XVGBTC', 'XZC': 'XZCBTC', 'YOYO': 'YOYOBTC', 'ZRX': 'ZRXBTC'}

#list of each variation of the parameter list, one is passed to each instance of the bot
PARAMETER_VARIATIONS=[]

def main():

    #CODE TO RUN MULTIPLE INSTANCES OF BOT

    procs = []
    for i in range(5):
        proc = subprocess.Popen([sys.executable, 'CryptoEvaluator.py', '{}in.csv'.format(i), '{}out.csv'.format(i)])
        procs.append(proc)

    for proc in procs:
        proc.wait()



if __name__ == "__main__":
    main()