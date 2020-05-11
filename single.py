from psaw import PushshiftAPI
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
import lxml
import lxml.html
import requests
import json

stock = input("Choose stock symbol:\n ")

sent = vol = price = volchange = trend = perc = "--"
print("Code\tFrequency\tWatchers\tPrice\tSentiment\tTrendScore\tVolume\tVol%\tPrice%")
r = requests.get(url='https://api.stocktwits.com/api/2/streams/symbol/'+stock+'.json')
json_data = json.loads(r.text)
try:
	watchers = json_data['symbol']['watchlist_count']
except KeyError:
	watchers="--"
	
html = requests.get('https://stocktwits.com/symbol/'+stock+'')
doc = lxml.html.fromstring(html.content)
stx = requests.get(url='https://stocktwits.com/symbol/'+stock+'')	
page_source = stx.content	

soup = BeautifulSoup(page_source, "html.parser")
all_scripts = soup.find_all('script')
script=str(all_scripts[7])

jsData = re.search(r'"sentimentChange":(.*),"volum', script)
trend = re.search(r'"trendingScore":(.*),"sent', script)

volume =re.search(r'"volume":(.*),"lastSiz', script)
volchange =re.search(r'"volumeChange":(.*),"price":', script)
perc =re.search(r'"percent":(.*),"lastUpdated":"', script)

try:
	sent=jsData.group(1)
except AttributeError:
	sent:"--"
try:
	trend = round(float(trend.group(1)),3)
except AttributeError:
	trend:"--"
try:
	vol=volume.group(1)
except AttributeError:
	vol:"--"
try:
	volchange=volchange.group(1)
except AttributeError:
	volchange:"--"
try:
	perc=perc.group(1)
except AttributeError:
	perc:"--"
	
	
try:
	price = doc.xpath('//*[@id="app"]/div/div/div[3]/div[2]/div/div[1]/div[1]/div/div[1]/div/div/div[1]/div[2]/span[1]/text()')[2]     
except IndexError:
	price="--"  


	 
padding = ""


if len(stock) < 4:
    padding = ' '

print(str(stock) + padding + "\t" + str(stock) + padding + "\t \t" + str(watchers)+ padding + "\t \t" + str(price) + "\t" + str(sent)+ "\t\t"  + str(trend)+ "\t\t"  + str(vol) + "\t" + str(volchange) + "\t" + str(perc))
