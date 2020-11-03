import os
import shelve
import random
import re

import requests as r
import cssselect
from lxml import etree

from app.config import base_dir


def get_ip():
    url = "https://www.xicidaili.com/nt/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0', }
    resp = r.get(url=url, headers=headers)
    content = resp.content.decode("utf-8")
    html = etree.HTML(content)
    table = html.cssselect("#ip_list > tr")

    proxies = {"http": [], "https": []}
    for tr in table[1:]:
        ip = tr.cssselect("td:nth-child(2)")[0].text
        port = tr.cssselect("td:nth-child(3)")[0].text
        protocol = tr.cssselect("td:nth-child(6)")[0].text
        exist = tr.cssselect("td:nth-child(9)")[0].text
        if "天" not in exist:
            continue
        date = int(re.findall(r"\d+", exist)[0])
        if date < 10:
            continue
        proxy = f"{ip}:{port}"
        if protocol.lower() == "http":
            proxies["http"].append(proxy)
        else:
            proxies["https"].append(proxy)
    return proxies


def test(proxy):
    try:
        url = "http://www.hibor.org"
        r.get(url, proxies=proxy, timeout=10, verify=False)
        return True
    except:
        return False


def run():
    proxies = get_ip()
    while True:
        proxy = {
            'http': random.choice(proxies["http"]),
            "https": random.choice(proxies["https"])
        }
        ret = test(proxy)
        if ret:
            break
    return proxy


if __name__ == '__main__':
    print(run())
