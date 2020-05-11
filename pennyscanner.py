#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" AutoDD: Automatically does the so called Due Diligence for you. """

#AutoDD - Automatically does the "due diligence" for you.
#Copyright (C) 2020  Fufu Fang

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>.

__author__ = "Fufu Fang"
__copyright__ = "The GNU General Public License v3.0"

from psaw import PushshiftAPI
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
import lxml
import lxml.html
import requests
import json

def a():
    print("pennystocks\n")
    global sub
    sub = "pennystocks"
    

def b():
    print("wallstreetbets\n")
    global sub
    sub = "wallstreetbets"

def c():
    print("stocks\n")
    global sub	
    sub="stocks"

def d():
    print("helloprofits\n")
    global sub
    sub="helloprofits"
def e():
    print("custom sub\n")
    global sub
    sub = input("Insert sub to analyze:\n ")

types = {"1":a,
         "2":b,
         "3":c,
         "4":d,
         "5":e
        }

user_input = input("Choose sub to monitor:\n 1-pennystocks \n 2-wallstreetbets \n 3-stocks \n 4-helloprofits\n 5-custom\n")

print("You chose:")

print(types[user_input]())



dayz = input("Insert number of days to analyze:\n ")
dayz = int(dayz)

def get_submission(n):
    """Returns a generator for the submission in past n days"""
    api = PushshiftAPI()
    s_date = datetime.today() - timedelta(days=n)
    s_timestamp = int(s_date.timestamp())
    gen = api.search_submissions(after=s_timestamp,
                                 subreddit=sub,
                                 filter=['title', 'selftext'])
    return gen


def get_freq_list(gen):
    """
    Return the frequency list for the past n days

    :param int gen: The generator for subreddit submission
    :returns:
        - all_tbl - frequency table for all stock mentions
        - title_tbl - frequency table for stock mentions in titles
        - selftext_tbl - frequency table for all stock metninos in selftext
    """

    # Python regex pattern for stocks codes
    pattern = "[A-Z]{3,4}"
    # Dictionary containing the summaries
    title_dict = {}
    selftext_dict = {}
    all_dict = {}

    for i in gen:
        if hasattr(i, 'title'):
            title = ' ' + i.title + ' '
            title_extracted = re.findall(pattern, title)
            
            for j in title_extracted:
           	                 
                if j in title_dict:
                    title_dict[j] += 1
                else:
                    title_dict[j] = 1

                if j in all_dict:
                    all_dict[j] += 1
                else:
                    all_dict[j] = 1

        if hasattr(i, 'selftext'):
            selftext = ' ' + i.selftext + ' '
            selftext_extracted = re.findall(pattern, selftext)
            title = ' ' + i.title + ' '
            title_extracted = re.findall(pattern, title)
            
            for j in selftext_extracted:
                if j in selftext_dict:
                    selftext_dict[j] += 1
                else:
                    selftext_dict[j] = 1

                if j in all_dict:
                    all_dict[j] += 1
                else:
                    all_dict[j] = 1

    title_tbl = sorted(title_dict.items(), key=lambda x: x[1], reverse=True)
    selftext_tbl = sorted(selftext_dict.items(), key=lambda x: x[1],
                          reverse=True)
    all_tbl = sorted(all_dict.items(), key=lambda x: x[1], reverse=True)

    return all_tbl, title_tbl, selftext_tbl


def filter_tbl(tbl, min):
    """
    Filter a frequency table

    :param list tbl: the table to be filtered
    :param int min: the number of days in the past
    :returns: the filtered table
    """
    
    BANNED_WORDS = [
        'THE', 'FUCK', 'ING', 'CEO', 'USD', 'WSB', 'FDA', 'NEWS', 'FOR', 'YOU',
        'BUY', 'HIGH', 'ADS', 'FOMO', 'THIS', 'OTC', 'ELI', 'IMO',
        'CBS', 'SEC', 'NOW', 'OVER', 'ROPE', 'MOON', "SSR", 'HOLD','TLDR', 'ETF', 'COVI', 'ORR'
    ]
    tbl = [row for row in tbl if row[1] > min]
    tbl = [row for row in tbl if row[0] not in BANNED_WORDS]
    
    
    return tbl


def print_tbl(tbl):
	sent = vol = price = volchange = trend = perc = indic = value = "--"
	
	print(f"Code\tFreq\tWatch\tPrice\tPrice%\tSent\tTrend\tVolume\t\tVol%\tValue\t\tDirection")
	for row in tbl:
		r = requests.get(url='https://api.stocktwits.com/api/2/streams/symbol/'+row[0]+'.json')
		json_data = json.loads(r.text)
		try:
			watchers = json_data['symbol']['watchlist_count']
			watchers=f"{watchers:<7}"
			watchers=f"{watchers:<7}"
		except KeyError:
			watchers="--"
			
		html = requests.get('https://stocktwits.com/symbol/'+row[0]+'')
		doc = lxml.html.fromstring(html.content)
		stx = requests.get(url='https://stocktwits.com/symbol/'+row[0]+'')	
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
			sent="--"
		try:
			trend = round(float(trend.group(1)),3)
		except AttributeError:
			trend="--"
		try:
			vol=volume.group(1)
			vol=f"{vol:<8}"
		except AttributeError:
			vol="--"
			vol=f"{vol:<8}"
		try:
			volchange=volchange.group(1)
		except AttributeError:
			volchange:"--"
		try:
			perc=perc.group(1)
		except AttributeError:
			perc="--"
			
			
		try:
			price = doc.xpath('//*[@id="app"]/div/div/div[3]/div[2]/div/div[1]/div[1]/div/div[1]/div/div/div[1]/div[2]/span[1]/text()')[2]     
		except IndexError:
			price="--"  
		
		user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
		headers = {'User-Agent': user_agent}

		yho = requests.get(url='https://finance.yahoo.com/quote/'+row[0]+'', headers=headers)
		page_source = yho.content	

		soup = BeautifulSoup(page_source, "html.parser")
		#all_scripts = soup.find_all('script')
		script=str(soup)

		jsData = re.search(r'"shortTermOutlook":{"stateDescription":"(.*?)","direction":', script)
		value=re.search(r'primaryColor\"\sdata-reactid=\"\d*\">(.*?)<\/div>',script)

		try:
			indic=jsData.group(1)
		except AttributeError:
			indic="--"
		try:
			value=value.group(1)
			value=f"{value:<14}"
		except AttributeError:
			value="--"
			value=f"{value:<14}"

		


			 
		padding = ""


		if len(row[0]) < 4:
			padding = ' '
		

		print(str(row[0]) + padding + "\t" + str(row[1]) + "\t" + str(watchers)+ "\t" + str(price) + "\t" + str(perc)+ "\t"+ str(sent)+ "\t" + str(trend)+ "\t"  + str(vol) + "\t" + str(volchange) + "\t" + str(value)+ "\t"+ str(indic))


if __name__ == '__main__':
    gen = get_submission(dayz)  # Get 1 day worth of submission
    all_tbl, _, _ = get_freq_list(gen)
    all_tbl = filter_tbl(all_tbl, dayz)
    print_tbl(all_tbl)
