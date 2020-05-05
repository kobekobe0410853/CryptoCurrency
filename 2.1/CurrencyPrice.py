# -*- coding: cp950 -*-
# -*- coding: utf8 -*-
from __future__ import division
import MySQLdb
import datetime
import time
import math

class CurrencyPrice:
      ethNowPrice = 0
      zecNowPrice = 0
      def __init__(self):
            ethNowPrice = self.pastHoursAverage(0.01,'eth')
            zecNowPrice = self.pastHoursAverage(0.01,'zec')
      def getPrice(self,hours=0):
            if hours==0:
                  eth = self.pastHoursAverage(0.00604, 'eth')  #average 22 sec price
                  zec = self.pastHoursAverage(0.00694, 'zec')  #average 25 sec price
                  btc = self.pastHoursAverage(0.00694, 'btc')  #average 25 sec price
                  priceDic = {'eth' : eth , 'btc' : btc , 'zec' : zec}
                  return priceDic
            else:
                  eth = self.pastHoursAverage(hours, 'eth')  #average hours sec price
                  zec = self.pastHoursAverage(hours, 'zec')  #average hours sec price
                  btc = self.pastHoursAverage(hours, 'btc')  #average hours sec price
                  priceDic = {'eth' : eth , 'btc' : btc , 'zec' : zec}
                  return priceDic
      def pastHoursAverage(self,hours,currency):
            tmp = []
            try:
                  db = MySQLdb.connect('localhost','root','1234567890','Virtual_Currency_Price')
                  cursor = db.cursor()
                  if currency == 'eth' :
                        while len(tmp) == 0:
                              sendString = 'select * from ETH where date_ > "%s";'%self.pastHoursTime(hours) 
                              cursor.execute(sendString)
                              for row in cursor:
                                    tmp.append(row[1])                 
                  elif currency == 'btc':
                        db.close()  #
                        return -1.0
                  elif currency == 'zec':
                        db.close()  #
                        return -1.0
                  else :
                        db.close()  #
                        return -1.0
                  avg =  float(sum(tmp))/len(tmp)
                  db.commit()
                  db.close()                  
                  return avg
            except Exception as inst:
                  print 'ERROR while getting PastHoursAverages !!  ' , inst
                  time.sleep(2)
                  return self.pastHoursAverage(hours,currency)
      def pastHoursTime(self,hours):
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts) - datetime.timedelta(hours = hours)
            return timestamp.strftime('%Y-%m-%d %H:%M:%S')
      def usd2OtherCurrency(self,usd,currencyName):
            return usd * self.getPrice(currencyName)
