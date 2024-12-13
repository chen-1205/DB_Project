from app import create_app, db

# 創建 Flask 應用
app = create_app()

# 設置應用上下文並初始化資料庫
with app.app_context():
    db.create_all()  # 創建資料表
    print("Database initialized successfully!")
