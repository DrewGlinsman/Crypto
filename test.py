import datetime
import pytz
from Generics import priceSymbols
from CryptoDistribution import readPickle


def createVolumeDict():
    buyVolumeDict = {}
    sellVolumeDict = {}

    # creating a timestamp of the current time and finding which day of the week it is
    currentTime = datetime.datetime.now(tz=pytz.UTC)
    currentTime = currentTime.astimezone(pytz.timezone('US/Eastern'))
    hour = currentTime.strftime("%H%M")
    minute = int(currentTime.strftime("%M"))

    day = currentTime.isoweekday()
    weekday = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
    }[day]

    delta = minute % 10
    if(delta == 0):
        for key, value in priceSymbols.items():
            value = value.lower()
            temp1, temp2 = readPickle(value, weekday, hour)
            buyVolumeDict.update(temp1)
            sellVolumeDict.update(temp2)

    # if the time difference is greater than or equal to 5 minutes round up
    if (delta >= 5):
        currentTime = currentTime + datetime.timedelta(minutes=(10 - delta))
        hour = currentTime.strftime("%H%M")
        for key, value in priceSymbols.items():
            value = value.lower()
            temp1, temp2 = readPickle(value, weekday, hour)
            buyVolumeDict.update(temp1)
            sellVolumeDict.update(temp2)

    # if the time difference is less than 5 subtract to nearest 10 minute interval
    elif(delta < 5):
        currentTime = currentTime + datetime.timedelta(minutes=(-delta))
        hour = currentTime.strftime("%H%M")
        for key, value in priceSymbols.items():
            value = value.lower()
            temp1, temp2 = readPickle(value, weekday, hour)
            buyVolumeDict.update(temp1)
            sellVolumeDict.update(temp2)

    return buyVolumeDict, sellVolumeDict


temp1, temp2 = createVolumeDict()
print("Buy Volume: " + str(temp1))
print("Num Items: " + str(len(temp1)))
print("Sell Volume: " + str(temp2))
