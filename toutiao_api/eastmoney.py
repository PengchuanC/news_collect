import re

from datetime import datetime

from bs4 import BeautifulSoup

from util import get_method
from model import News


URL = "http://finance.eastmoney.com/yaowen.html"


def east_money(url=URL):
    data = get_method(url)
    data = BeautifulSoup(data, 'lxml')
    li = data.find_all("div", attrs={"id": 'artitileList1'})
    cd = li[0].contents[1].find_all('div')

    data = []
    for section in cd:
        s = section
        title = section.find("p", attrs={'class': "title"})
        if title:
            title = title.text
            href = section.find("a").get("href")
            info = section.find("p", attrs={'class': "info"}).get('title')
            info_check = section.find("p", attrs={'class': "info"}).text
            if len(info) <= len(info_check):
                info = info_check
            time = section.find("p", attrs={'class': "time"}).text
            time = time_format(time)
            news = News(title=title, abstract=info, url=href, source="东方财富", savedate=time)
            data.append(news)

    return data


def time_format(time):
    time = re.sub("月", '-', time)
    time = re.sub("日", '', time)
    time = str(datetime.now().year) + '-' + time
    return time


east_money(URL)