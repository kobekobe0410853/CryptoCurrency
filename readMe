self.item = {'btcusd':{'price':[ {u'price':322.3,u'time':1508045240.0},{},{}  ],'volume':[ {},{} ],......}
Functions:
	getFromInfluxdb():
		complete self.item
	datetimeToTimestamp(T):
		arguments:
			T:'%Y-%m-%dT%H:%M:%SZ'
		return:
			timeStamp
	linearRegression(measurement='btcusd',field='price',timestamp,deltaTime=2.0,predictTime=0.1):
		arguments:
			measurement:	btcusd,ethusd,zecusd
			field:  price;volume;sellAmount;buyAmount (in String)
			timestamp:	the time (in TimeStamp)
			deltaTime:	past time delta to regression (in Hours)
			predictTime:	to predict time delta (in Hours)
		action:
			regressed between [timestamp-deltaTime*60*60:timestamp]
			predict [timestamp+predictTime*60*60]
		tmp[]:  
			input the data (in dictionary list [{},{},{}] )
		stats.linregress(x,y):	//from scipy import stats
			slope : float
			intercept : float intercept with Y
			r-value : float correlation coefficient
			p-value : float two-sided p-value for a hypothesis test whose null hypothesis is that the slope is zero.
			stderr : float Standard error of the estimate
		return:
			value of predictTimestamp (float)
	averagePrice(measurement='ethusd',field='price',timeStamp=0,timeDelta=0.05,predictTime=0.1):
		arguments:
			measurement:    btcusd,ethusd,zecusd
            field:  price;volume;sellAmount;buyAmount (in String)
            timestamp:  the time (in TimeStamp)
			timeDelta: 0.05 (in Hours)
			predictTime: 0.1 (in Hours)
		action:
			average price between [timeStamp+(predictTime-timeDelta/2)*60*60 : timeStamp+(predictTime+timeDelta/2)*60*60]
		return:
			value of price (float)
	formInputAndOutput():
		
