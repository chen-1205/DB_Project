import os

class Config:
    SECRET_KEY = "your_secret_key"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.abspath('db_project.db')}"  # SQLite 文件路徑
    SQLALCHEMY_TRACK_MODIFICATIONS = False
