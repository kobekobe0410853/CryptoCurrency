# -*- coding: cp950 -*-
import os
import math
import time
import datetime
import thread
from Transactor import *
from CurrencyPrice import *
class Monitor:
       def __init__(self, bitfinexAccount):
              self.setParameters( bitfinexAccount)
       def setParameters(self, bitfinexAccount):
              self.bitfinexAccount = bitfinexAccount
              self.exchanges = {'usd' : 0 , 'eth' : 0 , 'btc' : 0 , 'zec' : 0}
              self.deltaPriceToTrans = {'usd' : 0 , 'eth' : 0.65 , 'btc' : 0 , 'zec' : 0}
              #self.transactorNumber = input('      交易員數量 / how many transacotrs :  ')
              #self.deltaPriceToTrans = input('      漲跌多少做交易 / deltaPriceToTrans :  ')
              self.transactor = []
              self.currencyPrice = CurrencyPrice()
              balances = bitfinexAccount.getBalances()
              self.todayDate = datetime.datetime.now().date()
              for row in balances:
                     if row['currency'] == 'usd' and row['type'] == 'exchange': 
                            self.exchanges['usd'] = row['amount']                     
                     elif row['currency'] == 'btc' and row['type'] == 'exchange': 
                            self.exchanges['btc'] = row['amount']
                     elif row['currency'] == 'zec' and row['type'] == 'exchange':
                            self.exchanges['zec'] = row['amount']
                     elif row['currency'] == 'eth' and row['type'] == 'exchange':
                            self.exchanges['eth'] = row['amount']
                            self.transactorNumber = int( math.floor( (row['amount'])/(0.108)) )
                            if self.transactorNumber < 2:
                                   self.transactorNumber = 1
                            self.transactorNumber = 1
              os.system('cls')
              print
              print '      total exchange       *%.3fusd *%.3feth *%.3fzec' %(self.exchanges['usd'],self.exchanges['eth'],self.exchanges['zec'])
              print '      transactor num      * %d ' % self.transactorNumber
              #self.isFinanceDistributeByHand = raw_input('      finance distributing by hand (Y/N) ?  ')
              print '      finance distributing by hand (Y/N) ?  n'
              self.isFinanceDistributeByHand = 'n'
              print
              for i in range(0,self.transactorNumber):
                     self.transactor.append( Transactor( i, self.exchangeDistribute(i), self.deltaPriceToTrans, self.currencyPrice.getPrice()) )
       def exchangeDistribute(self,i):
              if  self.isFinanceDistributeByHand == 'Y':
                     usdTmp = self.exchanges['usd']
                     ethTmp = self.exchanges['eth']
                     for k in range(0,i):
                            usdTmp -= self.transactor[k].exchanges['usd']
                            ethTmp -= self.transactor[k].exchanges['eth']
                     usdFinance = input('transactor%d finance usd:'%i)
                     ethFinance = input('transactor%d finance eth:'%i)
                     while usdTmp < usdFinance or ethTmp < ethFinance:
                            usdFinance = input('dtransactor%d finance usd:'%i)
                            ethFinance = input('dtransactor%d finance eth:'%i)
                     return {'usd' : usdFinance , 'eth' : ethFinance , 'btc' : '0' , 'zec' : '0'}
              else :
                     if self.exchanges['eth']-0.108*i >= 0.108:
                            exchangesTmp = {'usd' : float(self.exchanges['usd'])/self.transactorNumber , 'eth' : 0.108 , 'btc' : 0 , 'zec' : 0}
                     else:
                            exchangesTmp = {'usd' : float(self.exchanges['usd'])/self.transactorNumber , 'eth' : 0 , 'btc' : 0 , 'zec' : 0}
                     print 'transactor%d %s' %(i,exchangesTmp)
                     return exchangesTmp
       def refreshMonitor(self):
              if self.todayDate != datetime.datetime.now().date():
                     self.bitfinexAccount.refresh()
                     self = Monitor( self.bitfinexAccount )
       def moniting(self):
              thread.start_new_thread(self.showInformations,())
              while True:
                     #self.refreshMonitor()
                     for i in range(0,self.transactorNumber):
                            self.exchanges['usd'] -= self.transactor[i].exchanges['usd']
                            self.exchanges['eth'] -= self.transactor[i].exchanges['eth']
                            
                            self.transactor[i].action( self.currencyPrice.getPrice(), self.bitfinexAccount)
                            
                            self.exchanges['usd'] += self.transactor[i].exchanges['usd']
                            self.exchanges['eth'] += self.transactor[i].exchanges['eth']
                            
                            time.sleep(5)
                     #self.bitfinexAccount.showBalancesWorth()
       def showInformations(self):
              while True:
                     print '      price%.2f   total finance *%.3fusd *%.3feth =%.3fusd      %s' % (self.currencyPrice.getPrice()['eth'], self.exchanges['usd'], self.exchanges['eth'], self.exchanges['usd']+self.exchanges['eth']*self.currencyPrice.getPrice()['eth'], datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))        
                     time.sleep(30)
                     
