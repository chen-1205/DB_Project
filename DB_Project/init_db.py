from app import db, create_app

def initialize_database():
    app = create_app()  
    with app.app_context():  
        db.create_all()  
        print("資料庫初始化完成！")

if __name__ == "__main__":
    initialize_database()