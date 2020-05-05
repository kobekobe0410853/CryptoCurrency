# -*- coding: cp950 -*-
from client import Client, TradeClient
from CurrencyPrice import *
import datetime
import time
class BitfinexAccount:
       balances = []  #餘額表
       ordersNow = []   #目前的訂單
       key = 'null'
       keyPassword = 'null'
       def __init__(self,key,keyPassword):
              self.key = key
              self.keyPassword = keyPassword
              self.tradeClient = TradeClient( key, keyPassword)
              self.currencyPrice = CurrencyPrice()
              self.balances = []    #清空餘額表
              self.ordersNow = []    #清空目前的訂單
              # format BALANCE into balances[]    抓餘額
              for row in self.tradeClient.balances():
                     tmp = {'currency' : '' , 'type' : '' , 'amount' : '' }
                     tmp['currency'] = str(row[u'currency'])               #0   虛擬貨幣名稱
                     tmp['type']       = str(row[u'type'])                      #1   餘額類型 ex: 'exchange' , 'trading' , 'funding'
                     tmp['amount']   = float(row[u'amount'])                 #2   數量
                     self.balances.append(tmp)
                     #print tmp
              # format ORDERS into ordersNow[]    抓現在的掛單
              for row in self.tradeClient.active_orders():
                     tmp = {'id' : '', 'cid' : '' , 'symbol' : '' , 'price' : '' , 'amount' : '' , 'side' : '' , 'timestamp' : '' , 'cid_date' : '' }
                     tmp['id']              = long(row[u'id'])                            #0   訂單編號 ID
                     tmp['cid']             = long(row[u'cid'])                           #1    訂單編號 CID
                     tmp['symbol']       = str(row[u'symbol'])                         #2    交易類型  ex: 'ethusd' ,  'btcusd'
                     tmp['price']          = float(row[u'price'])                          #3     price
                     tmp['amount']       = float(row[u'original_amount'])             #4     amount 
                     tmp['side']           = str(row[u'side'])                               #5     動作       ex: 'buy' , 'sell'
                     tmp['timestamp']   = str(row[u'timestamp'])                       #6      time stamp
                     tmp['cid_date']      = str(row[u'cid_date'])                           #7      date
                     self.ordersNow.append(tmp)
                     #print row
       def refresh(self):
              try:
                     self.balances = []    #清空餘額表
                     self.ordersNow = []    #清空目前的訂單
                     # format BALANCE into balances[]    抓餘額
                     for row in self.tradeClient.balances():
                            tmp = {'currency' : '' , 'type' : '' , 'amount' : '' }
                            tmp['currency'] = str(row[u'currency'])               #0   虛擬貨幣名稱
                            tmp['type']       = str(row[u'type'])                      #1   餘額類型 ex: 'exchange' , 'trading' , 'funding'
                            tmp['amount']   = float(row[u'amount'])                 #2   數量
                            self.balances.append(tmp)
                            #print tmp
                     # format ORDERS into ordersNow[]    抓現在的掛單
                     for row in self.tradeClient.active_orders():
                            tmp = {'id' : '', 'cid' : '' , 'symbol' : '' , 'price' : '' , 'amount' : '' , 'side' : '' , 'timestamp' : '' , 'cid_date' : '' }
                            tmp['id']              = long(row[u'id'])                            #0   訂單編號 ID
                            tmp['cid']             = long(row[u'cid'])                           #1    訂單編號 CID
                            tmp['symbol']       = str(row[u'symbol'])                         #2    交易類型  ex: 'ethusd' ,  'btcusd'
                            tmp['price']          = float(row[u'price'])                          #3     price
                            tmp['amount']       = float(row[u'original_amount'])             #4     amount 
                            tmp['side']           = str(row[u'side'])                               #5     動作       ex: 'buy' , 'sell'
                            tmp['timestamp']   = str(row[u'timestamp'])                       #6      time stamp
                            tmp['cid_date']      = str(row[u'cid_date'])                           #7      date
                            self.ordersNow.append(tmp)
                            #print row
              except Exception as inst:
                     print 'ERROR while refresh BitfinexAccount !!  ' , inst
                     time.sleep(1)
                     self.refresh()
       def showBalancesWorth(self):
              self.refresh()
              #print 'VV  price%.2f   *%.3fusd *%.1feth =%.3fusd       %s' % (self.currencyPrice.getPrice()['eth'], self.balances['usd']['exchange'], self.balances['eth']['exchange'], self.balances['usd']['exchange']+self.balances['eth']['exchange']*self.currencyPrice.getPrice()['eth'], datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))  
       def showBalances(self):
              self.refresh()
              for row in self.balances:
                     print row
       def getBalances(self):
              self.refresh()
              return self.balances
       def showOrdersNow(self):
              self.refresh()
              for row in self.ordersNow:
                     print row
       def getOrdersNow(self):
              self.refresh()
              return self.ordersNow
       def orderStatus(self, orderId):                                # 無法使用 !!!
              return self.tradeClient.status_order(orderId)
       def makeOrder(self, amount=0, price=0, side='buy', ord_type='exchange limit', symbol='ethusd', exchange='bitfinex'):
              #      side            =      'buy'       'sell'
              #      ord_type      =      'exchange limit'   'funding limit'
              #      symbol        =      'ethusd'      'btcusd'      'zecusd'
              try:
                     text = self.tradeClient.place_order(str(amount), str(price), side, ord_type, symbol, exchange)
                     #self.refresh()
                     return text
              except Exception as inst:
                     time.sleep(0.3)
                     return self.makeOrder(self, amount, price, side, ord_type, symbol, exchange)
       def deleteOrder(self, id_):
              self.tradeClient.delete_order(id_)
              self.refresh()



#myBitfinexAccount = BitfinexAccount('SjT8YsP7dit0iBI7Rl1egrGuI2R5lZfK4Gnz9TOJbS1','pl8pDDOIlVCaBGbVAkYw6x3GCIptw3bANle4pz8ICwX')          #order API
#myBitfinexAccount = BitfinexAccount('4bY5ZpWrrlUuwGo93AZqrkllxS7xPIyi3jMB2bUCmx5','X8Mo3PeahGhMeSiW8Q5VLQZM4t0mvk0lLD5BR7ngNMp')   #read only API
#myBitfinexAccount.showBalances()
#print
#myBitfinexAccount.showNowOrders()
