from . import Model, db


class News(db.Model, Model):
    __tablename__ = "t_ff_news"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), unique=True, index=True)
    abstract = db.Column(db.Text)
    url = db.Column(db.Text)
    source = db.Column(db.String(20))
    keyword = db.Column(db.String(10))
    savedate = db.Column(db.DateTime, nullable=False, index=True)

    def __repr__(self):
        return f"<News {self.title}>"
