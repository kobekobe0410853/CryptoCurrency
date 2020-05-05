# -*- coding: cp950 -*-
from CurrencyPrice import *
import MySQLdb
import time

class TurningPoint:
      def __init__(self):
            self.point = 'null'
      def isSellPoint(self):
            if self.connectDatabaseAndCalculateSumDelta(0.05) < -0.339: #3min 轉折回來  0.49        * 賣點
                  return True
            else:
                  return False
      def isBuyPoint(self):
            #7min or 10min or 21轉折回來0.702* 買點       #3min 還是持續成長0.32*看漲        #1min 還是持續成長0.1*看漲        #30sec 還是持續成長*看漲
            if ( self.connectDatabaseAndCalculateSumDelta(0.11666) > 0.572 \
            or self.connectDatabaseAndCalculateSumDelta(0.16666) > 0.832 \
            or self.connectDatabaseAndCalculateSumDelta(0.35) > 0.84 ) \
            and self.connectDatabaseAndCalculateSumDelta(0.05) > 0.359 \
            and self.connectDatabaseAndCalculateSumDelta(0.0166667) > 0.126\
            and self.connectDatabaseAndCalculateSumDelta(0.0083333) >= 0:       
                  return True
            else:
                  return False
      def isStillAscending(self,minute=3,deltaPrice=0.18):
            #3min
            hours = float(minute)/60.0
            if self.connectDatabaseAndCalculateSumDelta(hours) > deltaPrice:
                  return True
            else:
                  return False
      def connectDatabaseAndCalculateSumDelta(self,hours):
            ETH = []
            ETH2 = []
            try:
                  db = MySQLdb.connect('localhost','root','1234567890','Virtual_Currency_Price',port=3306)
                  cursor = db.cursor()
                  while len(ETH) == 0 or len(ETH2) == 0 :
                        sendString = 'select * from eth where date_ > "%s" and date_ < "%s";' % ( CurrencyPrice().pastHoursTime(hours), CurrencyPrice().pastHoursTime(hours/2.0))    
                        cursor.execute(sendString)
                        for row in cursor.fetchall():
                              ETH.append(row[1])
                        
                        sendString = 'select * from eth where date_ > "%s";' % CurrencyPrice().pastHoursTime(hours/2.0)
                        cursor.execute(sendString)
                        for row in cursor.fetchall():
                              ETH2.append(row[1])
                  db.commit()
                  db.close()
                  return float(self.calculateAverage(ETH2)) - float(self.calculateAverage(ETH))
            except Exception as inst:
                  print 'ERROR finding TURNING POINT while connecting virtural_currency_price!   Tabel: ETH!  ',inst
                  time.sleep(2)
                  return self.connectDatabaseAndCalculateSumDelta(hours)                 
      def calculateAverage(self,tmp):
            if len(tmp) > 0 :
                  return float(sum(tmp))/len(tmp)
            else :
                  return '分母是0 !!'
      def calculateDeltaSum(self,prices):
          global nullList
          nullList = []
          delta = []   
          delta.append(0)
          for i in range(1,len(prices)):
              delta.append(prices[i]-prices[i-1])
          return sum(delta)
