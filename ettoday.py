import sys
import urllib
import time
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import datetime
import time
import os
from time import gmtime, strftime

url_root = 'https://www.ettoday.net'
url = url_root + '/news/focus/%E6%94%BF%E6%B2%BB/'

ARTICAL_LIMITATION = 1000
NEWS_DIR_PATH = 'news' + os.sep
SAVE_TO_ONE_FILE = False
FROM_DATE = '2017-11-19'
TO_DATE = '2017-11-19'
ONE_FILE_DIR = NEWS_DIR_PATH + 'one_file' + os.sep
ONE_FILE_PATH = ONE_FILE_DIR + FROM_DATE + '_to_' + TO_DATE + '.txt'

driver = webdriver.Chrome('/home/jaqq/anaconda3/bin/chromedriver')
driver.get(url)

class News:
    def __init__(self, title, link, date_ts = None, date = None, author = None, content = None):
        self.title = title
        self.link = link
        self.date_ts = date_ts
        self.date = date
        self.author = author
        self.content = content

news_dict = {}


count_scroll = 0
SCROLL_PAUSE_TIME = 2
last_height = driver.execute_script("return document.body.scrollHeight")

def get_date_ts_from_str(date_str):
    date = re.findall(r"([0-9]+)月([0-9]+)日 ([0-9]+):([0-9]+)", date_str)    
    if len(date) > 0:
        date = date[0]
        if int(datetime.datetime.now().month) < int(date[1]):
            year = int(datetime.datetime.now().year) - 1
        else:
            year = int(datetime.datetime.now().year)

        return str(year) + '-' + str(date[0]) + '-' + str(date[1]) + ' ' + str(date[2]) + ':' + str(date[3])
    
    date = re.findall(r"([0-9]+)秒前", date_str)
    if len(date) > 0:
        date = datetime.datetime.fromtimestamp(int(time.mktime(time.localtime())) - int(date[0])).strftime("%Y-%m-%d %H:%M")
        return date

    date = re.findall(r"([0-9]+)分鐘前", date_str)
    if len(date) > 0:
        date = datetime.datetime.fromtimestamp(int(time.mktime(time.localtime())) - int(date[0]) * 60).strftime("%Y-%m-%d %H:%M")
        return date

    date = re.findall(r"([0-9]+)小時前", date_str)
    if len(date) > 0:
        date = datetime.datetime.fromtimestamp(int(time.mktime(time.localtime())) - int(date[0]) * 3600).strftime("%Y-%m-%d %H:%M")
        return date
    
    date = re.findall(r"([0-9]+-[0-9]+-[0-9]+ [0-9]+:[0-9]+)", date_str)
    if len(date) > 0:
        return date_str

while True:

    soup = BeautifulSoup(driver.page_source, "html.parser")
    news_divs = soup.select('div.part_pictxt_3')
    date = news_divs[-1].find_all("span", {"class": "date"})
    date = date[-1].text
    date = get_date_ts_from_str(date)
    last_date_ts = int(time.mktime(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M').timetuple()))

    count_scroll += 1

    if last_date_ts < int(time.mktime(time.gmtime(time.time()))) - 86400:     
        break
    else:
        pass

    if count_scroll > 1:
        break
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

soup = BeautifulSoup(driver.page_source, "html.parser")
news_divs = soup.select('div.part_pictxt_3')
news_divs = news_divs[0].find_all("div", {"class": "piece"})
count_artical = 0
for current_news in news_divs:
    count_artical += 1    
    if count_artical > ARTICAL_LIMITATION:
        break
    title = current_news.select('h3 > a')
    title = title[0]

    date = current_news.select("span[class=date]")
    date = date[-1].text
    date = get_date_ts_from_str(date)
    date_ts = int(time.mktime(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M').timetuple()))

    link = re.findall(r"/news\S+\.htm", title['href'])
    
    print(title.text, url_root + link[0], date)
    
    news_dict[title.text] = News(title.text, url_root + link[0], date_ts = date_ts, date = datetime.datetime.fromtimestamp(date_ts))

if SAVE_TO_ONE_FILE:
    if not os.path.exists(ONE_FILE_DIR):
        os.makedirs(ONE_FILE_DIR)
    f = open(ONE_FILE_PATH, 'w')

for key, news in news_dict.items():
    #print(news.title, news.link, news.date)
    print(news.date.year, news.date.month, news.date.day)
    driver.get(news.link)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    news_content = soup.select('div.story')[0].get_text()
    news_dict[key].content = news_content
    # TODO get correct date here
    if SAVE_TO_ONE_FILE:
        f.write(news.content)
    else:
        news_dir = NEWS_DIR_PATH + os.sep + str(news.date.year) + os.sep + str(news.date.month) + os.sep + str(news.date.day) + os.sep
        if not os.path.exists(NEWS_DIR_PATH):
            os.makedirs(news_dir)
        # TODO append
        f = open(news_dir + 'news.txt', 'w')
        f.write(news.content)
        f.close()
    time.sleep(5)
    break

if SAVE_TO_ONE_FILE:
    f.close()
