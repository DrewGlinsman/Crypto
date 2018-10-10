import requests
import PriceSymbolsUpdater

#one day in ms
ONE_DAY = 86400000

#one day in min
ONE_DAY_MIN = 1440

#one third day in ms
ONE_THIRD_DAY = 28800000

#one third day in min
ONE_THIRD_MIN = 480

#one minute in ms
ONE_MIN_MS = 60000

#one second in ms
ONE_SEC_MS = 1000

priceSymbols = PriceSymbolsUpdater.updatePriceSymbolsBinance()

def main():
    #grabbing the starttime of the data desired and the current time (endtime)
    endTime = requests.get("https://api.binance.com/api/v1/time")
    endTime = endTime.json()
    endTime = endTime['serverTime']
    startTime = endTime - ONE_THIRD_DAY

    #temporary dictionaries for each of the five types of data
    openpricedict = {}
    closepricedict = {}
    highpricedict = {}
    lowpricedict = {}
    volumedict = {}

    timeBuffer = ONE_THIRD_MIN
    x = 0
    minute = 0
    min = 0
    print('Start Time: ' + str(startTime) + ' End Time: ' + str(endTime))
    for x in range(3):
        # set up the dicts to be made of lists where the index is the minute associated with the list of values
        # and the values of each list correspond to the currencies in order from price symbols
        # these are made this way to facilitate easy transfer to the tables of the database
        for minute in range(timeBuffer):
            openpricedict.update({minute: []})
            closepricedict.update({minute: []})
            highpricedict.update({minute: []})
            lowpricedict.update({minute: []})
            volumedict.update({minute: []})

        #iterate through the dictionary of price symbols and store the five kinds of data in their corresponding dictionaries
        for currencyname in priceSymbols:
            #store 2 hours of data for the five categories to prime the database
            parameters = {'symbol': currencyname, 'startTime': startTime, 'endTime': endTime, 'interval': '1m'}
            data = requests.get("https://api.binance.com/api/v1/klines", params=parameters)
            data = data.json()
            min = timeBuffer - ONE_THIRD_MIN
            #iterate through the 2 hours of data and store it in ascending order (oldest to newest)
            for interval in data:
                openpricedict[min].append(interval[1])
                closepricedict[min].append(interval[4])
                highpricedict[min].append(interval[2])
                lowpricedict[min].append(interval[3])
                volumedict[min].append(interval[5])
                min+=1

        timeBuffer += ONE_THIRD_MIN
        endTime = startTime
        startTime -= ONE_THIRD_DAY
        print('Start Time: ' + str(startTime) + ' End Time: ' + str(endTime))
        print('timeBuffer ' + str(timeBuffer) + ' Min: ' + str(min))
    print(openpricedict)
    print(closepricedict)
    print(highpricedict)
    print(lowpricedict)
    print(volumedict)

if __name__ == "__main__":
    main()