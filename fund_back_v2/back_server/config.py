"""
flask项目基础配置文件
"""

import os


# 项目入口绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """base config"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret key'
    COMMIT_ON_TEARDOWN = True
    TRACK_MODIFICATIONS = True
    ADMIN = os.environ.get('FLASKY_ADMIN')
    DATABASE = ("USER", "PASSWORD", "HOST")
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):
    """运行环境配置"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql+pymysql://fund:123456@cdb-p3ccshwm.cd.tencentcdb.com:10053' \
                              '/fund_filter_production?charset=utf8mb4'


class DevelopmentConfig(Config):
    DATABASE = ('fund', "123456", "cdb-p3ccshwm.cd.tencentcdb.com:10053")
    user, password, host = DATABASE
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                   f"mysql+pymysql://{user}:{password}@{host}/fund_filter_production?charset=utf8mb4"
    DEBUG = True


config = {
    'testing': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
