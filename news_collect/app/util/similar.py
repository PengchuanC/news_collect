from datetime import date, timedelta
from functools import lru_cache, wraps

from jieba import lcut
from jieba import posseg
from gensim.similarities import SparseMatrixSimilarity
from gensim.corpora import Dictionary
from gensim.models import TfidfModel

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
        ret = session.query(News.title).filter(News.savedate >= _date).all()
        ret = [x[0] for x in ret]
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
            logs.info("以下新闻因重复暂不录入数据库：", [x for x in ret if x.title not in different])
            ret = [x for x in ret if x.title in different]
            return ret

        return func


if __name__ == '__main__':
    Similar.check("业绩大逆袭股曝光！行情一触即燃 已有股票八连阳")
