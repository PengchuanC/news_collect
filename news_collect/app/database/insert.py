from app.database import connector


class Session(object):
    def __init__(self, user, password, host, port, db):
        self.engine = connector.engine(user, password, host, port, db)
        self.session = connector.session(self.engine)

    def insert_one(self, row):
        self.session.add(row)
        try:
            self.session.commit()
        except:
            self.session.rollback()

    def insert_all(self, rows):
        self.session.add_all(rows)
        try:
            self.session.commit()
        except:
            self.session.rollback()

    def close(self):
        self.session.close()