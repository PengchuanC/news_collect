from app.core import *
from app.core.special import *
from app.database.model import News
from app.config import keyword, by_keyword, ignore
from app.util.similar import Similar


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
    content = row.abstract

    for ign in ignore:
        if ign in title:
            return None

    company = keyword["商业"]
    japan = keyword["日本"]
    economy = keyword["宏观"]
    finance = keyword["金融"]
    for key in japan:
        if any({key in title, key in content}):
            row.keyword = ["日本"]
            return row
    for key in company:
        if any({key in title, key in content}):
            row.keyword = "商业"
            return row
    for key in finance:
        if any({key in title, key in content}):
            row.keyword = "金融"
            break
    for key in economy:
        if any({key in title, key in content}):
            row.keyword = "宏观"
            return row
    # for section, keywords in keyword.items():
    #     for k in keywords:
    #         if k in title:
    #             row.keyword = section
    #             return row
    return row


def special_eastmoney():
    ret = []
    for i in range(1, 5):
        sem = SpecialEastMoney(None, i)
        news = sem.collect()
        ret.extend(news)
    return ret


def special_eastmoney_search_api():
    ret = []
    keywords = by_keyword["eastmoney"]
    for k in keywords:
        for i in range(1, 5):
            sems = SpecialEastMoneySearchApi(k, i)
            news = sems.collect()
            ret.extend(news)
    return ret


def special_hibor():
    ret = []
    keywords = by_keyword["hibor"]
    for k in keywords:
        sems = SpecialHiBor(k, 1)
        news = sems.collect()
        if news:
            ret.extend(news)
    return ret
