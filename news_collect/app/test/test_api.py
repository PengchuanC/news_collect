import unittest
from app.api import *


class TestApi(unittest.TestCase):

    def test_chinasecurity(self):
        news = chinasecurity("宏观", "", 0)
        for n in news:
            n_r = revise(n)
            print(n_r.title, n.keyword)
            if n_r.keyword != n.keyword:
                print(n_r.to_dict())

    def test_sina(self):
        news = sina("金融", "", 1)
        for n in news:
            n_r = revise(n)
            print(n_r.title, n.keyword)
            if n_r.keyword != n.keyword:
                print(n_r.to_dict())

    def test_eastmoney(self):
        news = eastmoney("金融", "news/czqyw", 1)
        for n in news:
            n_r = revise(n)
            if not n_r:
                break
            if n_r.keyword != n.keyword:
                print(n_r.to_dict())

    def test_caixin(self):
        news = caixin("商业", "companies", 1)
        for n in news:
            n_r = revise(n)
            if not n_r:
                break
            print(n_r.title, n.keyword)
            if n_r.keyword != n.keyword:
                print(n_r.to_dict())


if __name__ == '__main__':
    unittest.main()
