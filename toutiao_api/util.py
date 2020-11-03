import requests as r


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

    resp.encoding = 'utf-8'
    text = resp.text
    return text