from . import db, Model


class FundPerformance(db.Model, Model):
    __tablename__ = 't_ff_performance'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    windcode = db.Column(db.String(10), db.ForeignKey("t_ff_funds.windcode"), nullable=False, index=True)
    indicator = db.Column(db.String(20), nullable=False)
    value = db.Column(db.Float)
    update_date = db.Column(db.DateTime, nullable=False)

    funds = db.relationship("Funds", backref="performance")

    def __repr__(self):
        return f"<FundPerformance {self.windcode}>"
