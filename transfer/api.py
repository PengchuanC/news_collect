from datetime import date

import pandas as pd

from transfer.database.model import News
from transfer.database.insert import Session
from transfer.config import *


def news_from_remote():
    today = date.today()
    session = Session(**remote)
    news = session.session.query(News).filter(News.savedate >= today).all()
    session.close()
    return news


def news_from_local():
    today = date.today()
    session = Session(**local)
    news = session.session.query(News).filter(News.savedate >= today).all()
    session.close()
    return news


def news_to_local(news):
    session = Session(**local)
    data = [n.to_dict() for n in news]
    df = pd.DataFrame(data)
    df['savedate'] = df['savedate'].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
    for index, row in df.iterrows():
        row = pd.DataFrame(row).T
        try:
            row.to_sql("finance_news", session.engine, if_exists="append", index=False)
        except Exception as e:
            pass
    session.session.add_all(news)
    for n in news:
        session.insert_one(n)
    session.close()
    print("数据库从远程迁移到本地任务完成")


def news_to_remote(news):
    session = Session(**remote)
    data = [n.to_dict() for n in news]
    df = pd.DataFrame(data)
    df['savedate'] = df['savedate'].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
    for index, row in df.iterrows():
        row = pd.DataFrame(row).T
        try:
            row.to_sql("finance_news", session.engine, if_exists="append", index=False)
        except Exception as e:
            pass
    session.session.add_all(news)
    for n in news:
        session.insert_one(n)
    session.close()
    print("数据库从本地迁移到远程任务完成")
