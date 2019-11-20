from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

from app.database.model import News
from app.database.connector import default_session
from app.util.cache import Cache

target = {"宏观": 1, "金融": 2, "商业": 3, "日本": 4}
target_reverse = {y: x for x, y in target.items()}
vec = CountVectorizer()
mnb = MultinomialNB()


def fetch_data():
    se = default_session()
    ret = se.query(News.title, News.abstract, News.keyword).filter(
        News.keyword.in_(["宏观", "金融", "商业", "日本"])
    ).all()
    se.close()
    ret = [(x[0] + str(x[1]), x[2]) for x in ret]
    x = [i[0] for i in ret]
    y = [target.get(i[1]) for i in ret]
    return x, y


def train_data_set():
    cache = Cache("bayes", fetch_data)
    x, y = cache.cache()
    x = vec.fit_transform(x)
    mnb.fit(x, y)
    return mnb


def predict(news):
    train_data_set()
    x = vec.transform([news])
    pre = mnb.predict(x)
    pre = target_reverse.get(pre[0])
    return pre


if __name__ == '__main__':
    a = predict("国家统计局")
    print(a)
