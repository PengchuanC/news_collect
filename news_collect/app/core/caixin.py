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


class CaiXin(Collector):

    url = "caixin.com/"

    def format_url(self):
        return f"http://{self.path}.{self.url}"

    def collect(self):
        url = self.format_url()
        header["Referer"] = url
        response = r.get(url, headers=header)
        if response.status_code != 200:
            raise NetworkError(f"财新网访问失败\n\tstatus_code: {response.status_code}\n\turl:{url}")
        content = response.content.decode("utf-8")
        html = etree.HTML(content)
        articles = html.cssselect("#listArticle > div.boxa")

        news_collections = []

        for a in articles:
            title = a.cssselect("h4 > a")[0].text
            url = a.cssselect("h4 > a")[0].get("href")
            abstract = a.cssselect("p")[0].text
            save_date = a.cssselect("span")[0].text[-12:]
            save_date = save_date.replace("月", "/")
            save_date = save_date.replace("日", "")
            save_date = f"{date.today().year}/{save_date}"
            save_date = time.strptime(save_date, "%Y/%m/%d %H:%M")
            news = News(title=title, abstract=abstract, url=url, savedate=save_date, source="财新网", keyword=self.section)
            news_collections.append(news)
        return news_collections


if __name__ == '__main__':
    cx = CaiXin("宏观", "economy", 0)
    ns = cx.collect()
    print(ns[5].to_dict())
