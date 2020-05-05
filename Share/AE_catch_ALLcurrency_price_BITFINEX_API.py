# -*- coding: cp950 -*-
import thread
import time
import datetime
#import MySQLdb
from client import *

def sendToDatabase():
    global client,PriceNow,symbols 
    while True:
        '''
        try:
            db = MySQLdb.connect('localhost','root','1234567890','Virtual_Currency_Price',charset='utf8',port=3306)
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            cursor = db.cursor()
            sendString = 'insert into ETH (date_,price) values ("%s",%f);'%(nowTime(),PriceNow['ethusd'])
            cursor.execute(sendString)
            sendString = 'insert into BTC (date_,price) values ("%s",%f);'%(nowTime(),PriceNow['btcusd'])
            cursor.execute(sendString)
            sendString = 'insert into ZEC (date_,price) values ("%s",%f);'%(nowTime(),PriceNow['zecusd'])
            cursor.execute(sendString)
            db.commit()
            db.close()
            print datetime.datetime.now(),'  ',PriceNow
        except Exception as inst:
            print 'ERROR while connect and sending to database!  ',inst
        '''
        print PriceNow
        time.sleep(5)
def nowTime():
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return timestamp
def catchPrice(item):
    global client,PriceNow,symbols
    try:
        return client.ticker(item)[u'last_price']     # 最新成交價格
    except Exception as inst:
        #print 'ERROR while getting CurrencyPrice! ',inst
        time.sleep(1)
        return catchPrice(item)
def start(i):
    global client,PriceNow,symbols
    while True:
        PriceNow[symbols[i]] = catchPrice(symbols[i])
        time.sleep(4)
#currencyName = ['eth','btc','zec']
client = Client()
symbols = ['ethusd','btcusd','zecusd']
PriceNow = {'ethusd':0,'btcusd':0,'zecusd':0}
for i in range(0,len(symbols)):
    thread.start_new_thread( start, (i,) )
    time.sleep(1)
time.sleep(8)
sendToDatabase()
