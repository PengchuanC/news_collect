import os
from flask_script import Manager
from flask_migrate import Migrate

from back_server import create_app, db


app = create_app(os.getenv("FLASK_CONFIG") or "default")
manager = Manager(app)
migrate = Migrate(app, db)


def main_shell_context():
    return dict(app=app, db=db)


if __name__ == '__main__':
    manager.run()
