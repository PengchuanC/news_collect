import os
import time
from http import cookiejar

import requests as r
import cssselect
from lxml.html import etree

from app.core.special import SpecialCollector
from app.config import header
from app.database.model import News
from app.config import base_dir


class SpecialHiBor(SpecialCollector):
    login_url = "http://www.hibor.org/toplogin.asp?action=login"
    url = "http://www.hibor.org/newweb/web/search"
    proxy = None

    def get_cookie(self):
        payload = {
            "name": "13269431992",
            "pwd": "abcd1234",
            "tijiao.x": 7,
            "tijiao.y": 9,
            "checkbox": "on"
        }
        session = r.session()
        session.cookies = cookiejar.LWPCookieJar(filename=os.path.join(base_dir, "src/cookies.txt"))
        session.post(self.login_url, data=payload, headers=header)
        # session.cookies.save()
        session.close()
        cookie = session.cookies
        return cookie

    def cookie(self):
        cookie = os.path.join(base_dir, "src/cookies.txt")
        if os.path.exists(cookie):
            cookie = cookiejar.LWPCookieJar(filename=cookie)
        else:
            cookie = self.get_cookie()
        return cookie

    def format_url(self):
        url = self.url
        return url

    def collect(self):
        url = self.url
        cookie = self.get_cookie()
        print(cookie)

        data = {
            "index": 0,
            "f": "3x",
            "sslm": "all",
            "ssfw": "ybbt",
            "gjz": self.keyword,
            "sjfw": 1,
            "page": self.page
        }
        session = r.session()
        session.cookies = cookie
        resp = session.post(url, headers=header, data=data)
        content = resp.content.decode("utf-8")
        if not content:
            self.get_cookie()
            return
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
            page = session.post(url, headers=header).content
            page = str(page, encoding="gbk")
            page = etree.HTML(page)
            abstract = page.xpath("//div[@class='p_main']/p/span/text()")
            abstract = "".join(abstract)
            news = News(title=title, abstract=abstract, url=url, savedate=save_date, source=source, keyword="资产配置")
            print(news)
            if "期货" not in title:
                news_collections.append(news)
            time.sleep(5)
        session.close()
        return news_collections


if __name__ == '__main__':
    shb = SpecialHiBor("资产配置", 1)
    shb.collect()
