from back_server import db


class Style(db.Model):
    __tablename__ = "t_ff_style"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    windcode = db.Column(db.String(12), index=True)
    small_value = db.Column(db.Float)
    small_growth = db.Column(db.Float)
    mid_value = db.Column(db.Float)
    mid_growth = db.Column(db.Float)
    large_value = db.Column(db.Float)
    large_growth = db.Column(db.Float)
    bond = db.Column(db.Float)
    value_date = db.Column(db.Date)
    freq = db.Column(db.String(2))

    def __repr__(self):
        return f"<Style {self.windcode}>"
