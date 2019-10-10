import json
import datetime

import requests as r


from app.core import Collector
from app.config import header
from app.error import NetworkError
from app.database.model import News


class Sina(Collector):

    url = "http://feed.mix.sina.com.cn/api/roll/get?pageid=186&lid=1746&num=50&page=1"

    def format_url(self):
        return self.url

    def collect(self):
        url = self.format_url()
        response = r.get(url, headers=header)
        if response.status_code != 200:
            raise NetworkError(f"新浪财经网访问失败\n\tstatus_code: {response.status_code}\n\turl:{url}")
        content = response.content
        content = json.loads(content)
        data = content["result"]['data']
        data = [[d['title'], d['intro'], d["url"], d["media_name"], datetime.datetime.fromtimestamp(int(d["mtime"]))] for d in data]

        news_collections = []

        for d in data:
            title, abstract, url, source, save_ate = d
            news = News(title=title, abstract=abstract, url=url, source=source, savedate=save_ate, keyword=self.section)
            if not news.abstract.startswith("http"):
                news_collections.append(news)
        return news_collections
