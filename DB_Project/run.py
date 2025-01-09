from app import create_app
from init_db import initialize_database
from init_product import initialize_products

app = create_app()

if __name__ == "__main__":
    print("初始化資料庫...")
    initialize_database()

    print("初始化商品數據...")
    initialize_products()

    print("啟動服務器...")
    app.run(debug=True)