from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)

    with app.app_context():
        # 延遲導入並註冊 Blueprint
        from .routes import main
        app.register_blueprint(main)

    return app
