import warnings

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_cache import Cache
from flask_babelex import Babel

from back_server.config import config


warnings.filterwarnings("ignore")
db = SQLAlchemy()
cache = Cache(with_jinja2_ext=False)
babel = Babel()


def create_app(config_name):
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    cache.init_app(app)

    from back_server.routes.admin import admin
    admin.init_app(app)
    babel.init_app(app)

    app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'

    from .routes import main
    app.register_blueprint(main)

    from .routes.v1 import rest
    app.register_blueprint(rest, url_prefix="/api/v1")

    return app
