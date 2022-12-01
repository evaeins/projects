#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#@author: guangyudu
#import modules for use
import sqlite3
import time 
import datetime
from matplotlib import pyplot as plt
import numpy as np

def bucketCalAverStdDev(dataTime,priceData,interval=360):
	"""
	Return average and stdDev of every bucket
	"""
	size=len(dataTime)
	indexs=[]
	
	#--------------------------
	#step 1: get every 6min index
	
	#g 6 min head index
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
	
		
	return priceBucketAver, priceBucketStdDev

#splitSixMin([1,2,3,4,5,6,8,9,15,18,19,20],[1,2,3,4,5,6,8,9,15,18,19,20])
#exit()
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


class hisPrice:
	def __init__(self,type_):
		self.price=[]
		self.returnPrice=[]
		self.type=type_
		
	
	def toReturn(self):
		"""
		Get return
		"""
		income=[]
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

class currencyPair:
	def __init__(self,type_):
		self.type=type_
		self.price=hisPrice(type_)
		self.seconds=[]
		self.date=[]
		
		#connect database
		self.cx = sqlite3.connect("FXRATE5.db")
		self.cu=self.cx.cursor()
		
		#addData
		self.extractData()
		
		#Calculate income
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

#bucket of 6 minutes
bucO6=[]

print("%-8s\t%-8s\t%-8s\t%-8s\t%-8s"%("Curr","MyAver","LibAver","MyStd","LibStd"))
print("-"*80)
for cType in currencysType:
	# create a currencyPair object
	pair = currencyPair(cType)
	
	#save every currencyPair income it means return too
	currencysReturn.append(pair.income)
	
	
	#get type
	type=pair.type
	
	#get historical price
	hisprice=pair.price.price

	#get historical return
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
for cType in currencysType:
	# create a currencyPair object
	pair = currencyPair(cType)
	
	#get type
	type=pair.type
	
	#get historical price
	hisprice=pair.price.price
	
	
	#Split the data into six minutes, and calculate average and stdDev in each bucket
	seconds=pair.seconds

	bucketAver, bucketStdDev = bucketCalAverStdDev(seconds,hisprice)
	bucketAver2, bucketStdDev2 = bucketCalAverStdDev(seconds,hisprice,3600)
	
	#show 6 min bucket information
	print()
	print("="*40,end="")
	print("* %s *"%type,end="")
	print("="*40)
	
	print("%-12s\t%-12s\t%-12s"%("bucketID","bucketAver","bucketStdDev"))
	print("-"*50)
	maxStdDev=0
	minStdDev=99999
	for i in range(len(bucketAver)):
		print("%-12s\t%-12.2f\t%-12.7f"%("bucket "+str(i),bucketAver[i],bucketStdDev[i]))
		if bucketStdDev[i]>maxStdDev:
			maxStdDev = bucketStdDev[i]
		if bucketStdDev[i]<minStdDev:
			minStdDev = bucketStdDev[i]
		
	#show min & max in one hour
	print("-"*20)
	print("Max stdDev = %.7f in hour"%maxStdDev)
	print("Min stdDev = %.7f in hour"%minStdDev)
	
	
#show histogram
plt.figure(figsize=(25,20))
for i in range(len(currencysType)):
	plt.subplot(5,2,i+1)
	income = currencysReturn[i]
	plt.bar(range(len(income)),income)
	plt.ylabel("%s"%currencysType[i])
plt.show()
	


	
	
	
	
