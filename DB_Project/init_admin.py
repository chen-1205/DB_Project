from app.models import User
from werkzeug.security import generate_password_hash
from app import db

def initialize_admin():
    existing_admin = User.query.filter_by(email="admin@gmail.com").first()
    if existing_admin:
        print("管理員帳戶已存在！")
    else:
        admin_user = User(
            name="Admin",
            email="admin@gmail.com",
            password=generate_password_hash("admin123"),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("管理員帳戶已成功創建！")