# -*- coding: cp950 -*-
from client import *
import datetime
import time
import os
def look():
       time.sleep(2)
       try:
              catch = client.order_book('ethusd',{'limit_bids':340,'limit_asks':340})
       except Exception as inst:
              print inst
              return look()
       buyTotalAmount = 0.0
       sellTotalAmount = 0.0
       for i in catch[u'bids']:
              buyTotalAmount += i[u'amount']
       for i in catch[u'asks']:
              sellTotalAmount += i[u'amount']
       os.system('cls')
       print
       print 'buyTotalAmount:',buyTotalAmount,'           sellTotalAmount:',sellTotalAmount
       print
       if buyTotalAmount > sellTotalAmount*1.5:
              print '       買壓 漲 !'
              return 'buy_press'
       elif sellTotalAmount > buyTotalAmount*1.13:
              print '       賣壓 跌 !'
              return 'sell_press'
       else :
              print '       持平 '
              return 'hold'
def writeData(string,string2=''):
       with open("orderBookPrediction.txt", "a") as myfile:
              myfile.write(string+string2+'\n')
              myfile.close()
def priceNow():
       global client
       try:
              return int( client.ticker('ethusd')['last_price'] )
       except Exception as inst:
              time.sleep(0.2)
              return priceNow()
def action():
       global list_,previousAction,buyPrice
       print 'bpp',float(list_.count('buy_press'))/len(list_)
       print 'spp',float(list_.count('sell_press'))/len(list_)
       if previousAction == 'sell' and float(list_.count('buy_press'))/len(list_) > 0.96:
              buyPrice = priceNow()
              string = 'buy  %.2f   %s' %( buyPrice, datetime.datetime.fromtimestamp(time.time()).strftime('%Y/%m/%d %H:%M:%S') )
              writeData(string)
              previousAction = 'buy'
       elif ( previousAction == 'buy' and float( list_.count('sell_press') )/len(list_) > 0.37 ):
              #or ( previousAction == 'buy' and float(list_.count('sell_press'))/len(list_) > 0.5 ):
              string = 'sell  %.2f   %s\n' %( priceNow(), datetime.datetime.fromtimestamp(time.time()).strftime('%Y/%m/%d %H:%M:%S') )
              if priceNow()*0.998 > buyPrice*1.005:
                     writeData(string,'earn money \n')
              else:
                     writeData(string,'not earn money \n')
              previousAction = 'sell'
       elif ( previousAction == 'buy' and priceNow() < buyPrice - 2.0 ):
              #or ( previousAction == 'buy' and float(list_.count('sell_press'))/len(list_) > 0.5 ):
              string = 'sell  %.2f   %s\n' %( priceNow(), datetime.datetime.fromtimestamp(time.time()).strftime('%Y/%m/%d %H:%M:%S') ) 
              writeData(string,'止損點 \n')
              previousAction = 'sell'
       '''
       elif ( previousAction == 'buy' and priceNow()*0.998 > buyPrice*1.005 ):
              #or ( previousAction == 'buy' and float(list_.count('sell_press'))/len(list_) > 0.5 ):
              string = 'sell  %.2f   %s\n' %( priceNow(), datetime.datetime.fromtimestamp(time.time()).strftime('%Y/%m/%d %H:%M:%S') ) 
              writeData(string,'earn money \n')
              previousAction = 'sell'
       elif ( previousAction == 'buy' and float( len(list_) - list_.count('buy_press') )/len(list_) > 0.75 and priceNow()*0.998 > buyPrice*1.005 ):
              #or ( previousAction == 'buy' and float(list_.count('sell_press'))/len(list_) > 0.5 ):
              string = 'sell  %.2f   %s\n' %( priceNow(), datetime.datetime.fromtimestamp(time.time()).strftime('%Y/%m/%d %H:%M:%S') ) 
              writeData(string,'earn money \n')
              previousAction = 'sell'
       '''
previousAction = 'sell'
list_ = []
client = Client()
for i in range(0,60):
       list_.append( look() )
while True:
       list_.pop(0)
       list_.append( look() )
       #print list_
       action()
              
