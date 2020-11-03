from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from transfer.config import local as database


def engine(user, password, host, port, db):
    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4"
    driver = create_engine(url)
    return driver


def session(driver):
    session_obj = sessionmaker(bind=driver)
    _session = session_obj()
    return _session


def default_session():
    driver = engine(**database)
    _session = session(driver)
    return _session
