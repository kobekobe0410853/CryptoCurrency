# -*- coding: cp950 -*-
class MyOrder:
       orderInfo = []
        #0   �q��s�� ID
         #1    �q��s�� CID
          #2    �������  ex: 'ethusd' ,  'btcusd'
           #3     price
            #4     amount 
             #5     �ʧ@       ex: 'buy' , 'sell'
              #6      time stamp
               #7      date
                #8      transactor Number 
       def __init__(self, orderInfo, transNum):
              self.orderInfo = orderInfo
              self.orderInfo.append(transNum)
