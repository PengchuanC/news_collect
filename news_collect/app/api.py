from app.core import *
from app.database.model import News
from app.config import keyword


def eastmoney(section, path, page):
    em = EastMoney(section, path, page)
    news = em.collect()
    return news


def caixin(section, path, page):
    cx = CaiXin(section, path, page)
    news = cx.collect()
    return news


def chinasecurity(section, path, page):
    cs = ChinaSecurity(section, path, page)
    news = cs.collect()
    return news


def sina(section, path, page):
    s = Sina(section, path, page)
    news = s.collect()
    return news


def kyodo(section, path, page):
    kd = Kyodo(section, path, page)
    news = kd.collect()
    return news


def revise(row: News):
    """纠错，根据config文件的关键字分布，对新闻重新分组"""
    title = row.title
    for section, keywords in keyword.items():
        for k in keywords:
            if k in title:
                row.keyword = section
                return row
    return row
