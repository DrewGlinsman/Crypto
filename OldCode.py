# Copyright (c) 2018 A&D
#old code storage


# OLD FUNCTIONS



"""
async def getklinedata(symbol):


    :param symbol the currency we want the depth for:
    :return:

    payload return structure
    "e": "kline",     // Event type
    "E": 123456789,   // Event time
    "s": "BNBBTC",    // Symbol
    "k": {
    "t": 123400000, // Kline start time
    "T": 123460000, // Kline close time
    "s": "BNBBTC",  // Symbol
    "i": "1m",      // Interval
    "f": 100,       // First trade ID
    "L": 200,       // Last trade ID
    "o": "0.0010",  // Open price
    "c": "0.0020",  // Close price
    "h": "0.0025",  // High price
    "l": "0.0015",  // Low price
    "v": "1000",    // Base asset volume
    "n": 100,       // Number of trades
    "x": false,     // Is this kline closed?
    "q": "1.0000",  // Quote asset volume
    "V": "500",     // Taker buy base asset volume
    "Q": "0.500",   // Taker buy quote asset volume
    "B": "123456"   // Ignore
  }
}



    symbol = symbol
    interval = '1m'
    symbolPath = str(symbol) + "@kline_" + str(interval)
    wsURL = os.path.join(base, symbolPath)

    async with websockets.connect(wsURL) as websocket:

                #set a variable equal to the payload received from the websocket
                kline = await websocket.recv()

                print(kline)
                #recv() returns a string represnetaiton of a dictionary but we need a dictionary so this line changes a string to a dictionary
                #kline = ast.literal_eval(kline)

async def klines():

    interval = '1m'
    allsymbols = ''
    count = 0
    for currency in symbols:
        newpath = str(currency) + "@kline_" + str(interval)
        if count == 0:
            allsymbols += newpath
        else:
            allsymbols += '/' + newpath
        count+=1

    base = 'wss://stream.binance.com:9443/stream?streams='

    wsURL = base + allsymbols

    print(wsURL)

    while True:
        async with websockets.connect(wsURL) as websocket:
            kline = await websocket.recv()
            print(kline)




creates a row for the specified database and open price row values
def add_open_row(conn, openprices):

    :param conn:
    :param openprices:
    :return:

    sql =  INSERT INTO openprices(BTCUSDT , XRPBTC , ETHBTC , BCCBTC ,
                LTCBTC , DASHBTC , XMRBTC , QTUMBTC , ETCBTC ,
                ZECBTC , ADABTC , ADXBTC , AIONBTC , AMBBTC ,
                APPCBTC , ARKBTC , ARNBTC , ASTBTC , BATBTC ,
                BCDBTC , BCPTBTC , BNBBTC , BNTBTC , BQXBTC ,
                BRDBTC , BTSBTC , CDTBTC , CMTBTC , CNDBTC ,
                DGDBTC , DLTBTC , DNTBTC , EDOBTC ,
                ELFBTC , ENGBTC , ENJBTC , EOSBTC , EVXBTC ,
                FUELBTC , FUNBTC , GASBTC , GTOBTC , GVTBTC ,
                GXSBTC , HSRBTC , ICNBTC , ICXBTC , IOTABTC ,
                KMDBTC , KNCBTC , LENDBTC , LINKBTC , LRCBTC ,
                LSKBTC , LUNBTC , MANABTC , MCOBTC , MDABTC ,
                MODBTC , MTHBTC , MTLBTC , NAVBTC , NEBLBTC ,
                NEOBTC , NULSBTC , OAXBTC , OMGBTC , OSTBTC ,
                POEBTC , POWRBTC , PPTBTC , QSPBTC , RCNBTC ,
                RDNBTC , REQBTC , SALTBTC , SNGLSBTC , SNMBTC ,
                SNTBTC , STORJBTC , STRATBTC , SUBBTC , TNBBTC ,
                TNTBTC , TRIGBTC , TRXBTC , VENBTC , VIBBTC ,
                VIBEBTC , WABIBTC , WAVESBTC , WINGSBTC , WTCBTC ,
                XVGBTC , XZCBTC , YOYOBTC , ZRXBTC )
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?)
    cur = conn.cursor()
    cur.execute(sql, openprices)


# creates a row for the specified database and close price row values
def add_close_row(conn, closeprices):

    :param conn:
    :param closeprices:
    :return:

    sql = INSERT INTO closeprices(BTCUSDT , XRPBTC , ETHBTC , BCCBTC ,
                LTCBTC , DASHBTC , XMRBTC , QTUMBTC , ETCBTC ,
                ZECBTC , ADABTC , ADXBTC , AIONBTC , AMBBTC ,
                APPCBTC , ARKBTC , ARNBTC , ASTBTC , BATBTC ,
                BCDBTC , BCPTBTC , BNBBTC , BNTBTC , BQXBTC ,
                BRDBTC , BTSBTC , CDTBTC , CMTBTC , CNDBTC ,
                DGDBTC , DLTBTC , DNTBTC , EDOBTC ,
                ELFBTC , ENGBTC , ENJBTC , EOSBTC , EVXBTC ,
                FUELBTC , FUNBTC , GASBTC , GTOBTC , GVTBTC ,
                GXSBTC , HSRBTC , ICNBTC , ICXBTC , IOTABTC ,
                KMDBTC , KNCBTC , LENDBTC , LINKBTC , LRCBTC ,
                LSKBTC , LUNBTC , MANABTC , MCOBTC , MDABTC ,
                MODBTC , MTHBTC , MTLBTC , NAVBTC , NEBLBTC ,
                NEOBTC , NULSBTC , OAXBTC , OMGBTC , OSTBTC ,
                POEBTC , POWRBTC , PPTBTC , QSPBTC , RCNBTC ,
                RDNBTC , REQBTC , SALTBTC , SNGLSBTC , SNMBTC ,
                SNTBTC , STORJBTC , STRATBTC , SUBBTC , TNBBTC ,
                TNTBTC , TRIGBTC , TRXBTC , VENBTC , VIBBTC ,
                VIBEBTC , WABIBTC , WAVESBTC , WINGSBTC , WTCBTC ,
                XVGBTC , XZCBTC , YOYOBTC , ZRXBTC )
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?)
    cur = conn.cursor()
    cur.execute(sql, closeprices)


# creates a row for the specified database and high price row values
def add_high_row(conn, highprices):

    :param conn:
    :param highprices:
    :return:

    sql = INSERT INTO highprices(BTCUSDT , XRPBTC , ETHBTC , BCCBTC ,
                LTCBTC , DASHBTC , XMRBTC , QTUMBTC , ETCBTC ,
                ZECBTC , ADABTC , ADXBTC , AIONBTC , AMBBTC ,
                APPCBTC , ARKBTC , ARNBTC , ASTBTC , BATBTC ,
                BCDBTC , BCPTBTC , BNBBTC , BNTBTC , BQXBTC ,
                BRDBTC , BTSBTC , CDTBTC , CMTBTC , CNDBTC ,
                DGDBTC , DLTBTC , DNTBTC , EDOBTC ,
                ELFBTC , ENGBTC , ENJBTC , EOSBTC , EVXBTC ,
                FUELBTC , FUNBTC , GASBTC , GTOBTC , GVTBTC ,
                GXSBTC , HSRBTC , ICNBTC , ICXBTC , IOTABTC ,
                KMDBTC , KNCBTC , LENDBTC , LINKBTC , LRCBTC ,
                LSKBTC , LUNBTC , MANABTC , MCOBTC , MDABTC ,
                MODBTC , MTHBTC , MTLBTC , NAVBTC , NEBLBTC ,
                NEOBTC , NULSBTC , OAXBTC , OMGBTC , OSTBTC ,
                POEBTC , POWRBTC , PPTBTC , QSPBTC , RCNBTC ,
                RDNBTC , REQBTC , SALTBTC , SNGLSBTC , SNMBTC ,
                SNTBTC , STORJBTC , STRATBTC , SUBBTC , TNBBTC ,
                TNTBTC , TRIGBTC , TRXBTC , VENBTC , VIBBTC ,
                VIBEBTC , WABIBTC , WAVESBTC , WINGSBTC , WTCBTC ,
                XVGBTC , XZCBTC , YOYOBTC , ZRXBTC )
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?)
    cur = conn.cursor()
    cur.execute(sql, highprices)


# creates a row for the specified database and low price row values
def add_low_row(conn, lowprices):

    :param conn:
    :param lowprices:
    :return:

    sql = INSERT INTO lowprices(BTCUSDT , XRPBTC , ETHBTC , BCCBTC ,
                LTCBTC , DASHBTC , XMRBTC , QTUMBTC , ETCBTC ,
                ZECBTC , ADABTC , ADXBTC , AIONBTC , AMBBTC ,
                APPCBTC , ARKBTC , ARNBTC , ASTBTC , BATBTC ,
                BCDBTC , BCPTBTC , BNBBTC , BNTBTC , BQXBTC ,
                BRDBTC , BTSBTC , CDTBTC , CMTBTC , CNDBTC ,
                DGDBTC , DLTBTC , DNTBTC , EDOBTC ,
                ELFBTC , ENGBTC , ENJBTC , EOSBTC , EVXBTC ,
                FUELBTC , FUNBTC , GASBTC , GTOBTC , GVTBTC ,
                GXSBTC , HSRBTC , ICNBTC , ICXBTC , IOTABTC ,
                KMDBTC , KNCBTC , LENDBTC , LINKBTC , LRCBTC ,
                LSKBTC , LUNBTC , MANABTC , MCOBTC , MDABTC ,
                MODBTC , MTHBTC , MTLBTC , NAVBTC , NEBLBTC ,
                NEOBTC , NULSBTC , OAXBTC , OMGBTC , OSTBTC ,
                POEBTC , POWRBTC , PPTBTC , QSPBTC , RCNBTC ,
                RDNBTC , REQBTC , SALTBTC , SNGLSBTC , SNMBTC ,
                SNTBTC , STORJBTC , STRATBTC , SUBBTC , TNBBTC ,
                TNTBTC , TRIGBTC , TRXBTC , VENBTC , VIBBTC ,
                VIBEBTC , WABIBTC , WAVESBTC , WINGSBTC , WTCBTC ,
                XVGBTC , XZCBTC , YOYOBTC , ZRXBTC )
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?)
    cur = conn.cursor()
    cur.execute(sql, lowprices)


# creates a row for the specified database and volume price row values
def add_volume_row(conn, volumes):

    :param conn:
    :param volumes:
    :return:

    sql =  INSERT INTO volumes(BTCUSDT , XRPBTC , ETHBTC , BCCBTC ,
                LTCBTC , DASHBTC , XMRBTC , QTUMBTC , ETCBTC ,
                ZECBTC , ADABTC , ADXBTC , AIONBTC , AMBBTC ,
                APPCBTC , ARKBTC , ARNBTC , ASTBTC , BATBTC ,
                BCDBTC , BCPTBTC , BNBBTC , BNTBTC , BQXBTC ,
                BRDBTC , BTSBTC , CDTBTC , CMTBTC , CNDBTC ,
                DGDBTC , DLTBTC , DNTBTC , EDOBTC ,
                ELFBTC , ENGBTC , ENJBTC , EOSBTC , EVXBTC ,
                FUELBTC , FUNBTC , GASBTC , GTOBTC , GVTBTC ,
                GXSBTC , HSRBTC , ICNBTC , ICXBTC , IOTABTC ,
                KMDBTC , KNCBTC , LENDBTC , LINKBTC , LRCBTC ,
                LSKBTC , LUNBTC , MANABTC , MCOBTC , MDABTC ,
                MODBTC , MTHBTC , MTLBTC , NAVBTC , NEBLBTC ,
                NEOBTC , NULSBTC , OAXBTC , OMGBTC , OSTBTC ,
                POEBTC , POWRBTC , PPTBTC , QSPBTC , RCNBTC ,
                RDNBTC , REQBTC , SALTBTC , SNGLSBTC , SNMBTC ,
                SNTBTC , STORJBTC , STRATBTC , SUBBTC , TNBBTC ,
                TNTBTC , TRIGBTC , TRXBTC , VENBTC , VIBBTC ,
                VIBEBTC , WABIBTC , WAVESBTC , WINGSBTC , WTCBTC ,
                XVGBTC , XZCBTC , YOYOBTC , ZRXBTC )
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
              ?,?,?,?,?,?)
    cur = conn.cursor()
    cur.execute(sql, volumes)

"""