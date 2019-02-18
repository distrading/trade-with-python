# -*- coding:UTF-8 -*-
import requests
import json
import time
import hashlib

requests.packages.urllib3.disable_warnings()

api_key = '-'
secret_key = '-'
symbol = 'bchusdt'
amountdot = 4
treading_amount = 0.1
pg = 0.0004   #压单价差
treading_pg = 0.0001
small_amount = 0.0001
sleep_time = 0.7

def GetSign(sign_str):
	sign = hashlib.md5()
	sign.update(sign_str.encode("utf-8"))
	return sign.hexdigest()	

def GetTicker(symbol):
	payload = {'symbol':symbol}
	return requests.get('https://api.bikicoin.com/exchange-open-api/open/api/get_ticker',params=payload,verify=False).json()['data']

def GetAccount():
	timestamp = str(int(time.time()))
	sign_str = 'api_key'+api_key+'time'+timestamp+secret_key
	signed = GetSign(sign_str)
	payload = {'api_key':api_key,'time':timestamp,'sign':signed}
	return requests.get('https://api.bikicoin.com/exchange-open-api/open/api/user/account',params=payload,verify=False).json()['data']['coin_list']

def GetOrders():
	timestamp = str(int(time.time()))
	sign_str = 'api_key'+api_key+'pageSize'+'100'+'symbol'+symbol+'time'+timestamp+secret_key
	signed = GetSign(sign_str)	
	payload = {'symbol':symbol,'pageSize':100,'api_key':api_key,'time':timestamp,'sign':signed}
	return requests.get('https://api.bikicoin.com/exchange-open-api/open/api/new_order',params=payload,verify=False).json()['data']

def create_order(side,price,amount):
	timestamp = str(int(time.time()))
	price = str(price)
	amount = str(amount)
	sign_str = 'api_key'+api_key+'price'+price+'side'+side+'symbol'+symbol+'time'+timestamp+'type'+'1'+'volume'+amount+secret_key
	signed = GetSign(sign_str)	
	payload = {'side':side,'type':1,'volume':amount,'price':price,'symbol':symbol,'api_key':api_key,'time':timestamp,'sign':signed}
	return requests.post('https://api.bikicoin.com/exchange-open-api/open/api/create_order',params=payload,verify=False).json()['data']['order_id']
	
def CancelOrder(order_id):
	timestamp = str(int(time.time()))
	order_id = str(order_id)
	sign_str = 'api_key'+api_key+'order_id'+order_id+'symbol'+symbol+'time'+timestamp+secret_key
	signed = GetSign(sign_str)	
	payload = {'order_id':order_id,'symbol':symbol,'api_key':api_key,'time':timestamp,'sign':signed}
	return requests.post('https://api.bikicoin.com/exchange-open-api/open/api/cancel_order',params=payload,verify=False).json()

def Buy(price,amount):
	return create_order('BUY',price,amount)

def Sell(price,amount):
	return create_order('SELL',price,amount)
	
def CancelAll():
	orders = GetOrders()
	i = 0
	while i < orders['count']:
		print(CancelOrder(orders['resultList'][i]['id']))
		i += 1

def ssss():
	ticker = GetTicker(symbol)
	buy_price = round(float(ticker['sell']) - pg,4)
	sell_price = round(buy_price + treading_pg,4)
	buy_small_id = Buy(buy_price,small_amount)
	print('start ssss',time.ctime())
	i = 0
	while i < 15:
		time.sleep(sleep_time)
		order_id = Sell(sell_price,treading_amount)
		a = CancelOrder(order_id)
		if a['code'] == '8':
			CancelOrder(buy_small_id)
			print('ssss success')
			break
		i += 1
	CancelOrder(buy_small_id)
	print('ssss falid')

def bbbb():
	ticker = GetTicker(symbol)
	sell_price = round(float(ticker['buy']) + pg,4)
	buy_price = round(sell_price - treading_pg,4)
	sell_small_id = Sell(sell_price,small_amount)
	print('start bbbb',time.ctime())
	i = 0
	while i < 15:
		time.sleep(sleep_time)
		order_id = Buy(buy_price,treading_amount)
		a = CancelOrder(order_id)
		if a['code'] == '8':
			CancelOrder(sell_small_id)
			print('bbbb success')
			break
		i += 1
	CancelOrder(sell_small_id)
	print('bbbb falid')

def onTick():
	CancelAll()
	ticker = GetTicker(symbol)
	if (float(ticker['sell']) -float(ticker['buy']))/float(ticker['buy']) > 0.004:
		account = GetAccount()
		if float(account[6]['normal']) < treading_amount:
			bbbb()
		else:
			ssss()


if __name__ == '__main__':
	while True:
		onTick()
		time.sleep(7)
