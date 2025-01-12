import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")  # 從環境變量加載，默認值為 "default_secret_key"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.abspath('db_project.db')}"  # SQLite 文件路徑
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = 'static/images'  # 指定上傳目錄
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大上傳文件大小為 16 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # 支持的文件格式