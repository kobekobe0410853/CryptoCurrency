# -*- coding: cp950 -*-
from TurningPoint import *
from CurrencyPrice import *
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
              time.sleep(2) #要delay 因為 multi thread 速度太慢 無法跟新參數
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
              if self.orderTransactedSuccess  == False:
                     self.orderTransactedSuccess  = True
                     ordersNow = bitfinexAccount.getOrdersNow()
                     # VV 沒賣掉 ticker +1
                     for row in bitfinexAccount.getOrdersNow():
                            #print row['id'],type(row['id'])
                            if long( row['id'] ) == long( self.myOrderId ):
                                   self.orderTransactedSuccess = False
                                   self.orderTicker += 1
                     ####
                     if self.orderTransactedSuccess :
                            # VV 賣掉了
                            print '              //transactor%d 訂單已經買進或賣出了 ! ! !' % self.transactorNumber
                            self.orderTicker = 0
                            if self.previousAction == 'buy':
                                   self.sellSuccess('eth', self.priceWhenMakeOrder['eth'] )
                                   self.previousAction = 'sell' 
                            elif self.previousAction == 'sell':
                                   self.buySuccess('eth', self.priceWhenMakeOrder['eth'] )
                                   self.previousAction = 'buy'
                            self.previousActionPrice = self.priceWhenMakeOrder
                            self.orderTicker = 0
                     else :
                            print '              //transactor%d 下的訂單 還在 // order is still alive' % self.transactorNumber
                            if self.previousAction == 'sell' and self.turningPoint.isStillAscending()==False:
                                   self.orderTicker = 100
                            if self.orderTicker >= 30:
                                   # 如果tick 30次 還沒賣掉  那就: 取消訂單, ticker規0, orderTransactedSuccessFLAG設為True 讓他可以執行下一筆交易
                                   bitfinexAccount.deleteOrder(self.myOrderId)
                                   self.orderTransactedSuccess = True
                                   print '          -- 取消訂單 !!!!!!!!!!'
                                   print '          -- transactor ' , self.transactorNumber
                                   print '          -- delete the Order ID:' , self.myOrderId
                                   print 
                                   self.orderTicker = 0
              elif ( self.orderTransactedSuccess\
              and self.previousAction == 'buy'\
              and self.predictAscendingWrongFlag == True )\
              or ( self.orderTransactedSuccess\
              and self.previousAction == 'buy'\
              and CurrencyPrice['eth'] > (self.previousActionPrice['eth']+self.deltaPriceToTrans['eth']) \
              and self.exchanges['eth'] >= 0.1\
              and self.isTheTransPoint('isHighPoint?')\
              and self.isProfitBiggerThanFee('eth', CurrencyPrice['eth']) ):    #   "看多預測錯誤 賣"  or  "漲 賣"             
                     ## 賣
                     self.myOrderId = long( bitfinexAccount.makeOrder( 0.1, CurrencyPrice['eth'], 'sell', 'exchange limit', 'ethusd')[u'order_id'] )
                     print '下訂單 !!!!!!!!!!'
                     print '// transactor ' , self.transactorNumber
                     print '// the Order ID:' , self.myOrderId
                     print 
                     self.orderTransactedSuccess = False
                     #self.orderTransactedSuccess = True
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
                     self.myOrderId = long( bitfinexAccount.makeOrder( 0.1, CurrencyPrice['eth']+0.1, 'buy', 'exchange limit', 'ethusd')[u'order_id'] )
                     print '下訂單 !!!!!!!!!!'
                     print '// transactor ' , self.transactorNumber
                     print '// the Order ID:' , self.myOrderId
                     print 
                     self.orderTransactedSuccess = False
                     #self.orderTransactedSuccess = True
                     self.priceWhenMakeOrder = CurrencyPrice
                     time.sleep(3)
       def sellSuccess(self, currency, price):
              if currency == 'eth':
                     self.exchanges['usd'] += 0.1 * price
                     self.exchanges['eth'] -= 0.1
                     self.sendTransActionToDatabase(-0.1, 0.1 * price, price, 'sold ETH')
                     print '↘  %s' % datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                     print '   Transactor %d  /price%.2f/     %.3f  sold  %.1f' % (self.transactorNumber, price, 0.1 * (price), 0.1),'  Finance *%.1feth *%.4fusd  =%.4fusd'%(self.exchanges['eth'], self.exchanges['usd'], self.exchanges['usd']+self.exchanges['eth']*price)
                     print
              #thread.start_new_thread( self.refreshPreviousActionPrice,())
       def buySuccess(self, currency, price):
              if currency == 'eth':
                     self.exchanges['usd'] -= 0.1 * (price+0.1)
                     self.exchanges['eth'] += 0.1
                     self.sendTransActionToDatabase(0.1, -0.1 * (price+0.1), price+0.1, 'buy ETH')
                     print '↘  %s' % datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                     print '   Transactor %d  /price%.2f/     %.3f  buy  %.1f' % (self.transactorNumber, price+0.1, 0.1 * (price+0.1), 0.1),'  Finance *%.1feth *%.4fusd  =%.4fusd'%(self.exchanges['eth'], self.exchanges['usd'], self.exchanges['usd']+self.exchanges['eth']*price)              
                     print
              thread.start_new_thread( self.predictAscendingWrong,())
       def predictAscendingWrong(self):
              self.predictAscendingWrongFlag = False
              while True:
                     # 如果這筆看多      漲幅已經超過手續費      就成功預測會漲
                     if self.currencyPrice.getPrice()['eth'] - (self.previousActionPrice['eth']+0.1) > self.currencyPrice.getPrice()['eth']*0.0055:
                            break
                     elif self.turningPoint.connectDatabaseAndCalculateSumDelta(0.00333) < -0.16:  #2min 又跌回來  0.16       
                            self.predictAscendingWrongFlag = True
                            print 
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
