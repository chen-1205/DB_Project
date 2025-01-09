from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate

migrate = Migrate()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)

    # 註冊 Blueprint
    from .routes import main
    # from .api import api

    app.register_blueprint(main)
    # app.register_blueprint(api)

    return app
