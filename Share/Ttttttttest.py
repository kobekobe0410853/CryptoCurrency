# -*- coding: cp950 -*-
from TurningPoint import *
from CurrencyPrice import *
from BitfinexAccount import *
import MySQLdb
import datetime
import time
import thread
class Transactor:
       def __init__(self, transNum, exchanges, deltaPriceToTrans, currencyPriceNow):
              self.transactorNumber = transNum
              self.exchanges = exchanges
              self.deltaPriceToTrans = deltaPriceToTrans
              self.turningPoint = TurningPoint()
              self.currencyPrice = CurrencyPrice()
              self.firstIntoMarketFlag = True
              self.orderTransactedSuccess = True
              self.orderTicker = 0         # count this order if it has been too long but this order didnt transact !!
              if ( self.transactorNumber%2 ) == 1:
                     self.previousAction = 'sell'       #### 全部進來都要先買 eth 
              else :
                     self.previousAction = 'sell'
              self.previousActionPrice = currencyPriceNow
              thread.start_new_thread( self.recentDayDescendingWatching,())
              thread.start_new_thread( self.refreshPreviousHoursPrice,())
              time.sleep(15) #要delay 因為 multi thread 速度太慢 無法跟新參數
       def refreshPreviousHoursPrice(self):
              self.refreshTime = 60*5
              while True:
                     if self.previousAction == 'sell':
                            self.previousHoursPrice = self.currencyPrice.getPrice(1.8)
                            # 1.8 小時      /        108分鐘
                            #thread.start_new_thread( self.refreshPreviousActionPrice,())
                     time.sleep(self.refreshTime)       # sleep 5 min
       def recentDayDescendingWatching(self):
              while True:
                     # 8 小時內跌了5元 "可能崩盤了"
                     if self.turningPoint.connectDatabaseAndCalculateSumDelta(8) < -5:
                            self.recentDayDescendingFlag = True
                     else :
                            self.recentDayDescendingFlag =  False
                     time.sleep(60*30) # 30min
       def action(self, CurrencyPrice, bitfinexAccount):
              if ( self.orderTransactedSuccess\
              and self.previousAction == 'buy'\
              and self.predictAscendingWrongFlag == True )\
              or ( self.orderTransactedSuccess\
              and self.previousAction == 'buy'\
              and CurrencyPrice['eth'] > (self.previousActionPrice['eth']+self.deltaPriceToTrans['eth']) \
              and self.exchanges['eth'] >= 0.1\
              and self.isTheTransPoint('isHighPoint?')\
              and self.isProfitBiggerThanFee('eth', CurrencyPrice['eth']) ):    #   "看多預測錯誤 賣"  or  "漲 賣"             
                     ## 賣
                     print 
                     print '賣點 ',datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                     self.priceWhenMakeOrder = CurrencyPrice
                     time.sleep(3)
              elif self.recentDayDescendingFlag == False\
              and self.orderTransactedSuccess\
              and self.previousAction == 'sell'\
              and CurrencyPrice['eth']  < self.previousHoursPrice['eth']\
              and self.exchanges['usd'] > CurrencyPrice['eth'] * 0.1\
              and self.orderTransactedSuccess\
              and self.isTheTransPoint('isLowPoint?'):      #跌 買               
                     ## 買          and CurrencyPrice['eth']  < (self.previousActionPrice['eth']-self.deltaPriceToTrans['eth'])
                     print
                     print '買點 ',datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                     self.priceWhenMakeOrder = CurrencyPrice
                     thread.start_new_thread( self.predictAscendingWrong,())
                     time.sleep(3)
       def predictAscendingWrong(self):
              self.predictAscendingWrongFlag = False
              while True:
                     # 如果這筆看多      漲幅已經超過手續費      就成功預測會漲
                     if self.currencyPrice.getPrice()['eth'] - (self.previousActionPrice['eth']+0.1) > self.currencyPrice.getPrice()['eth']*0.0055:
                            break
                     elif self.turningPoint.connectDatabaseAndCalculateSumDelta(0.00333) < -0.16:  #2min 又跌回來  0.16       
                            self.predictAscendingWrongFlag = True
                            print '看多預測錯誤 !!!!!!'
                     time.sleep(8)
       def isProfitBiggerThanFee(self, currency, price):
              if currency == 'eth':
                     if price - (self.previousActionPrice['eth']+0.1) > price * 0.0058:
                            return True
                     else :
                            return False
       def isTheTransPoint(self,point):
              if point == 'isHighPoint?':                  
                     return self.turningPoint.isSellPoint()
              elif point == 'isLowPoint?':
                     return self.turningPoint.isBuyPoint()
       def sendTransActionToDatabase(self,ethDelta,usdDelta,ethNowPrice,action):
              try:
                     db = MySQLdb.connect('localhost','root','1234567890','Virtual_Currency_Price')
                     sendString = 'insert into ETH_transs (date_,transactorNumber,price,eth,usd,action_) values ("%s",%d,%f,%f,%f,"%s")' % (self.currencyPrice.pastHoursTime(0), self.transactorNumber, ethNowPrice, ethDelta, usdDelta, action)
                     cursor = db.cursor()
                     cursor.execute(sendString)
                     db.commit()
                     db.close()
              except Exception as inst:
                     print 'ERROR while sending TracsactionSuccessMessage to database !!  ' , inst
                     time.sleep(2)
                     self.sendTransActionToDatabase(ethDelta,usdDelta,ethNowPrice,action)
currencyPrice = CurrencyPrice()
bitfinexAccount = BitfinexAccount('SjT8YsP7dit0iBI7Rl1egrGuI2R5lZfK4Gnz9TOJbS1','pl8pDDOIlVCaBGbVAkYw6x3GCIptw3bANle4pz8ICwX')          #order API
#bitfinexAccount = BitfinexAccount('4bY5ZpWrrlUuwGo93AZqrkllxS7xPIyi3jMB2bUCmx5','X8Mo3PeahGhMeSiW8Q5VLQZM4t0mvk0lLD5BR7ngNMp')   #read only API
transactor = Transactor(0,{'usd' : 100 , 'eth' : 0.108 , 'btc' : 0 , 'zec' : 0},{'usd' : 0 , 'eth' : 0.65 , 'btc' : 0 , 'zec' : 0},currencyPrice.getPrice())
while True:
       transactor.action(currencyPrice.getPrice(), bitfinexAccount)
       time.sleep(5)
