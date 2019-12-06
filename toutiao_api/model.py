from sqlalchemy import Column, String, Integer, TEXT, DateTime, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


base = declarative_base()


class News(base):
    __tablename__ = 'finance_news'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, unique=True, index=True)
    abstract = Column(TEXT)
    url = Column(TEXT)
    source = Column(String(20))
    savedate = Column(DateTime)

    def __repr__(self):
        return f"<Toutiao {self.title}>"

    @staticmethod
    def connector(user, password):
        engine = News.engine(user, password)
        session = sessionmaker(bind=engine)
        return session

    @staticmethod
    def engine(user, password):
        engine = create_engine(f"mysql+pymysql://{user}:{password}@localhost:3306/fund_filter?charset=utf8mb4")
        return engine
