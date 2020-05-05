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
                     self.previousAction = 'sell'       #### �����i�ӳ��n���R eth 
              else :
                     self.previousAction = 'sell'
              self.previousActionPrice = currencyPriceNow
              thread.start_new_thread( self.recentDayDescendingWatching,())
              thread.start_new_thread( self.refreshPreviousHoursPrice,())
              time.sleep(2) #�ndelay �]�� multi thread �t�פӺC �L�k��s�Ѽ�
       def refreshPreviousHoursPrice(self):
              self.refreshTime = 60*5
              while True:
                     if self.previousAction == 'sell':
                            self.previousHoursPrice = self.currencyPrice.getPrice(1.8)
                            # 1.8 �p��      /        108����
                            #thread.start_new_thread( self.refreshPreviousActionPrice,())
                     time.sleep(self.refreshTime)       # sleep 5 min
       def recentDayDescendingWatching(self):
              while True:
                     # 8 �p�ɤ��^�F5�� "�i��Y�L�F"
                     if self.turningPoint.connectDatabaseAndCalculateSumDelta(8) < -5:
                            self.recentDayDescendingFlag = True
                     else :
                            self.recentDayDescendingFlag =  False
                     time.sleep(60*30) # 30min
       def action(self, CurrencyPrice, bitfinexAccount):
              if self.orderTransactedSuccess  == False:
                     self.orderTransactedSuccess  = True
                     ordersNow = bitfinexAccount.getOrdersNow()
                     # VV �S�汼 ticker +1
                     for row in bitfinexAccount.getOrdersNow():
                            #print row['id'],type(row['id'])
                            if long( row['id'] ) == long( self.myOrderId ):
                                   self.orderTransactedSuccess = False
                                   self.orderTicker += 1
                     ####
                     if self.orderTransactedSuccess :
                            # VV �汼�F
                            print '              //transactor%d �q��w�g�R�i�ν�X�F ! ! !' % self.transactorNumber
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
                            print '              //transactor%d �U���q�� �٦b // order is still alive' % self.transactorNumber
                            if self.previousAction == 'sell' and self.turningPoint.isStillAscending()==False:
                                   self.orderTicker = 100
                            if self.orderTicker >= 30:
                                   # �p�Gtick 30�� �٨S�汼  ���N: �����q��, ticker�W0, orderTransactedSuccessFLAG�]��True ���L�i�H����U�@�����
                                   bitfinexAccount.deleteOrder(self.myOrderId)
                                   self.orderTransactedSuccess = True
                                   print '          -- �����q�� !!!!!!!!!!'
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
              and self.isProfitBiggerThanFee('eth', CurrencyPrice['eth']) ):    #   "�ݦh�w�����~ ��"  or  "�� ��"             
                     ## ��
                     self.myOrderId = long( bitfinexAccount.makeOrder( 0.1, CurrencyPrice['eth'], 'sell', 'exchange limit', 'ethusd')[u'order_id'] )
                     print '�U�q�� !!!!!!!!!!'
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
              and self.isTheTransPoint('isLowPoint?'):      #�^ �R               
                     ## �R          and CurrencyPrice['eth']  < (self.previousActionPrice['eth']-self.deltaPriceToTrans['eth'])
                     self.myOrderId = long( bitfinexAccount.makeOrder( 0.1, CurrencyPrice['eth']+0.1, 'buy', 'exchange limit', 'ethusd')[u'order_id'] )
                     print '�U�q�� !!!!!!!!!!'
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
                     print '��  %s' % datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                     print '   Transactor %d  /price%.2f/     %.3f  sold  %.1f' % (self.transactorNumber, price, 0.1 * (price), 0.1),'  Finance *%.1feth *%.4fusd  =%.4fusd'%(self.exchanges['eth'], self.exchanges['usd'], self.exchanges['usd']+self.exchanges['eth']*price)
                     print
              #thread.start_new_thread( self.refreshPreviousActionPrice,())
       def buySuccess(self, currency, price):
              if currency == 'eth':
                     self.exchanges['usd'] -= 0.1 * (price+0.1)
                     self.exchanges['eth'] += 0.1
                     self.sendTransActionToDatabase(0.1, -0.1 * (price+0.1), price+0.1, 'buy ETH')
                     print '��  %s' % datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                     print '   Transactor %d  /price%.2f/     %.3f  buy  %.1f' % (self.transactorNumber, price+0.1, 0.1 * (price+0.1), 0.1),'  Finance *%.1feth *%.4fusd  =%.4fusd'%(self.exchanges['eth'], self.exchanges['usd'], self.exchanges['usd']+self.exchanges['eth']*price)              
                     print
              thread.start_new_thread( self.predictAscendingWrong,())
       def predictAscendingWrong(self):
              self.predictAscendingWrongFlag = False
              while True:
                     # �p�G�o���ݦh      ���T�w�g�W�L����O      �N���\�w���|��
                     if self.currencyPrice.getPrice()['eth'] - (self.previousActionPrice['eth']+0.1) > self.currencyPrice.getPrice()['eth']*0.0055:
                            break
                     elif self.turningPoint.connectDatabaseAndCalculateSumDelta(0.00333) < -0.16:  #2min �S�^�^��  0.16       
                            self.predictAscendingWrongFlag = True
                            print 
                            print '�ݦh�w�����~ !!!!!!'
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
