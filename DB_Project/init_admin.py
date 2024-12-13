from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

# 創建 Flask 應用
app = create_app()

# 進入應用上下文
with app.app_context():
    # 檢查是否已存在管理員
    existing_admin = User.query.filter_by(email="admin@example.com").first()
    if existing_admin:
        print("管理員帳戶已存在！")
    else:
        # 創建管理員帳戶
        admin_user = User(
            name="Admin",
            email="admin@example.com",
            password=generate_password_hash("admin123"),  # 設定默認密碼
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("管理員帳戶已成功創建！")