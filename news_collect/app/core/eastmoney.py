import re
import time
from datetime import date

import requests as r
import cssselect
from lxml.html import etree

from app.core import Collector
from app.config import header
from app.error import NetworkError
from app.database.model import News


class EastMoney(Collector):

    url = "http://finance.eastmoney.com"
    url2 = "http://biz.eastmoney.com"

    def format_url(self):
        if self.section != "商业":
            return _format_url(self.url, self.path, self.page)
        else:
            return _format_url(self.url2, self.path, self.page)

    def collect(self):
        url = self.format_url()
        news_collections = _collect(url)
        _news_collections = []
        for n in news_collections:
            n.keyword = self.section
            if self.section == "日本":
                if any({"日本" in n.title, "日本" in n.abstract}):
                    _news_collections.append(n)
            else:
                _news_collections.append(n)
        return _news_collections


def _format_url(url, path, page):
    """
    格式化东方财富网板块链接
    :param url: 东方财富网主页链接
    :param path: 板块路由
    :param page: 页码
    :return: 格式化的网址
    """
    return f"{url}/{path}_{page}.html"


def _collect(url):
    """
    获取爬虫内容
    :param url: 目标链接
    :return: 目标内容
    """
    header["Referer"] = url
    response = r.get(url, headers=header)
    if response.status_code != 200:
        raise NetworkError(f"东方财富网访问失败\n\tstatus_code: {response.status_code}\n\turl:{url}")
    content = response.content.decode("utf-8")
    html = etree.HTML(content)
    span = html.cssselect('#newsListContent > li')

    news_collection = []
    for s in span:
        head = s.cssselect("div.text > p.title > a")[0]
        title = head.text.strip()
        url = head.get("href")
        abstract = s.cssselect("div.text > p.info")[0].get("title")
        abstract = abstract if abstract else s.cssselect("div.text > p.info")[0].text
        abstract = re.sub(r"[\r\n\s]", "", abstract)
        abstract = abstract.split("】")[-1] if abstract else abstract
        patten = re.compile(r"[（](.*?)[）]", re.S)
        source = re.findall(patten, abstract) if abstract else None
        source = source[-1] if source else "东方财富"
        save_date = s.cssselect("div.text > p.time")[0].text.strip()
        save_date = save_date.replace("月", "/")
        save_date = save_date.replace("日", "")
        save_date = f"{date.today().year}/{save_date}"
        save_date = time.strptime(save_date, "%Y/%m/%d %H:%M")
        news = News(title=title, abstract=abstract, url=url, source=source, savedate=save_date)
        news_collection.append(news)
    return news_collection

