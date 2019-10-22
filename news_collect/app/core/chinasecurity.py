import os
import re
import time

import requests as r
import cssselect
from lxml.html import etree

from app.core import Collector
from app.config import header
from app.error import NetworkError
from app.database.model import News


class ChinaSecurity(Collector):

    url = "http://www.cs.com.cn/xwzx/hg/"

    def format_url(self):
        return self.url

    def collect(self):
        url = self.format_url()
        response = r.get(url, headers=header)
        if response.status_code != 200:
            raise NetworkError(f"中国证券报访问失败\n\tstatus_code: {response.status_code}\n\turl:{url}")
        content = response.content
        html = etree.HTML(content)
        articles = html.cssselect("ul.list-lm > li")

        news_collections = []

        for a in articles:
            title = a.cssselect("a")[0].text
            url = a.cssselect("a")[0].get("href")
            url = os.path.join(self.url, url)
            save_date = a.cssselect("span")[0].text
            save_date = time.strptime(save_date, "%y-%m-%d %H:%M")
            response = r.get(url)
            html = etree.HTML(response.content)
            source = html.cssselect("body > div:nth-child(9) > div.box835.hidden.left > div.article > div.info > "
                                    "p:nth-child(2) > em:nth-child(2)")[0].text[3:]
            try:
                # abstract = html.cssselect("div.article-t.hidden > p:nth-child(1)")[0].text.strip()
                abstracts = html.cssselect("div.article-t.hidden > p")
                for p in abstracts:
                    if p.text:
                        abstract = p.text.strip()
                        break
                else:
                    abstract = None
            except IndexError:
                try:
                    # abstract = html.cssselect("div.article-t.hidden > div > p:nth-child(1)")[0].text.strip()
                    abstracts = html.cssselect("div.article-t.hidden > div > p")
                    for p in abstracts:
                        if p.text:
                            abstract = p.text.strip()
                            break
                    else:
                        abstract = None
                except IndexError:
                    abstract = None

            news = News(title=title, abstract=abstract, url=url, savedate=save_date, source=source,
                        keyword=self.section)
            news_collections.append(news)
        return news_collections
