import re

import requests as r
import cssselect
from lxml.html import etree

from app.core.special import SpecialCollector
from app.config import header
from app.error import NetworkError
from app.core.eastmoney import extract_content


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


if __name__ == '__main__':
    SEM = SpecialEastMoney(None, 1)
    ret = SEM.collect()
    print(ret[0].to_dict())
