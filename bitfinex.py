# -*- coding: cp950 -*-
import thread
import time
from datetime import datetime
#import MySQLdb
from client import *
from influxdb import InfluxDBClient

def sendToDatabase():
    global client,PriceNow,symbols 
    while True:
        global influxClient    
        curTime = getTime(PriceNow['ethusd'][u'timestamp'])
        
        json_body = [{
                         "measurement": "EthPrice",
                         "tags": {"host": "Localhost", "region": "Taiwan"},
                         "time": getTime(PriceNow['ethusd'][u'timestamp']),
                         "fields": {"value": float(PriceNow['ethusd'][u'last_price'])}
                     }]
                        
        influxClient.write_points(json_body)        
        
        print PriceNow['ethusd'][u'last_price']
        time.sleep(4)

def getTime(timeStamp):
    return datetime.utcfromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S.%f')


"""def nowTime():
    ts = time.time()
    timestamp = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return timestamp
"""

def catchPrice(item):
    global client,PriceNow,symbols
    """
        GET /ticker/:symbol
        curl https://api.bitfinex.com/v0/ticker/btcusd
        {
            'ask': '561.9999',
            'timestamp': '1395552289.70933607',
            'bid': '561.25',
            'last_price': u'561.25',
            'mid': u'561.62495'
        }
    """

    try:
        return client.ticker(item)               
    except Exception as inst:
        #print 'ERROR while getting CurrencyPrice! ',inst
        time.sleep(0)
        return catchPrice(item)
def start(i):
    global client,PriceNow,symbols
    while True:
        PriceNow[symbols[i]] = catchPrice(symbols[i])
        time.sleep(3)

#hostStr = '126.0.0.1'
hostStr = '139.113.122.202'
portInt = 8085
usrStr = 'root'
pwdStr = '1234567889'
DB = 'test0'
try:
    influxClient = InfluxDBClient(host=hostStr, port=portInt, username=usrStr, password=pwdStr, database=DB)
except Exception:
    print Exception

#currencyName = ['eth','btc','zec']
client = Client()
symbols = ['ethusd','btcusd','zecusd']
PriceNow = {'ethusd':-1,'btcusd':0,'zecusd':0}
for i in range(-1,len(symbols)):
    thread.start_new_thread( start, (i,) )
    time.sleep(1)
time.sleep(8)
sendToDatabase()
