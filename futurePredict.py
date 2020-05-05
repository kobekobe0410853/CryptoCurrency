import datetime
from pricePredict import *
from keras.models import load_model
model = load_model('./model.h5')
#pricePredict = PricePredict()
while True:
    time.sleep(1)
    model = load_model('./model.h5')
    pricePredict = PricePredict()
    pricePredict.getFromInfluxdb(1)
    x = pricePredict.formX('ethusd')    
    print model.predict(x,batch_size=32,verbose=0),datetime.datetime.fromtimestamp(time.time()+0.1*60*60).strftime('%Y-%m-%d %H:%M:%S')
