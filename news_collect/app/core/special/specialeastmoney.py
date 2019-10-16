import json
import re
from urllib.parse import urlencode

import requests as r
import cssselect
from lxml.html import etree

from app.core.special import SpecialCollector
from app.config import header
from app.error import NetworkError
from app.core.eastmoney import extract_content
from app.database.model import News


class SpecialEastMoney(SpecialCollector):
    url = "http://finance.eastmoney.com/a/cywjh_page.html"

    def format_url(self):
        url = re.sub("page", str(self.page), self.url)
        return url

    def collect(self):
        url = self.format_url()
        response = r.get(url, headers=header)
        if response.status_code != 200:
            raise NetworkError(f"东方财富网访问失败\n\tstatus_code: {response.status_code}\n\turl:{url}")
        content = response.content.decode("utf-8")
        html = etree.HTML(content)
        articles = html.cssselect("#newsListContent > li")
        news_collection = extract_content(articles, self.keyword)
        return news_collection


class SpecialEastMoneySearchApi(SpecialCollector):
    refer = "http://so.eastmoney.com/CArticle/s"
    url = "http://api.so.eastmoney.com/bussiness/Web/GetSearchList"

    def format_url(self):
        refer_data = {
            "keyword": self.keyword,
            "pageindex": self.page,
            "searchrange": "16384",
            "sortfield": "8"
        }
        self.refer = self.refer + "?" + urlencode(refer_data)
        data = {
            "type": "16392",
            "keyword": self.keyword,
            "pageindex": self.page,
            "name": "caifuhaowenzhang",
        }
        url = self.url + "?" + urlencode(data)
        return url

    def collect(self):
        url = self.format_url()
        header["Referer"] = self.refer
        response = r.get(url, headers=header)
        if response.status_code != 200:
            raise NetworkError(f"东方财富网访问失败\n\tstatus_code: {response.status_code}\n\turl:{url}")
        content = response.content.decode("utf-8")
        data = json.loads(content)["Data"]

        news_collection = []

        if not data:
            return news_collection

        for d in data:
            title = re.sub(r"[<em></em>]", "", d["Title"])
            abstract = d["Content"]
            url = d["ArticleUrl"]
            source = d["NickName"]
            save_date = d["ShowTime"]
            news = News(title=title, abstract=abstract, url=url, savedate=save_date, source=source,
                        keyword=self.keyword)
            news_collection.append(news)
        return news_collection


if __name__ == '__main__':
    SEM = SpecialEastMoneySearchApi("公募基金", 1)
    ret = SEM.collect()
    print(ret[5].to_dict())
