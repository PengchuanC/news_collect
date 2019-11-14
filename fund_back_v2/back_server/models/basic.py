from back_server.models import Model, db


class BasicInfo(db.Model, Model):
    __tablename__ = "t_ff_basic_info"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    windcode = db.Column(db.String(10), db.ForeignKey('t_ff_funds.windcode'), nullable=False, index=True)
    sec_name = db.Column(db.String(10), nullable=False)
    fullname = db.Column(db.String(30), name="fund_fullname")
    setup_date = db.Column(db.DateTime, name="fund_setupdate")
    benchmark = db.Column(db.String(100), name="fund_benchmark")
    company = db.Column(db.String(20), name="fund_fundmanagementcompany")
    invest_scope = db.Column(db.Text, name="fund_investscope")
    structured = db.Column(db.String(2), name="fund_structuredfundornot")
    first_invest_type = db.Column(db.String(25), name="fund_firstinvesttype")
    invest_type = db.Column(db.String(25), name="fund_investtype")
    update_date = db.Column(db.DateTime, nullable=False, index=True)

    funds = db.relationship("Funds", backref="basic_info")

    def __repr__(self):
        return f"<BasicInfo {self.windcode}>"
