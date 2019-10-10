import re
import time

import requests as r
import cssselect
from lxml.html import etree

from app.core import Collector
from app.config import header
from app.error import NetworkError
from app.database.model import News


class Kyodo(Collector):

    url = "https://china.kyodonews.net/news"

    def format_url(self):
        return f"{self.url}/{self.path}?page={self.page}"

    def collect(self):
        url = self.format_url()
        response = r.get(url, headers=header)
        if response.status_code != 200:
            raise NetworkError(f"共同网访问失败\n\tstatus_code: {response.status_code}\n\turl:{url}")
        content = response.content.decode("utf-8")
        html = etree.HTML(content)
        articles = html.cssselect("#js-postListItems > li")

        news_collection = []

        for a in articles:
            title = a.cssselect("a > h3")[0].text
            url = "https://china.kyodonews.net" + a.cssselect("a")[0].get("href")
            save_date = a.cssselect("p.time")[0].text
            save_date = re.sub(r"[\s日|]", "", save_date)
            save_date = re.sub(r"[年月]", "/", save_date)
            save_date = time.strptime(save_date, "%Y/%m/%d-%H:%M")
            source = a.cssselect("a")[-1].text
            response = r.get(url)
            html = etree.HTML(response.content)
            abstract = html.cssselect("div.article-body > p:nth-child(1)")[0].text
            abstract = re.sub(r"[\r\s\t]", "", abstract)
            abstract = abstract.split("】")[-1]
            news = News(title=title, abstract=abstract, url=url, savedate=save_date, source=source, keyword=self.section)
            # if any({"日本" in news.title, "日本" in news.abstract}) and
            if "快讯" not in news.title:
                news_collection.append(news)
        return news_collection
