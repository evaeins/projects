#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 12 20:31:05 2022

@author: guangyudu
"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 12 20:28:33 2022

@author: guangyudu
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#@author: guangyudu
#import modules for use
import sqlite3
import time 
import datetime
import requests
from matplotlib import pyplot as plt
import numpy as np
from sqlalchemy import create_engine
import sqlalchemy as sa
from datetime import timedelta

#build database and create table to store data
class Crawl():
    def __init__(self):
        self.list = ['AUD/USD','CNY/USD','EUR/USD','AUD/EUR','AUD/CNY','EUR/CNY','AUD/CAD','CAD/USD','CAD/CNY','NZD/USD']
        #create database
        self.engine = create_engine(r'sqlite://///Users/guangyudu/Desktop/dgy/gre/FXRATE5-2.db') 
        #connect to the database
        self.connection = self.engine.connect() 
        self.metadata = sa.MetaData(bind=self.engine)
        self.currency = ['AUDUSD','CNYUSD','EURUSD','AUDEUR','AUDCNY','EURCNY','AUDCAD','CADUSD','CADCNY','NZDUSD']
        for i in range(0,10):
            self.currency[i] = sa.Table(self.currency[i], self.metadata,
                     sa.Column('TIMESTAMP', sa.Integer()),
                     sa.Column('FXRATE', sa.Float()),
                     sa.Column('TIMESTAMPOFENRTY', sa.String())
                     ) 
            #Creates the tables
        self.metadata.create_all(self.engine) #Creates the table
#Data Extraction
    def func(self):
        try:
            for i in self.list:
                #get time for entry
                now = datetime.datetime.now().strftime("%D %H:%M:%S")
                response = requests.get('https://api.polygon.io/v1/conversion/{}?amount=1&precision=4&apiKey=beBybSi8daPgsTp5yx5cHtHpYcrjp5Jq'.format(i,))
                #transform the text into dictionary
                dict=eval(response.text)['last']
                #get the fx rate
                rate=dict['converted'] 
                #get the timestamp from dictionary
                ts = dict['timestamp'] 
                #inset data into tables
                query = sa.insert(self.currency[self.list.index(i)]).values(TIMESTAMP=ts, FXRATE=rate, TIMESTAMPOFENRTY=now)
                self.connection.execute(query)
        except:    
            self.func()

#get real time data            
    def run(self):
        tomorrow = (datetime.datetime.now() + timedelta(days= 1)).strftime("%D %H:%M")
        while True:
            self.func()
            time.sleep(1) #set the time interval for calling funtions
            current_time=datetime.datetime.now().strftime("%D %H:%M")
            end_time = tomorrow #set the time for ending
            print ('current time is ',current_time)
            print('the end time is ',tomorrow)
            print('///')
            if  current_time ==end_time:
                break
 #data calculation for later use
def bucketCalAverStdDev(dataTime,priceData,interval=360):
	"""
	Return average and stdDev of every bucket
	"""
	size=len(dataTime)
	indexs=[]
	
	#--------------------------
	#step 1: get every 6min index
	
	#get 6 min head index
	headI=0
	tempList=[]
	for i in range(size):
		if dataTime[i]-dataTime[headI] <= interval:
			tempList.append(i)
			#print(tempList)
			
		else:
			indexs.append(tempList.copy())
			headI=i
			tempList=[]
			tempList.append(i)
	indexs.append(tempList.copy())
	tempList.append(headI)
	
	#--------------------------
	#step 2: fill every bucket price
	priceBucket=[]
	for bucketI in indexs:
		tempList=[]
		for i in bucketI:
			tempList.append(priceData[i])
		priceBucket.append(tempList.copy())
	
	#---------------------------
	#step 3: calculate every bucket average price
	priceBucketAver=[]
	priceBucketStdDev=[]
	for priceI in priceBucket:
		#average
		mean_=round(sum(priceI)/len(priceI),3)
		priceBucketAver.append(mean_)
		
		#stdDev
		stdDev_=0
		for price in priceI:
			stdDev_+=(price-mean_)**2
		stdDev_=round((stdDev_/len(priceI))**0.5,7)
		priceBucketStdDev.append(stdDev_)
		
	#---------------------------
	#step 3: cal moving average price with 5 point
	priceMovingAver=[]
	priceMovingAverStd=[]
	size_=len(priceBucketAver)
	for i in range(size_):
		try:
			priceBucketAver[i+5]
			movingAver=calAverageMy(priceBucketAver[i:i+5])
			movingStd=calStdDevMy(priceBucketAver[i:i+5])
		except:
			movingAver=calAverageMy(priceBucketAver[i:size_])
			movingStd=calStdDevMy(priceBucketAver[i:size_])
	
		priceMovingAver.append(movingAver)
		priceMovingAverStd.append(movingStd)
	

	return priceBucketAver, priceBucketStdDev, priceMovingAver, priceMovingAverStd

def toSeconds(strDate):
	"""
	Turn date into seconds
	"""
	d=datetime.datetime.strptime(strDate,'%d/%m/%y %H:%M:%S')
	seconds = time.mktime(d.timetuple())
	return seconds

def calAverageLib(data):
	"""
	return average from library numpy
	"""
	a=np.array(data)
	return a.mean()
	
def calStdDevLib(data):
	"""
	return average from library numpy
	"""
	a=np.array(data)
	return a.std()
	
def calAverageMy(data):
	"""
	return average
	"""
	size=len(data)
	
	return sum(data)/size

def calStdDevMy(data):
	"""
	return STANDARD DEVIATION
	"""
	aver=calAverageMy(data)
	size=len(data)
	stdDev=0
	for d in data:
		stdDev += pow(d-aver,2)
		
	return (stdDev/size)**0.5

def calBand(average,std,fold=1.75):
	"""
	Calculation of Bollinger Bands and return it
	"""
	bolu=[]
	bold=[]
	m=len(average)
	for i in range(len(average)):
		u = average[i]+std[i]*fold
		d = average[i]-std[i]*fold
		bolu.append(u)
		bold.append(d)
	
	return bolu,bold
	
def calMovingAveragePrice(price):
	"""
	
	"""
	pass
#get return
class  hisPrice:
	def __init__(self,type_):
		self.price=[]
		self.returnPrice=[]
		self.type=type_
		
	
	def toReturn(self):
		"""
		Get return
		"""
		income=[0]
		size=len(self.price)
		for i in range(0,size-1):
			nextPrice=self.price[i+1]
			currPrice=self.price[i]
			return_=(nextPrice-currPrice)/currPrice
			income.append(return_)
	
		return income
		
		
	def addRecord(self,r):
		"""
		Add recode to list
		"""
		self.price.append(r)
		
	def showHistogram(self,income):
		"""
		Display histogram of return
		"""
		plt.figure(figsize=(12,5))
		plt.bar(x=range(len(income)),height=income)
		plt.show()
#build class to store 10 currencypairs
class currencyPair:
	def __init__(self,type_):
		self.type=type_
		self.price= hisPrice(type_)
		self.seconds=[]
		self.date=[]
		
		#connect database
		self.cx = sqlite3.connect("FXRATE5-2.db")
		self.cu=self.cx.cursor()
		
		#addData
		self.extractData()
		
		#get return
		self.income=self.price.toReturn()
		#self.price.showHistogram(a)
		#print(a)
		
	def addData(self,date,price):
		"""
		Add date and price
		"""
		self.date.append(date)
		self.price.addRecord(price)
		self.seconds.append(toSeconds(date))
		
	def extractData(self):
		"""
		Get data from data base
		"""
		for data in self.cu.execute("select * from %s"%self.type):
			timeStamp = data[0]
			price = data[0]
			price = data[1]
			date = data[2]
			self.addData(date,price)

currencysType=[
	'AUDUSD',
	'CNYUSD',
	'EURUSD',
	'AUDEUR',
	'AUDCNY',
	'EURCNY',
	'AUDCAD',
	'CADUSD',
	'CADCNY',
	'NZDUSD',
	]
currencysReturn=[]
currencysPrice=[]

#bucket of 6 minutes
bucO6=[]

print("%-8s\t%-8s\t%-8s\t%-8s\t%-8s"%("Curr","MyAver","LibAver","MyStd","LibStd"))
print("-"*80)
for cType in currencysType:
	# create a currencyPair object
	pair = currencyPair(cType)
	
	#save every currencyPair return 
	currencysReturn.append(pair.income)
	
	
	#get type
	type=pair.type
	
	#get  price
	hisprice=pair.price.price
	currencysPrice.append(hisprice)
	
	#get return
	hisReturn=pair.price.toReturn()
	
	
	#get average return from My
	myAverReturn = calAverageMy(hisReturn)
	
	#get average return from library
	libAverReturn = calAverageLib(hisReturn)
	
	#get stdDev return from My
	myStdDevReturn = calStdDevMy(hisReturn)
	
	#get stdDev return from library
	libStdDevReturn = calStdDevLib(hisReturn)
	
	#show information
	print("%-8s\t%-8.7f\t%-8.7f\t%-8.7f\t%-8.7f"%(type,myAverReturn,libAverReturn,myStdDevReturn,libStdDevReturn))
	
print("="*80)
print("Curr:    the type of currencys pair")
print("MyAver:  the average of return from my")
print("LibAver: the average of return from library")
print("MyStd:   the stdDev of return from my")
print("MyStd:   the stdDev of return from library")


#show 6 min bucket information about average and stdDev
print()
print()
print("*"*80)
print("* show 6 min bucket information about average and stdDev *")
currencysBOLU = []
currencysBOLD = []
currencysBucketPrice = []
currencysBucketMoving = []
for cType in currencysType:
	# create a currencyPair object
	pair = currencyPair(cType)
	
	#get type
	type=pair.type
	
	#get price
	hisprice=pair.price.price
	
	#get return
	hisReturn=pair.price.toReturn()
	
	#Split the data into six minutes, and calculate average and stdDev in each bucket
	seconds=pair.seconds
	
	bucketAver, bucketStdDev, bucketMovingAver, bucketMovingStd= bucketCalAverStdDev(seconds,hisprice)
	bucketAver3, bucketStdDev3,_,_ = bucketCalAverStdDev(seconds,hisReturn)#return every 6min
	bucketAver2, bucketStdDev2,_,_ = bucketCalAverStdDev(seconds,hisprice,3600)
	BOLU, BOLD = calBand(bucketMovingAver,bucketMovingStd,1.25)
	currencysBOLU.append(BOLU)
	currencysBOLD.append(BOLD)
	currencysBucketPrice.append(bucketAver)
	currencysBucketMoving.append(bucketMovingAver)
	
	#show 6 min bucket information
	print()
	print("="*40,end="")
	print("* %s *"%type,end="")
	print("="*40)
	
	print("%-12s\t%-12s\t%-12s\t%-12s\t%-12s\t%-12s\t%-12s\t%-12s\t%-12s\t%-12s"%("bucketID","bucketAverP","bucketStdDevP","bucketAverR","bucketStdDevR","MovingAverP","BOLU","BOLD","Type","profit"))
	print("-"*160)
	maxStdDev=0
	minStdDev=99999
	myChoose = "Nothing"
	preType = "Nothing"
	myReturn = 1
	prePrice = 0
	currPrice = 0
	myMoney = 1
	#count how many postive or negative returns before crossing the bollinger band	
	def count_return(currencysBucketPrice,hisReturn,currencysBOLU,currencysBOLD):
		num_positive=[]
		num_negative=[]
		for i in range(0,len(currencysBOLU)):
			count=0
			if currencysBucketPrice[i]<=currencysBOLD[i] :
				while i>=0:
					if hisReturn[i]<0:
						count+=1
						i-=1
					if hisReturn[i]>=0:
						num_negative.append(count)
						count=0
						break
			if currencysBucketPrice[i]>=currencysBOLU[i]:
				while i>=0:
					if hisReturn[i-1]>0:
						count+=1
						i-=1
					if hisReturn[i-1]<=0:
						num_positive.append(count)
						count=0 
						break
		return num_positive,num_negative
	'''strategy and analysis'''
	for i in range(len(bucketAver)):
		currPrice = bucketAver[i]
		if i >= 2:
			#base on price
            #if bucketAver[i]>BOLU[i] and bucketAver[i-1]<BOLU[i-1]
            #based on predict next price is up or down
			#if BOLU[i] > BOLU[i-1] and BOLU[i] > BOLU[i-2]:
			#base on return
			if hisReturn[i]>0 and  hisReturn[i-1]>0 and hisReturn[i-2]>0  :
				preType = "SELL"
			elif hisReturn[i]<0 :
				preType = "BUY"
			else:
				preType = "Nothing"
				
			#my action base on predict
			if preType == "BUY" and myChoose == "Nothing":
				myChoose = "BUY"
				myReturn = 0
				prePrice = bucketAver[i]
				
			elif myChoose == "BUY":
				myChoose = "SELL"
				
				#cal my profit
				myMoney = myMoney * (1+(currPrice - prePrice)/prePrice)
				
		print("%-12s\t%-12.3f\t%-12.7f\t%-12.7f\t%-12.7f\t%-12.3f\t%-12.7f\t%-12.7f\t%-12s\t%-12.7f"%("bucket "+str(i),bucketAver[i],bucketStdDev[i],bucketAver3[i],bucketStdDev3[i],bucketMovingAver[i],BOLU[i],BOLD[i],myChoose,myMoney))
		if bucketStdDev[i]>maxStdDev:
			maxStdDev = bucketStdDev[i]
		if bucketStdDev[i]<minStdDev:
			minStdDev = bucketStdDev[i]
			
		if i >= 2:
			if myChoose == "SELL":
				myChoose = "Nothing"
		
	#show min & max in one hour
	print("-"*20)
	print("Max stdDev = %.7f in hour"%maxStdDev)
	print("Min stdDev = %.7f in hour"%minStdDev)
	

#show histogram
plt.figure(figsize=(25,20))
for i in range(len(currencysType)):
	plt.subplot(5,2,i+1)
	income = currencysReturn[i]
	price_ = currencysBucketPrice[i]
	bolu_ = currencysBOLU[i]
	bold_ = currencysBOLD[i]
	moving = currencysBucketMoving[i]
	
	#-----------------------------
	#show band
	plt.plot(range(len(bolu_)),bolu_,color="orange",label="upper band")
	plt.plot(range(len(price_)),price_,color="blue",label="bucket price")
	plt.plot(range(len(moving)),moving,color="blue",linestyle=":",label="moving price")
	plt.plot(range(len(bold_)),bold_,color="red",label="lower band")
	plt.xlim(-2,len(price_)+5)
	plt.legend(loc="lower right")
	#plt.bar(range(len(income)),income)
	plt.ylabel("%s"%currencysType[i])
plt.show()
	


	
	
	
	
