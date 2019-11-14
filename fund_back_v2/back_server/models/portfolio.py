from back_server import db


class Portfolio(db.Model):
    __tablename__ = "t_ff_portfolio"
    port_id = db.Column(db.Integer, primary_key=True, nullable=False)
    port_name = db.Column(db.String(30), nullable=False)
    port_type = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Portfolio {self.port_name}>"


class PortfolioObserve(db.Model):
    __tablename__ = "t_ff_portfolio_observe"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    port_id = db.Column(db.Integer, db.ForeignKey("t_ff_portfolio.port_id"), nullable=False)
    windcode = db.Column(db.String(12), nullable=False)
    update_date = db.Column(db.DateTime, nullable=False)

    portfolio = db.relationship("Portfolio", backref="observe")

    def __repr__(self):
        return f"<PortfolioObserve {self.port_id}>"


class PortfolioCore(db.Model):
    __tablename__ = "t_ff_portfolio_core"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    port_id = db.Column(db.Integer, db.ForeignKey("t_ff_portfolio.port_id"), nullable=False)
    windcode = db.Column(db.String(12), nullable=False)
    update_date = db.Column(db.DateTime, nullable=False)

    portfolio = db.relationship("Portfolio", backref="core")

    def __repr__(self):
        return f"<PortfolioObserve {self.port_id}>"
