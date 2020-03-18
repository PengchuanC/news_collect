from . import Model, db


class Funds(db.Model, Model):
    __tablename__ = "t_ff_funds"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    windcode = db.Column(db.String(10), nullable=False, primary_key=True)
    category = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Funds {self.windcode}>"


class FundNav(db.Model, Model):
    __tablename__ = "t_ff_fund_nav"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    windcode = db.Column(db.String(10), db.ForeignKey("t_ff_funds.windcode"), nullable=False, primary_key=True)
    nav = db.Column(db.Float)
    nav_adj = db.Column(db.Float)
    date = db.Column(db.Date, nullable=False)

    funds = db.relationship("Funds", backref="nav")
