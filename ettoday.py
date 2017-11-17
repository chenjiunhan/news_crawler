import sys
import urllib
import time
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import datetime
import time
from time import gmtime, strftime

url_root = 'https://www.ettoday.net'
url = url_root + '/news/focus/%E6%94%BF%E6%B2%BB/'

ARTICAL_LIMITATION = 1000

driver = webdriver.Chrome('/home/jaqq/anaconda3/bin/chromedriver')
driver.get(url)

class News:
    def __init__(self, title, link, date = None, author = None, content = None):
        self.title = title
        self.link = link
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
        #TODO cross year        
        print(date)
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
    '''soup = BeautifulSoup(driver.page_source, "html.parser")
    last_date = soup.findAll("span", {"class" : "date"})
    print(last_date)
    last_date = last_date[-1].text
    last_date = get_date_ts_from_str(last_date)
    last_date_ts = int(time.mktime(datetime.datetime.strptime(last_date, '%Y-%m-%d %H:%M').timetuple()))'''

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
        print(last_date_ts, int(time.mktime(time.gmtime(time.time()))) - 86400)
    if count_scroll > 100:
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
    print(date)
    date = get_date_ts_from_str(date)
    print(date)
    date_ts = int(time.mktime(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M').timetuple()))

    #for title in titles:        
    link = re.findall(r"/news\S+\.htm", title['href'])
    #if len(link) == 0:
    #    continue
    print(title.text, url_root + link[0], date)
    news_dict[title.text] = News(title.text, url_root + link[0], date = date_ts)


for key, news in news_dict.items():
    print(news.title, news.link, news.date)
    driver.get(news.link)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    news_content = soup.select('div.story')[0].get_text()
    news_dict[key] = news_content
    time.sleep(5)

f = open('news', 'w')

#for key, news in news_dict.items():
    #w
f.close()
