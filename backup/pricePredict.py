import keras
import random
import time
import datetime
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
    def getFromInfluxdb(self):
        host = '140.113.122.202'
        port = 8086
        user = 'root'
        password = '1234567890'
        dbname = 'virtualCurrencyPrice'
        client = InfluxDBClient(host,port,user,password,dbname)
        for measurement in self.measurement:
            for field in self.field:
                query = 'select volume from ethusd where price>360'
                query = 'select %s from %s' % (field, measurement)
                response = client.query(query) 
                response = list(response)[0]
                for i in range(0,len(response)):
                    response[i]['time'] = self.datetimeToTimestamp(response[i]['time'])
                self.item[measurement][field] = response 
        #f = open('item.txt','w')
        #f.write(str(self.item))
        #print self.item['ethusd']['price'][0] 
        print 'load self.item done'
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
        return sum(tmp)/len(tmp)
    def formInputAndOutput(self,measurement='btcusd'):
        allTimeStamp = []
        for item in self.item[measurement]['price']:
            allTimeStamp.append( item['time'] )
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
            if tmp.count('no data')+tmp2.count('no data') == 0:
                self.input[measurement].append(tmp)
                self.output[measurement].append(tmp2)
            if random.randint(1,1000)<2:
                #print tmp,tmp2 
                f = open('data.txt','a')
                f.write(str(tmp))
                f.write(str(tmp2))
                f.write(str(' \n'))
                f.close()
            if random.randint(1,1000)<200:
                os.system('clear')
                print 'formInputAndOutput regressioning ',float(allTimeStamp.index(timeStamp)*100.0/len(allTimeStamp)),'% completed'
symbols = ['ethusd','btcusd','zecusd'] 
if __name__=='__main__':
    pricePredict = PricePredict()
    pricePredict.getFromInfluxdb()
    #print pricePredict.item['ethusd']['price']
    #print pricePredict.linearRegression('ethusd','price',1511653642.0)
    pricePredict.formInputAndOutput('ethusd')
     
