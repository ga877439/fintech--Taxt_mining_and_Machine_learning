import aiohttp	#用來加速爬蟲
import asyncio
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup as bs
import pickle	
import time	#用來記錄所花時間
import multiprocessing as mp	#用來多進程
import pandas as pd

#dates
start_date = "2018-07-01"
stop_date = "2018-07-31"
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

	return url_links	#先return好首頁之下各個鏈結的url


def parse(html,date):
	li_doc = bs(html, 'lxml')	#此為新網站對應的bs 物件
	
	#get title
	li_title = li_doc.select_one('title').get_text()[0:-15]

	#get date
	li_date = datetime.strptime(date, "%Y%m%d").strftime('%Y-%m-%d')	#date是此函數的輸入值之一，li_date可回傳出格式為('%Y-%m-%d')的字串
	
#	get content
	li_content = ""
	for ele in li_doc.select('div.text > p'):	#本文內容位於 <div class="text"> 的<p>之下
		if not 'appE1121' in ele.get('class', []):	#由於<div class="text"> 的<p>之下 有3個 子標籤 <p class="appE1121">是不需要的信息，我們不考慮納入
			li_content += ele.get_text()
	#get link

	pattern = li_doc.find('div',attrs ={"class":"fb-comments"}) 	#找到link的所在位置
	li_link = pattern['data-href']

#	append new row
	a_dict = {	#data 是一個list，此裡面會append 每天 每個政治新聞的 信息(以dictionary存取)
				'date' : li_date,
				'title': li_title,
				'link' : li_link,
				'content' : li_content,
				'tags' : []
			}
	return  a_dict	#返回dictionary 作為 pool.get()方法的抓取值


async def crawl(url, session):
	r = await session.get(url)
	html = await r.text()
	return html


async def main(loop,all_data):
	pool = mp.Pool(4)   	#使用4個核心來多進程處理
	for date in dates:	
		print('start crawling :', date)
		#爬取首頁

		res = requests.get('https://news.ltn.com.tw/list/newspaper/politics/' + date)	
		doc = bs(res.text, 'lxml')
		url_list = get_urls(doc)	#取得某一天政治業面的所有urls
		
		#異步抓取每個分頁
				
		async with aiohttp.ClientSession() as session:

			tasks = [loop.create_task(crawl(url, session)) for url in url_list]	#把所有url_list 分成多個待處理的網址，在等待response的時候會去爬取其他網址
			finished, unfinished = await asyncio.wait(tasks)
			htmls = [f.result() for f in finished]	#done, pending = await asyncio.wait({task})

			# 多進程輸出dictionary

			parse_tasks = [pool.apply_async(parse, args=( html ,date)) for html in htmls]		#使用4個核心來解析網頁，並把返回值提取出來
			data1 = [j.get() for j in parse_tasks]
			
			# 存取資料
			all_data += data1


if __name__ == "__main__":
	all_data = []
	t1 = time.time()
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main(loop,all_data))
	loop.close()
	print('Total time consumed in way of aiohttp and multiprocessing is %s seconds' %( time.time()-t1 )	)	#Total time consumed in way of aiohttp and multiprocessing is 121.83902072906494 seconds
	print(len(all_data))	#1660
	#pandas
	df = pd.DataFrame(all_data)[['date', 'title', 'link', 'content', 'tags']]	
	print(df.head(n=30))
