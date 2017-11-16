import sys
import urllib
import time
from bs4 import BeautifulSoup
from selenium import webdriver
import re
url_root = 'https://www.ettoday.net'
url = url_root + '/news/focus/%E6%94%BF%E6%B2%BB/'

ARTICAL_LIMITATION = 10

driver = webdriver.Chrome('/home/jaqq/anaconda3/bin/chromedriver')
driver.get(url)

class News:
    def __init__(self, title, link, date = None, author = None, content = None):
        self.title = title
        self.link = link
        self.date = date
        self.author = author
        self.content = content

news_list = {}

soup = BeautifulSoup(driver.page_source, "html.parser")
current_names = soup.select('div.part_pictxt_3')
count_artical = 0
for current_name_list in current_names:
    count_artical += 1    
    if count_artical > ARTICAL_LIMITATION:
        break
    titles = current_name_list.select('h3 > a')
    for title in titles:        
        link = re.findall(r"/news\S+\.htm", title['href'])
        if len(link) == 0:
            continue
        news_list[title.text] = News(title.text, url_root + link[0])


for key, news in news_list.items():
    print(news.title, news.link)
