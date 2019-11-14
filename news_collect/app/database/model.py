from sqlalchemy import Column, Integer, String, DateTime, Text

from sqlalchemy.ext.declarative import declarative_base


base = declarative_base()


class News(base):
    __tablename__ = "t_ff_news"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), unique=True)
    abstract = Column(Text)
    url = Column(Text)
    source = Column(String(20))
    savedate = Column(DateTime, nullable=False)
    keyword = Column(String(10))

    def __repr__(self):
        return f"<News {self.title}>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
