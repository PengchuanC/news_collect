from datetime import date, timedelta
from functools import lru_cache, wraps

from jieba import lcut
from jieba import posseg
from gensim.similarities import SparseMatrixSimilarity
from gensim.corpora import Dictionary
from gensim.models import TfidfModel
from fuzzywuzzy import fuzz

from app.database.model import News
from app.database.insert import Session
from app.config import database_remote as database
from app.logger import logs


class Similar(object):

    @staticmethod
    def check(news):
        """检查是否重复"""
        dictionary, corpus, num_features = Similar.dictionary()
        kw_vector = dictionary.doc2bow(lcut(news))
        tfidf = TfidfModel(corpus)
        tf_texts = tfidf[corpus]
        tf_kw = tfidf[kw_vector]
        sparse_matrix = SparseMatrixSimilarity(tf_texts, num_features)
        similarities = sparse_matrix.get_similarities(tf_kw)
        for e, s in enumerate(similarities, 1):
            if 0.6 < s < 0.98:
                return
        return news

    @staticmethod
    def one_week():
        today = date.today()
        one_week = today - timedelta(days=3)
        return one_week

    @staticmethod
    @lru_cache(None)
    def simple(_date):
        """样本集
        :return: List<News>
        """
        session = Session(**database).session
        ret = session.query(News.title, News.abstract).filter(News.savedate >= _date).all()
        ret = [x[0] + x[1] for x in ret]
        session.close()
        return ret

    @staticmethod
    def test(news):
        Similar.check(news)

    @staticmethod
    def dictionary():
        _date = Similar.one_week()
        simple = Similar.simple(_date)
        stop = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'r']
        ret = [posseg.lcut(x) for x in simple]
        ret = [i for texts in ret for i in texts]
        ret = [x for x in ret if x.flag not in stop]
        ret = list(set(ret))
        dictionary = Dictionary(ret)
        num_features = len(dictionary.token2id)
        corpus = [dictionary.doc2bow(lcut(src)) for src in simple]
        return dictionary, corpus, num_features

    @staticmethod
    def check_similar(inner):
        @wraps(inner)
        def func(*args, **kwargs):
            ret = inner(*args, **kwargs)
            different = [Similar.check(x.title) for x in ret]
            logs.info(f"以下新闻因重复暂不录入数据库：{[x for x in ret if x.title not in different]}")
            ret = [x for x in ret if x.title in different]
            return ret

        return func


class Similarity(object):
    @staticmethod
    def simple(_date):
        """样本集
        :return: List<News>
        """
        session = Session(**database).session
        ret = session.query(News.title, News.abstract).filter(News.savedate >= _date - timedelta(days=5)).all()
        if not ret:
            ret = session.query(News.title, News.abstract).filter(News.savedate >= _date - timedelta(days=1)).all()
        session.close()
        ret = [Similarity.reduce(x[0] + x[1]) for x in ret]
        return ret

    @staticmethod
    def reduce(text):
        stop = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'r']
        text = [x.word for x in posseg.lcut(text) if x.flag not in stop]
        text = "".join(text)
        return text

    @staticmethod
    def check(text1, text2):
        ret = fuzz.token_sort_ratio(text1, text2)
        return ret

    @staticmethod
    def compare(news):
        news = [x for x in news if x.abstract]
        all_news = []
        simple = Similarity.simple(date.today())
        for n in news:
            if n.keyword == "资产配置":
                print(n)
                all_news.append(n)
            title = Similarity.reduce(n.title + str(n.abstract))
            for s in simple:
                ratio = Similarity.check(s, title)
                if ratio > 30:
                    break
            else:
                all_news.append(n)
        return all_news

    @staticmethod
    def check_similar(inner):
        @wraps(inner)
        def func(*args, **kwargs):
            ret = inner(*args, **kwargs)
            different = Similarity.compare(ret)
            return different
        return func


if __name__ == '__main__':
    print(Similarity.compare(News(title="区块链“弄潮” 基金揭秘三路径提振个股业绩",
                                  abstract="10月28日，A股三大股指全线收涨，盘中最抢眼的当属区块链板块，早盘集合竞价便掀起涨停潮。截至收盘，区块链指数单日上涨8.85%，板块中广博股份、晨鑫科技、金冠股份等40只个股涨停。虽然市场热情高涨，但多位公私募基金经理却表示对区块链了解并不深入，也并无相关操作。")))
