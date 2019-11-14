from . import db, Model


class Classify(db.Model, Model):
    """
    create table if not exists `fund_classify`(
    `ID` int not null primary key auto_increment,
    `WINDCODE` char(10) not null,
    `BRANCH` char(10) not null,
    `CLASSIFY` char(20) not null,
    `UPDATE_DATE` datetime not null
    );
    """
    __tablename__ = 't_ff_classify'
    id = db.Column(db.Integer, primary_key=True)
    windcode = db.Column(db.String(10), db.ForeignKey("t_ff_funds.windcode"), nullable=False)
    branch = db.Column(db.String(10))
    classify = db.Column(db.String(20))
    update_date = db.Column(db.DATETIME)

    funds = db.relationship("Funds", backref="classify")

    def __repr__(self):
        return f"<Classify {self.windcode}>"
