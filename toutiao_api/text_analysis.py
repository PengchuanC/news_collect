import re
from datetime import datetime

import requests as r
from textrank4zh import TextRank4Sentence

from api import news_format
from model import News

tr4s = TextRank4Sentence()


def get_method(url: str):
    """
    通过GET请求获取数据
    :param url: 今日头条财经栏目Url
    :return: json
    """
    header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/76.0.3809.100 Safari/537.36"}

    resp = r.get(url, headers=header)
    if resp.status_code != 200:
        raise IOError(f"访问失败，错误码{resp.status_code}")

    text = resp.text
    return text


def abstract(news):
    url = "https://www.toutiao.com/a" + news['item_id']
    html = get_method(url)
    content = re.findall('.*content(.*)slice.*', html)
    if not content:
        return
    uni = content[0]
    uni = re.sub(r"\\u003C", '<', uni)
    uni = re.sub(r"\\u003E", ">", uni)
    uni = re.sub(r"\\&quot", "", uni)

    dr = re.compile('<[^>]+>', re.S)
    dd = dr.sub('', uni)

    tr4s.analyze(text=dd, lower=True, source='all_filters')
    _abstract = []
    for i in tr4s.get_key_sentences():
        _abstract.append([i.index, i.sentence])

    # _abstract = sorted(_abstract[:10], key=lambda x: x[0])
    return _abstract[0][1]


def prepare(pages):
    data = news_format(pages)
    data_set = []

    for d in data:
        if d['title'] == d['abstract']:
            try:
                abst = abstract(d)
                d['abstract'] = abst
            except IndexError:
                pass
        url = "https://www.toutiao.com/a" + d['url']
        t = News(title=d['title'], abstract=d['abstract'], url=url, source=d['source'], savedate=datetime.now())
        data_set.append(t)
    return data_set