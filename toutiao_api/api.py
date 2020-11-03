import json
import requests as r
import pandas as pd


def news_url_format(max_behot_time=0):
    """
    根据max_behot_time返回网址，初始设置为0，默认获取最新新闻
    :param max_behot_time:
    :return:
    """
    url = f"https://www.toutiao.com/api/pc/feed/?category=news_finance&utm_source=toutiao&widen=1&max_behot_time={max_behot_time}" \
          f"&max_behot_time_tmp={max_behot_time}"
    return url


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

    data = json.loads(resp.text)
    if data['message'] != "success":
        raise IOError("从今日头条获取数据失败")
    return data


def x_page_news(pages: int):
    """
    输入页数获取多页新闻
    :param pages: 页数
    :return: List<Toutiao Data>
    """
    i = 0
    url = news_url_format()

    ret = []
    while i < pages:
        data = get_method(url)
        ret.append(data)
        behot = data["next"]["max_behot_time"]
        url = news_url_format(behot)
        i += 1

    return ret


def news_format(pages: int):
    data = x_page_news(pages)
    news = []
    for d in data:
        news.extend(d['data'])
    return news


if __name__ == '__main__':
    news = news_format(5)
    print(news)
