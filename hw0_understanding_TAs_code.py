from datetime import datetime, timedelta

start_date = "2018-07-01"
stop_date = "2018-12-31"
	
start = datetime.strptime(start_date, "%Y-%m-%d")	# datetime.strptime(date_string, format) return a datetime object
stop = datetime.strptime(stop_date, "%Y-%m-%d")

dates = list()
while start <= stop:	#迴圈~ start time 每加一天都check是否有超過stop_date
	dates.append(start.strftime('%Y%m%d'))	#object.strftime(format) return a string representing the date of the object in the specific format.
	start = start + timedelta(days=1)	#timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0) is a time shift.
	
import requests
from bs4 import BeautifulSoup as bs

def process_document(document, date):	#document 是 request庫抓取text 之後的 BeautifulSoup(r.text, 'lxml')	返回值
	

	nodes = document.select('ul.list > li')	
	#select 是 bs 的 css選擇器	
	#由於新聞鏈接的url 藏在原始碼中<ul class="list">標簽裡面的	<li>
	#格式類似於 	<li> <a href="news/politics/paper/1257940" .... </li>
	#所以我們先把ul.list標籤裡面所有 li子標籤都找出來
	
	# print(nodes[0])	
	# <li>
	# <a class="ph" data-desc="P:8:一週大事（6月24日至30日）" href="news/politics/paper/1213078">
	# <img src="https://img.ltn.com.tw/2018/new/jul/1/images/272.jpg"/>
	# </a>
	# <a class="tit" data-desc="T:8:一週大事（6月24日至30日）" href="news/politics/paper/1213078">
	# <p>一週大事（6月24日至30日）</p>
	# </a><div class="tagarea"><span class="newspapertag">政治新聞</span></div>
	# </li>
	
	
	data = list()

	for li in nodes:	#nodes 裡面是一群<li>標籤	我們想知道是否有 <a> tag 並且找出 key(href) 對應的 value('url')
		
	#	check if is empty element
		if li.select_one('a') == None:	#Select_one 找到第一個有'a'tag 如果不存在該標籤 代表沒有 href 所以我們跳過後續步驟
			continue

	#	get link
	#	以key:hreft 來對應出value，由於對應網站url格式為https://news.ltn.com.tw/news/politics/paper/1257949 所以把url 加上一個字串
		li_link = 'http://news.ltn.com.tw/' + li.select_one('a')['href']	
		
		# request for document
		li_res = requests.get(li_link)
		li_doc = bs(li_res.text, 'lxml')	#此為新網站對應的bs 物件

		#get date
		li_date = datetime.strptime(date, "%Y%m%d").strftime('%Y-%m-%d')	#date是此函數的輸入值之一，li_date可回傳出格式為('%Y-%m-%d')的字串

	#	get title
		li_title = li.select_one('p').get_text()	#nodes 裡面的 li 內的p標籤 包含title 所以可直接用select_one 提取出text內容

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
	return data
	

all_data = list()
import time
t1 = time.time()	#紀錄爬取所花費的時間
for date in dates:	#dates 是一個list，每個element是 datetime object 範圍從start到stop
	print('start crawling :', date)
	res = requests.get('https://news.ltn.com.tw/list/newspaper/politics/' + date)	#爬取每日政治新聞，鏈接規則類似 'https://news.ltn.com.tw/list/newspaper/politics/20181230'
	doc = bs(res.text, 'lxml')
	data = process_document(doc, date)	#把bs4 及時間放入該函數後，可以回傳一個list，list中每個element是字典
	all_data += data	#list 可以相加
print('Total time consumed in normal way is %s seconds' %( time.time()-t1 )	)	#Total time consumed in normal way is 780.1049983501434 seconds
print(len(all_data))	#1660

	
#將檔案存成pickle檔案；
# with open(r'C:\Users\User\Documents\GitHub\fintech--Taxt_mining_and_Machine_learning\data\liberty_times.pkl', 'wb') as f:		#使用二進位寫入模式來保存資料
	# pickle.dump(all_data, f)	#把資料 丟入(dump)進 filehander(f) 裡		

import pandas as pd

df = pd.DataFrame(all_data)[['date', 'title', 'link', 'content', 'tags']]	
print(df.head())	#DataFrame.head(n=5) return the first n rows






