import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")  
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.abspath('db_project.db')}"  
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = 'DB_Project/app/static/images'  
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  
