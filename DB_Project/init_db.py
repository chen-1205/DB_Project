from app import create_app, db

# 創建 Flask 應用
app = create_app()

# 創建數據表
with app.app_context():
    db.create_all()
    print("數據庫和表已成功創建！")
