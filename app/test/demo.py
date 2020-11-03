from jieba import lcut
from jieba import posseg
from gensim.similarities import SparseMatrixSimilarity
from gensim.corpora import Dictionary
from gensim.models import TfidfModel

from app.config import database_remote as database
from app.database.insert import Session
from app.database.model import News


session = Session(**database).session
ret = session.query(News).filter(News.savedate >= "2019-10-28").all()
session.close()


def similar(aim):
    aim_text = aim.title + aim.abstract
    simple = [x.title+x.abstract for x in ret[0:-10]]
    text = [set(posseg.lcut(x)) for x in simple]
    text = list({y for x in text for y in x})
    dictionary = Dictionary(text)
    length = len(dictionary.token2id)
    corpus = [dictionary.doc2bow(lcut(src)) for src in simple]
    tfidf = TfidfModel(corpus)
    tf_texts = tfidf[corpus]
    sparse_matrix = SparseMatrixSimilarity(tf_texts, length)

    vector = dictionary.doc2bow(lcut(aim_text))
    tf_kw = tfidf[vector]
    similarities = sparse_matrix.get_similarities(tf_kw)

    print(aim.title)
    for e, s in enumerate(similarities, 1):
        if s > 0.1:
            print(s, ret[e-1].title)


for aim in ret[-10:]:
    similar(aim)
