# -*- coding: cp950 -*-
import time
import datetime
import MySQLdb
from bitfinex.client import *

def sendToDatabase():
    global ETH_PriceNow
    print datetime.datetime.now(),' price:',ETH_PriceNow
    try:
        db = MySQLdb.connect('localhost','root','1234567890','Virtual_Currency_Price',charset='utf8',port=3306)
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        sendString = 'insert into ETH (date_,price) values ("%s",%f);'%(nowTime(),ETH_PriceNow)
        cursor = db.cursor()
        cursor.execute(sendString)
        db.commit()
        db.close()
    except Exception as inst:
        print 'ERROR while connect and sending to database!  ',inst
def nowTime():
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return timestamp

symbols = ['ethusd','zecusd']
client = Client()
while True:
    ETH_PriceNow = client.ticker('ethusd')[u'last_price']   # 最新成交價格
    sendToDatabase()
    time.sleep(3.5)
