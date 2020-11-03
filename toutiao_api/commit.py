from sqlalchemy.exc import IntegrityError
from apscheduler.schedulers.blocking import BlockingScheduler

from eastmoney import east_money

from model import News, base


schedule = BlockingScheduler()


def commit(data, user, password):
    session = News.connector(user, password)()
    for d in data:
        try:
            session.add(d)
            session.commit()
        except IntegrityError:
            session.rollback()
        except Exception as e:
            print(type(e))
    session.close()


def main():
    schedule.add_job(commit, "interval", hours=1, args=[east_money(), "fund", "123456"])
    schedule.start()


if __name__ == '__main__':
    # base.metadata.create_all(News.engine('fund', '123456'))
    main()
