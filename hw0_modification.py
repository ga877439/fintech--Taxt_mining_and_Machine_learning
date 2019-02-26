import aiohttp	#用來加速爬蟲
import asyncio
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup as bs
import pickle	
import time

#dates
start_date = "2018-07-01"
stop_date = "2018-12-31"
start = datetime.strptime(start_date, "%Y-%m-%d")	# datetime.strptime(date_string, format) return a datetime object
stop = datetime.strptime(stop_date, "%Y-%m-%d")
dates = list()
while start <= stop:	#迴圈~ start time 每加一天都一天都check是否有超過stop_date
	dates.append(start.strftime('%Y%m%d'))	#object.strftime(format) return a string representing the date of the object in the specific format.
	start = start + timedelta(days=1)	#timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0) is a time shift.
# return dates


def get_urls(document):
#將一個頁面所有鏈接的url存成list並返回
	url_links = []
	list_title = []
	nodes = document.select('ul.list > li')
	for li in nodes:

		# check if is empty element
		if li.select_one('a') == None:
			continue
		#	get link
		li_link = 'http://news.ltn.com.tw/' + li.select_one('a')['href']	
		url_links.append(li_link)
		#	get title
		li_title = li.select_one('p').get_text()	#nodes 裡面的 li 內的p標籤 包含title 所以可直接用select_one 提取出text內容
		list_title.append(li_title)
	return url_links, list_title	#先return好鏈結的url以及title


async def getPage(url,data,date, li_title):
#異步抓取url 
	print(url)
	async with aiohttp.ClientSession() as session:	
		async with session.get(url) as response:

			assert response.status==200	#確保網頁有連接
			text = await response.text()	#在等待的時候可以先去get 其他url 的response
			li_doc = bs(text, 'lxml')	#此為新網站對應的bs 物件

			#get date
			li_date = datetime.strptime(date, "%Y%m%d").strftime('%Y-%m-%d')	#date是此函數的輸入值之一，li_date可回傳出格式為('%Y-%m-%d')的字串

		# get link
			li_link = str(url)
		#	get content
			li_content = ""
			for ele in li_doc.select('div.text > p'):	#本文內容位於 <div class="text"> 的<p>之下
				if not 'appE1121' in ele.get('class', []):	#由於<div class="text"> 的<p>之下 有3個 子標籤 <p class="appE1121">是不需要的信息，我們不考慮納入
					li_content += ele.get_text()

		#	append new row
			data.append({	#data 是一個list，此裡面會append 每天 每個政治新聞的 信息(以dictionary存取)
				'date' : li_date,
				'title': li_title,
				'link' : li_link,
				'content' : li_content,
				'tags' : []
			})
		
all_data = []

t1 = time.time()	#紀錄爬取所花費的時間
for date in dates:	
	tem_list = []
	print('start crawling :', date)
	res = requests.get('https://news.ltn.com.tw/list/newspaper/politics/' + date)	
	doc = bs(res.text, 'lxml')
	url_list, title = get_urls(doc)	#取得某一天政治業面的所有urls
	data = []
	loop = asyncio.get_event_loop()			
				
	tasks = [getPage(url_list[i],data,date,title[i]) for i in range(len(url_list))]			
	loop.run_until_complete(asyncio.wait(tasks))
	
	all_data += data	
print('Total time consumed is %s seconds' %( time.time()-t1 )	)	#Total time consumed is 222.6810507774353 seconds
# print(all_data)



import pickle	

with open(r'C:\Users\User\Documents\GitHub\fintech--Taxt_mining_and_Machine_learning\data\liberty_times.pkl', 'wb') as f:		#使用二進位寫入模式來保存資料
	pickle.dump(all_data, f)	#把資料 丟入(dump)進 filehander(f) 裡		

import pandas as pd

df = pd.DataFrame(all_data)[['date', 'title', 'link', 'content', 'tags']]	
print(df.head(n=10))

