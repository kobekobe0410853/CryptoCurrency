import keras
import random
import time
import datetime
import math
import thread
import os 
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
    def getFromInfluxdb(self,flag24=0):
        host = '140.113.122.202'
        port = 8086
        user = 'root'
        password = '1234567890'
        dbname = 'virtualCurrencyPrice'
        client = InfluxDBClient(host,port,user,password,dbname)
        #fromTimeStr = datetime.datetime.fromtimestamp(timeStamp-28800-86555).strftime('%Y-%m-%dT%H:%M:%SZ')
        for measurement in self.measurement:
            for field in self.field:
                query = 'select volume from ethusd where price>360'
                #timeStr = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%dT%H:%M:%SZ')
                if flag24 == 1:
                    query = 'select %s from %s where time > now()-25h' % (field, measurement)
                else:
                    query = 'select %s form %s ' % (field,measurement)
                response = client.query(query) 
                response = list(response)[0]
                for i in range(0,len(response)):
                    response[i]['time'] = self.datetimeToTimestamp(response[i]['time'])
                self.item[measurement][field] = response 
        #f = open('item.txt','w')
        #f.write(str(self.item))
        #print self.item['ethusd']['price'][0] 
        #print 'load self.item done'
    def datetimeToTimestamp(self,T):
        timestamp = time.mktime( utc.localize(datetime.datetime.strptime(T,'%Y-%m-%dT%H:%M:%SZ')).utctimetuple() )
        return timestamp 
    def slot(self):
        i=0 
    def linearRegression(self,measurement='btcusd',field='price',timeStamp=0,timeDelta=0.5,predictTime=0.1):
        tmp = self.item[measurement][field]
        timeDelta = timeDelta*60*60
        fromTimeStamp = timeStamp-timeDelta
        destTimeStamp = timeStamp
        tmpValue = []
        tmpTime = []
        for i in range(0,len(tmp)):
            if tmp[i]['time'] > fromTimeStamp and tmp[i]['time'] < destTimeStamp:
                tmpValue.append(tmp[i][field])
                tmpTime.append(tmp[i]['time'])
            elif tmp[i]['time'] > destTimeStamp:
                break
        if len(tmpTime)==0 or len(tmpValue)==0:
            return 'no data' 
        x = np.asarray(tmpTime)
        y = np.asarray(tmpValue)
        slope,yIntercept,correlationValue,pValue,stdError = stats.linregress(x,y)        
        predictValue = slope*(timeStamp+predictTime*60*60) + yIntercept
        #print y
        if math.isnan(predictValue):
            return 'no data'
        return predictValue
    def averagePrice(self,measurement='btcusd',field='price',timeStamp=0,timeDelta=0.05,predictTime=0.1):
        timeStamp = timeStamp + predictTime*60*60
        tmp = []
        for i in range(0,len(self.item[measurement][field])):
            if self.item[measurement][field][i]['time']>timeStamp-timeDelta*60*60/2\
            and self.item[measurement][field][i]['time']<timeStamp+timeDelta*60*60/2:     
                tmp.append( self.item[measurement][field][i][field] )
            elif self.item[measurement][field][i]['time']>timeStamp+timeDelta*60*60/2:
                break 
        if len(tmp)==0:
            return 'no data'
        return float(sum(tmp))/len(tmp)
    def formX(self,measurement='btcusd',timeStamp=0):
        if timeStamp==0:
            timeStamp = time.time()-28800
        tmp = []
        tmp2 = []
        tmp.append(self.linearRegression(measurement,'price',timeStamp,24.0))
        tmp.append(self.linearRegression(measurement,'price',timeStamp,12))
        tmp.append(self.linearRegression(measurement,'price',timeStamp,6))
        tmp.append(self.linearRegression(measurement,'price',timeStamp,3))
        tmp.append(self.linearRegression(measurement,'price',timeStamp,1))
        tmp.append(self.linearRegression(measurement,'price',timeStamp,0.5))   
        tmp.append(self.linearRegression(measurement,'price',timeStamp,0.16))
        tmp.append(self.linearRegression(measurement,'price',timeStamp,0.08))
        tmp.append(self.linearRegression(measurement,'sellAmount',timeStamp,0.1))
        tmp.append(self.linearRegression(measurement,'sellAmount',timeStamp,0.05))
        tmp.append(self.linearRegression(measurement,'sellAmount',timeStamp,0.02))
        tmp.append(self.linearRegression(measurement,'buyAmount',timeStamp,0.1))
        tmp.append(self.linearRegression(measurement,'buyAmount',timeStamp,0.05))
        tmp.append(self.linearRegression(measurement,'buyAmount',timeStamp,0.02))
        tmp.append(self.linearRegression(measurement,'volume',timeStamp,12))
        tmp2.append(tmp)
        if tmp.count('no data')!= 0 and len(tmp)==0:
            print 'something wrong bro!'
            return 0
        return np.asarray(tmp2)
    def formInputAndOutput(self,threadNumber=0,measurement='btcusd',allTimeStamp = []):
        recent_dir = os.path.dirname(__file__)
        #fi = open(os.path.join(recent_dir,'{}{}{}{}{}'.format('/',measurement,'/input',threadNumber,'.txt')),'a')
        #fo = open(os.path.join(recent_dir,'{}{}{}{}{}'.format('/',measurement,'/output',threadNumber,'.txt')),'a')
        fi = open('{0}{1}{2}{3}'.format(measurement,'_input',threadNumber,'.txt'),'a')
        fo = open('{0}{1}{2}{3}'.format(measurement,'_output',threadNumber,'.txt'),'a') 
        #print self.item[measurement]['price'] 
        for timeStamp in allTimeStamp:
            tmp = []
            tmp2 = []
            tmp.append(self.linearRegression(measurement,'price',timeStamp,24.0))
            tmp.append(self.linearRegression(measurement,'price',timeStamp,12))
            tmp.append(self.linearRegression(measurement,'price',timeStamp,6))
            tmp.append(self.linearRegression(measurement,'price',timeStamp,3))
            tmp.append(self.linearRegression(measurement,'price',timeStamp,1))
            tmp.append(self.linearRegression(measurement,'price',timeStamp,0.5))   
            tmp.append(self.linearRegression(measurement,'price',timeStamp,0.16))
            tmp.append(self.linearRegression(measurement,'price',timeStamp,0.08))
            tmp.append(self.linearRegression(measurement,'sellAmount',timeStamp,0.1))
            tmp.append(self.linearRegression(measurement,'sellAmount',timeStamp,0.05))
            tmp.append(self.linearRegression(measurement,'sellAmount',timeStamp,0.02))
            tmp.append(self.linearRegression(measurement,'buyAmount',timeStamp,0.1))
            tmp.append(self.linearRegression(measurement,'buyAmount',timeStamp,0.05))
            tmp.append(self.linearRegression(measurement,'buyAmount',timeStamp,0.02))
            tmp.append(self.linearRegression(measurement,'volume',timeStamp,12))
            tmp2.append(self.averagePrice(measurement,'price',timeStamp))
            if tmp.count('no data')+tmp2.count('no data') == 0 and len(tmp)!=0 and len(tmp2)!=0:
                #self.input[measurement].append(tmp)
                #self.output[measurement].append(tmp2)
                #if random.randint(1,1000)<2000:
                #print tmp,tmp2 
                fi.write(str(tmp))
                fi.write(str('\n'))
                fo.write(str(tmp2))
                fo.write(str('\n'))
            if random.randint(1,1000)<200:
                os.system('clear')
                #print 'formInputAndOutput regressioning ',float(allTimeStamp.index(timeStamp)*100.0/len(allTimeStamp)),'% completed'
                self.threadComplete[threadNumber] = float(100.0*allTimeStamp.index(timeStamp))/len(allTimeStamp)
                #print 'form data',self.completePercent,'% complete' 
        fi.close()
        fo.close()
    def writeData(self,measurement='btcusd'):
        self.completePercent = 0.000
        self.threadComplete = []
        allTimeStamp = []
        maxThread = 3
        for item in self.item[measurement]['price']:
            allTimeStamp.append(item['time'])
        for i in range(0,maxThread):
            self.threadComplete.append(0.0)
            thread.start_new_thread(self.formInputAndOutput,\
                    (i,measurement,allTimeStamp[i*len(allTimeStamp)/maxThread:(i+1)*len(allTimeStamp)/maxThread]))
        while True:
            time.sleep(3)
            os.system('clear')
            for i in range(0,maxThread):
                #total = total + self.threadComplete[i] 
                print i,'complete ',self.threadComplete[i],'%'
            #print 'total ',total/len(allTimeStamp) 
            #print 'form data ',self.completePercent,'%complete'
symbols = ['ethusd','btcusd','zecusd'] 
if __name__=='__main__':
    pricePredict = PricePredict()
    pricePredict.getFromInfluxdb()
    #print pricePredict.item['ethusd']['price']
    #print pricePredict.linearRegression('ethusd','price',1511653642.0)
    #pricePredict.formInputAndOutput(0,'ethusd')
    pricePredict.writeData('ethusd')
