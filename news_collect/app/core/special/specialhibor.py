import json
import re
from http import cookiejar
from urllib.parse import urlencode

import requests as r
import cssselect
from lxml.html import etree

from app.core.special import SpecialCollector
from app.config import header
from app.error import NetworkError
from app.core.eastmoney import extract_content
from app.database.model import News


class SpecialHiBor(SpecialCollector):
    login_url = "http://www.hibor.org/toplogin.asp?action=login"
    url = "http://www.hibor.org/newweb/web/search"

    def cookie(self):
        payload = {
            "name": "13221735254",
            "pwd": "hb20191014",
            "tijiao.x": 30,
            "tijiao.y": 18,
            "checkbox": "on"
        }
        session = r.session()
        session.cookies = cookiejar.LWPCookieJar(filename="Cookies.txt")
        ret = session.post(self.login_url, data=payload, headers=header)
        session.cookies.save()
        session.close()
        cookie = ret.headers["Set-Cookie"]
        cookie = re.sub(r"path=/,", "", cookie)
        cookie = cookie.split(";")
        cookie = [x for x in cookie if any({"robih" in x, "MBname" in x})]
        cookie = f"MBpermission=0;{';'.join(cookie)}"
        return cookie

    def format_url(self):
        url = self.url
        return url

    def collect(self):
        url = self.url
        cookie = self.cookie()

        header["Cookie"] = cookie

        data = {
            "index": 0,
            "f": "3x",
            "sslm": "all",
            "ssfw": "ybbt",
            "gjz": self.keyword,
            "sjfw": -7,
            "page": self.page
        }

        resp = r.post(url, headers=header, data=data)
        content = resp.content.decode("utf-8")
        content = etree.HTML(content)
        article = content.cssselect("#table1 >  tr")

        news_collections = []
        for a in article:
            head = a.cssselect("td > div.tab_divttl > span:nth-child(2) > a")[0]
            url = "http://www.hibor.org" + head.get("href")
            title = head.get("title")
            save_date = a.cssselect("td > div.tab_divtxt > span:nth-child(1) > strong")[0].text
            source = a.cssselect("td > div.tab_divtxt > span:nth-child(3)")[0].text
            source = f"慧博-{source[3:]}"
            page = r.post(url, headers=header).content
            page = etree.HTML(page)
            abstract = page.xpath("/html/body/div[2]/div[5]/div[1]/div[2]/div[8]/div[1]/div/p/span/text()")
            abstract = "".join(abstract)
            news = News(title=title, abstract=abstract, url=url, savedate=save_date, source=source)
            news_collections.append(news)
        return news_collections


if __name__ == '__main__':
    shb = SpecialHiBor("资产配置", 1)
    shb.collect()
