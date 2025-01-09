from app import create_app
from init_db import initialize_database
from init_product import initialize_products
from init_admin import initialize_admin

app = create_app()

if __name__ == "__main__":

    with app.app_context():
        print("初始化資料庫...")
        initialize_database()
        print("初始化商品數據...")
        initialize_products()
        initialize_admin()
        print("啟動服務器...")

    


    app.run(debug=True)