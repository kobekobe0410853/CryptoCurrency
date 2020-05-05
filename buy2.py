# -*- coding: utf-8 -*-
import datetime
from pricePredict2 import *
from keras.models import load_model
import os 
import tensorflow as tf
from influxdb import InfluxDBClient 
def client_influxdb():
    global client_influxdb
    host = '140.113.122.202'
    port = 8086
    user = 'root'
    password = '1234567890'
    #client_influxdb = {'eth':'','btc':'','zec':''}
    dbname = 'virtualCurrencyPrice'
    client_influxdb= InfluxDBClient(host, port, user, password, dbname)
def sendToDatabase(symbol,price):
    global client_influxdb 
    try:
        timestamp = datetime.datetime.fromtimestamp(time.time()-28800).strftime('%Y-%m-%dT%H:%M:%SZ')
        json_body = [{"measurement": symbol ,\
                      "tags": {"platform": "bitfinex"},\
                      "time": timestamp ,\
                      "fields": {"predictPrice": price }}]
        #"2009-11-10T23:00:00Z"
        client_influxdb.write_points(json_body)
    except Exception as inst:
        print 'ERROR while connect and sending to database!  ',inst
client_influxdb() 
with tf.device('/cpu:0'):
    model = load_model('./model.h5')
    pricePredict = PricePredict()
os.system('cls' if os.name == 'nt' else 'clear')
oldDelta = [0,0,0,0]


wallet = {'usd':100,'eth':0}
printtime=0






while True:
    with tf.device('/cpu:0'):
        #if random.randint(0,1:00) < 5:
        #    model = load_model('./model.h5')
        timeStamp = time.time()
        pricePredict.getFromInfluxdb(1)
        x = np.asarray( pricePredict.formPredictData('ethusd',timeStamp) )
        predict = model.predict(x,batch_size=16,verbose=0)
        #print len(predict[0])
        #sendToDatabase('ethusd',float(predict[0].tolist()[0]))
        nowPrice = pricePredict.average(timeStamp-28800,1,'ethusd','price')
        oldDelta.append(predict[0][0]-nowPrice)
        oldDelta = oldDelta[1:4]
        delta1 = 0
        delta2 = 0
        tmpUp = 0
        tmpDown = 0
        delta1 = predict[0][0]-nowPrice 
        for i in range(0,len(oldDelta)-1):
            delta2 += oldDelta[len(oldDelta)-1]-oldDelta[i]
            if oldDelta[len(oldDelta)-1]-oldDelta[i]>0.8:
                tmpUp+=1
            elif oldDelta[len(oldDelta)-1]-oldDelta[i]<-0.8:
                tmpDown+=1
        
        if delta1>0:
            strDelta1 = ' ++ delta1:%.9f'%delta1
        elif delta1<0:
            strDelta1 = ' -- delta1:%.9f'%delta1 
        else:   
            strDelta1 = '    delta1:0.000'
    
        if delta2>0:
            strDelta2 = ' + delta2:%.9f'%delta2 
        elif delta2<0:
            strDelta2 = ' - delta2:%.9f'%delta2
        else :
            strDelta2 = '   delta2:0.000'
    
        timeNow =  datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S')
        
        if tmpUp>1:
            strAction = ' buy '
            string = timeNow+' %.9f'%nowPrice+' %.9f'%predict[0][0]+strDelta1+strDelta2+strAction+'\n'  
            f = open('transaction.txt','a')
            f.write(string)
            f.close()
        elif tmpDown>1:
            strAction = ' sell '
            string = timeNow+' %.9f'%nowPrice+' %.9f'%predict[0][0]+strDelta1+strDelta2+strAction+'\n'
            f = open('transaction.txt','a')
            f.write(string)
            f.close()
        else:
            strAction = ''
    
    
        #print timeNow,' %.9f'%nowPrice,' %.9f'%predict[0][0],strDelta1,strDelta2,strAction
        
        if delta1>0 and delta2>0 and wallet['usd']>0:
            buyamount = wallet['usd']/nowPrice
            wallet['usd']=0
            wallet['eth'] = wallet['eth']+buyamount* 0.9997
            print "   Buy",buyamount ,"   ETH"
        elif delta1<0 and delta2<0 and wallet['eth']>0 :
            sellamount = wallet['eth'] 
            wallet['eth']=0
            wallet['usd'] = wallet['usd']+sellamount*nowPrice* 0.9997
            print "   Sell",sellamount,"   ETH"
                
        print timeNow ,  "    USD:  " ,wallet['usd'] , "   ETH:   " , wallet['eth'] ,"   Total = ", nowPrice*wallet['eth']+wallet['usd']
        









    '''
    if delta2>0:
            print datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S'),' Now:%.9f'%nowPrice,\
                                                            '  pred:%.9f'%predict[0][0],' ++','delta2:%.9f'%delta2
    elif delta2<0:
        print datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S'),' Now:%.9f'%nowPrice,\
                                                            '  pred:%.9f'%predict[0][0],' --','delta2:%.9f'%delta2 
    else:
        print datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S'),' Now:%.9f'%nowPrice,\
                                                            '  pred:%.9f'%predict[0][0],'   ','delta2:%.9f'%delta2  
    '''



