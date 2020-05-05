# -*- coding: cp950 -*-
class MyOrder:
       orderInfo = []
        #0   訂單編號 ID
         #1    訂單編號 CID
          #2    交易類型  ex: 'ethusd' ,  'btcusd'
           #3     price
            #4     amount 
             #5     動作       ex: 'buy' , 'sell'
              #6      time stamp
               #7      date
                #8      transactor Number 
       def __init__(self, orderInfo, transNum):
              self.orderInfo = orderInfo
              self.orderInfo.append(transNum)
