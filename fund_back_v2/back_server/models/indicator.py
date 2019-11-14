from . import db, Model
from sqlalchemy.dialects.mysql import DOUBLE


class Indicators(db.Model, Model):
    __tablename__ = "t_ff_indicator_for_filter"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    windcode = db.Column(db.String(10), db.ForeignKey("t_ff_funds.windcode"), nullable=False)
    indicator = db.Column(db.String(50), nullable=False)
    numeric = db.Column(DOUBLE)
    text = db.Column(db.Text)
    note = db.Column(db.String(20))
    rpt_date = db.Column(db.DateTime, nullable=False)
    update_date = db.Column(db.DateTime, nullable=False)

    funds = db.relationship("Funds", backref="filter")

    def __repr__(self):
        return f"<Indicators {self.windcode}>"


class IndicatorsForPlot(db.Model, Model):

    __tablename__ = 't_ff_indicator_for_plot'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    windcode = db.Column(db.String(10), db.ForeignKey("t_ff_funds.windcode"), nullable=False)
    fund_setupdate = db.Column(db.DateTime, nullable=False)
    fund_corp_fundmanagementcompany = db.Column(db.String(25))
    fund_fundscale = db.Column(db.Float)
    prt_netasset = db.Column(db.Float)
    rpt_date = db.Column(db.DateTime)
    update_date = db.Column(db.DateTime)

    funds = db.relationship("Funds", backref="plot")

    def __repr__(self):
        return f"<IndicatorsForPlot {self.windcode}>"
