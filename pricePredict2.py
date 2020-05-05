import keras
import random
import time
import datetime
import math
import thread
import os 
import sys
import numpy as np 
from scipy import stats
from pytz import utc,timezone
from sklearn.linear_model import LinearRegression
from influxdb import InfluxDBClient
class PricePredict:
    def __init__(self):
        self.measurement = ['btcusd','ethusd','zecusd']
        self.field = ['price','buyAmount','sellAmount','volume']
        #tmp = {'price':[],'sellAmount':[],'buyAmount':[],'volume':[]} 
        self.item = {'btcusd':{'price':[],'sellAmount':[],'buyAmount':[],'volume':[]},\
                     'ethusd':{'price':[],'sellAmount':[],'buyAmount':[],'volume':[]},\
                     'zecusd':{'price':[],'sellAmount':[],'buyAmount':[],'volume':[]}}
        self.input = {'btcusd':[],'ethusd':[],'zecusd':[]}
        self.output = {'btcusd':[],'ethusd':[],'zecusd':[]}
    def getFromInfluxdb(self,flag24=0,timeStamp=0,limit=-1,flag1=0):
        self.__init__()
        host = '140.113.122.202'
        port = 8086
        user = 'root'
        password = '1234567890'
        dbname = 'virtualCurrencyPrice'
        client = InfluxDBClient(host,port,user,password,dbname)
        if flag24==1 and timeStamp==0:
            strtmp = 'where time > now()-25h'
        elif flag24==1 and timeStamp!=0:
            strtmp = 'where time > %f'%(timeStamp-28800-25*60*60)
        elif flag24==0 and limit!=0:
            strtmp = 'limit %d'%(limit)
        elif flag24==0 and limit==-1:
            strtmp = ''
        if flag1==1:
            strtmp = 'where time > now()-360h'
        for measurement in self.measurement:
            for field in self.field:
                query = 'select %s from %s %s' % (field,measurement,strtmp)
                response = client.query(query)
                try:
                    response = list(response)[0]
                    #print response
                    for i in range(0,len(response)):
                        response[i]['time'] = self.datetimeToTimestamp(response[i]['time'])
                    self.item[measurement][field] = response 
                except Exception as e:
                    pass
        #print self.item['ethusd']['price']
        #time.sleep(1222) 
    def datetimeToTimestamp(self,T):
        timestamp = time.mktime( utc.localize(datetime.datetime.strptime(T,'%Y-%m-%dT%H:%M:%SZ')).utctimetuple() )
        return timestamp 

    def slope(self,timeStamp,timeDelta=5,measurement='btcusd',field='price'):
        fromTimeStamp = timeStamp-timeDelta*60
        tmpY = []
        tmpX = []
        for i in range(0,len(self.item[measurement][field])):
            if fromTimeStamp<self.item[measurement][field][i]['time'] and timeStamp>self.item[measurement][field][i]['time']:
                tmpY.append(self.item[measurement][field][i][field])
                tmpX.append(self.item[measurement][field][i]['time'])
            elif timeStamp<self.item[measurement][field][i]['time']:
                break
        if len(tmpY)<2 or len(tmpX)<2:
            return 'no data'
        tmpY = np.asarray(tmpY)
        tmpX = np.asarray(tmpX)
        slope,yIntercept,correlationValue,pValue,stdError = stats.linregress(tmpX,tmpY)
        return slope

    def average(self,timeStamp,timeDelta=5,measurement='btcusd',field='price'):
        tmp = []
        for i in range(0,len(self.item[measurement][field])):
            if self.item[measurement][field][i]['time'] > timeStamp-timeDelta*60\
            and self.item[measurement][field][i]['time'] < timeStamp:
                tmp.append( self.item[measurement][field][i][field] )
            elif self.item[measurement][field][i]['time']>timeStamp:
                break 
        if len(tmp)==0:
            return 'no data'
        return float(sum(tmp))/len(tmp)
    
    def ratio(self,timeStamp1,timeDelta1,timeStamp2,timeDelta2,measurement='btcusd',field='price',mode=0):
        if mode==0:
            num1 = self.average(timeStamp1,timeDelta1,measurement,field) 
            num2 = self.average(timeStamp2,timeDelta2,measurement,field)
            if num1=='no data' or num2=='no data':
                return 'no data' 
            return float(num1-num2)/num1
        num1 = self.average(timeStamp1,timeDelta1,measurement,'sellAmount')
        num2 = self.average(timeStamp2,timeDelta2,measurement,'buyAmount')
        if num1=='no data' or num2=='no data':
            return 'no data'
        if mode==1:
            #ratio of sell/buy 5min
            return num1/num2
        elif mode==2:
            #ratio of buy/sell 5min
            return num2/num1

    def trend(self,timeStamp,measurement='ethusd',field='price'):
        num1 = self.average(timeStamp-10*60,5,measurement,'price')
        num2 = self.average(timeStamp,5,measurement,'price')
        if num1=='no data' or num2=='no data':
            return 'no data'
        elif num2>num1:
            return 1
        elif num1>num2:
            return -1
        else :
            return 0

    def formPredictData(self,measurement='btcusd',timeStamp=0):
        if timeStamp==0:
            timeStamp = time.time()-28800
        else:
            timeStamp-=28800
        tmp1 = []
        tmp1.append(self.average(timeStamp,0.5,measurement,'price'))                         #past 0.5min price avg
        tmp1.append(self.slope(timeStamp,15,measurement,'price'))                            #slope of 15min  price
        tmp1.append(self.slope(timeStamp,60,measurement,'price'))                            #slope of 60min  price
        tmp1.append(self.slope(timeStamp,360,measurement,'price'))                           #slope of 3hr    price 
        tmp1.append(self.ratio(timeStamp,0.5,timeStamp-0.5*60,0.5,measurement,'sellAmount')) #ratio of 1min  sellAmount   increase
        tmp1.append(self.ratio(timeStamp,0.5,timeStamp-0.5*60,0.5,measurement,'buyAmount'))  #ratio of 1min  buyAmount    increase
        tmp1.append(self.ratio(timeStamp,1,timeStamp,1,measurement,'sell/buy Amount',1))     #ratio of 1min  sellAmount / buyAmount
        tmp1.append(self.ratio(timeStamp,1,timeStamp,1,measurement,'buy/sell Amount',2))     #ratio of 1min  buyAmount  / sellAmount
        tmp1.append(self.ratio(timeStamp,1.5,timeStamp-1.5*60,1.5,measurement,'sellAmount')) #ratio of 3min  sellAmount   increase
        tmp1.append(self.ratio(timeStamp,1.5,timeStamp-1.5*60,1.5,measurement,'buyAmount'))  #ratio of 3min  buyAmount    increase
        tmp1.append(self.ratio(timeStamp,3,timeStamp,3,measurement,'sell/buy Amount',1))     #ratio of 3min  sellAmount / buyAmount
        tmp1.append(self.ratio(timeStamp,3,timeStamp,3,measurement,'buy/sell Amount',2))     #ratio of 3min  buyAmount  / sellAmount
        tmp1.append(self.ratio(timeStamp,4.5,timeStamp-4.5*60,4.5,measurement,'sellAmount')) #ratio of 9min  sellAmount   increase
        tmp1.append(self.ratio(timeStamp,4.5,timeStamp-4.5*60,4.5,measurement,'buyAmount'))  #ratio of 9min  buyAmount    increase
        tmp1.append(self.ratio(timeStamp,9,timeStamp,9,measurement,'sell/buy Amount',1))     #ratio of 9min  sellAmount / buyAmount
        tmp1.append(self.ratio(timeStamp,9,timeStamp,9,measurement,'buy/sell Amount',2))     #ratio of 9min  buyAmount  / sellAmount
        if  tmp1.count('no data')==0 and len(tmp1)!=0:
            return [tmp1]
        else:
            return 'no data'
    def formTrainingData(self,measurement='btcusd'):
        self.trainingDataX = []
        self.trainingDataY = []
        #self.trainingDataZ = []
        count = 0
        for item in self.item[measurement]['price']:
            count+=1
            timeStamp = item['time']
            tmp1 = []
            tmp2 = []
            #tmp3 = []

            tmp1.append(self.average(timeStamp,0.5,measurement,'price'))                         #past 0.5min price avg
	    tmp1.append(self.slope(timeStamp,15,measurement,'price'))                            #slope of 15min  price
	    tmp1.append(self.slope(timeStamp,60,measurement,'price'))                            #slope of 60min  price
            tmp1.append(self.slope(timeStamp,360,measurement,'price'))                           #slope of 3hr    price 
            tmp1.append(self.ratio(timeStamp,0.5,timeStamp-0.5*60,0.5,measurement,'sellAmount')) #ratio of 1min  sellAmount   increase
            tmp1.append(self.ratio(timeStamp,0.5,timeStamp-0.5*60,0.5,measurement,'buyAmount'))  #ratio of 1min  buyAmount    increase
            tmp1.append(self.ratio(timeStamp,1,timeStamp,1,measurement,'sell/buy Amount',1))     #ratio of 1min  sellAmount / buyAmount
            tmp1.append(self.ratio(timeStamp,1,timeStamp,1,measurement,'buy/sell Amount',2))     #ratio of 1min  buyAmount  / sellAmount
            tmp1.append(self.ratio(timeStamp,1.5,timeStamp-1.5*60,1.5,measurement,'sellAmount')) #ratio of 3min  sellAmount   increase
            tmp1.append(self.ratio(timeStamp,1.5,timeStamp-1.5*60,1.5,measurement,'buyAmount'))  #ratio of 3min  buyAmount    increase
            tmp1.append(self.ratio(timeStamp,3,timeStamp,3,measurement,'sell/buy Amount',1))     #ratio of 3min  sellAmount / buyAmount
            tmp1.append(self.ratio(timeStamp,3,timeStamp,3,measurement,'buy/sell Amount',2))     #ratio of 3min  buyAmount  / sellAmount
            tmp1.append(self.ratio(timeStamp,4.5,timeStamp-4.5*60,4.5,measurement,'sellAmount')) #ratio of 9min  sellAmount   increase
            tmp1.append(self.ratio(timeStamp,4.5,timeStamp-4.5*60,4.5,measurement,'buyAmount'))  #ratio of 9min  buyAmount    increase
            tmp1.append(self.ratio(timeStamp,9,timeStamp,9,measurement,'sell/buy Amount',1))     #ratio of 9min  sellAmount / buyAmount
            tmp1.append(self.ratio(timeStamp,9,timeStamp,9,measurement,'buy/sell Amount',2))     #ratio of 9min  buyAmount  / sellAmount
        
            tmp2.append(self.average(timeStamp+1*60,1,measurement,'price'))                   ###price  1min average of  0min later
            tmp2.append(self.average(timeStamp+2*60,1,measurement,'price'))                   ###price  1min average of  1min later
            tmp2.append(self.average(timeStamp+3*60,1,measurement,'price'))                   ###price  1min average of  2min later
            tmp2.append(self.average(timeStamp+4*60,1,measurement,'price'))                   ###price  1min average of  3min later
            tmp2.append(self.average(timeStamp+5*60,1,measurement,'price'))                   ###price  1min average of  4min later
            tmp2.append(self.average(timeStamp+6*60,1,measurement,'price'))                   ###price  1min average of  5min later
            tmp2.append(self.average(timeStamp+7*60,1,measurement,'price'))                   ###price  1min average of  6min later
            tmp2.append(self.average(timeStamp+8*60,1,measurement,'price'))                   ###price  1min average of  7min later
            tmp2.append(self.average(timeStamp+9*60,1,measurement,'price'))                   ###price  1min average of  8min later
            tmp2.append(self.average(timeStamp+10*60,1,measurement,'price'))                  ###price  1min average of  9min later
            tmp2.append(self.average(timeStamp+11*60,1,measurement,'price'))                  ###price  1min average of 10min later
            tmp2.append(self.average(timeStamp+12*60,1,measurement,'price'))                  ###price  1min average of 11min later
            tmp2.append(self.average(timeStamp+13*60,1,measurement,'price'))                  ###price  1min average of 12min later
            tmp2.append(self.average(timeStamp+14*60,1,measurement,'price'))                  ###price  1min average of 13min later
            tmp2.append(self.average(timeStamp+15*60,1,measurement,'price'))                  ###price  1min average of 14min later
            """
            #tmp3 part
            division = 5
            h = 5
            calc = [0]*division
            tmp3 = [0]*division
            if tmp2.count('no data') == 0:
                for i in range(len(tmp2)):
                    calc[] += 1

            tmp3[calc.index(maxcalc)] = 1
            """

            #tmp2.append(self.ratio(timeStamp+5*60,5,timeStamp,5,measurement,'price'))       ###ratio of 15min prospect
            #tmp2.append(self.trend(timeStamp+5*60,measurement,'price'))           ###trend of 15min increase/decrease
            if tmp1.count('no data')+tmp2.count('no data')==0 and len(tmp1)!=0 and len(tmp2)!=0:
                self.trainingDataX.append(tmp1)
                self.trainingDataY.append(tmp2)
                self.trainingDataZ.append(tmp3)
            #if random.randint(0,100)<70:
            self.writeData(measurement)
            self.trainingDataX = []
            self.trainingDataY = []
            self.trainingDataZ = []    
            os.system('cls' if os.name == 'nt' else 'clear')
            print 'percentage ',float(100*count)/len(self.item[measurement]['price']),'% complete' 
            print 'length     ',len(self.item[measurement]['price'])
            sys.stdout.flush()
            #time.sleep(2)
    def writeData(self,measurement='btcusd'):
        fx = open('{}{}'.format(measurement,'_traingX.txt'),'a')
        fy = open('{}{}'.format(measurement,'_traingY.txt'),'a')
        #fz = open('{}{}'.format(measurement,'_traingZ.txt'), 'a')
        for i in range(0,len(self.trainingDataX)):
            fx.write(str(self.trainingDataX[i]))
            fx.write(str('\n'))
            fy.write(str(self.trainingDataY[i]))
            fy.write(str('\n')) 
            #fz.write(str(self.trainingDataZ[i]))
            #fz.write(str('\n'))
        fx.close()
        fy.close()
           
symbols = ['ethusd','btcusd','zecusd'] 
if __name__=='__main__':
    pricePredict = PricePredict()
    pricePredict.getFromInfluxdb(1,0,7000,1)
    for symbol in ['ethusd']:
        pricePredict.formTrainingData(symbol)
        pricePredict.writeData(symbol)
