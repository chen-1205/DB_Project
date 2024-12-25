from app import create_app
from app.models import Product, db

# 創建 Flask 應用
app = create_app()

# 商品資料
products = [
    {"name": "A", "price": 10, "stock": 5, "image_url": "https://imgur.com/a/71yZkPn"},
    {"name": "B", "price": 15, "stock": 5, "image_url": "https://imgur.com/a/qDFalik"},
    {"name": "C", "price": 12, "stock": 5, "image_url": "https://imgur.com/a/k3ceg8F"},
    {"name": "D", "price": 14, "stock": 5, "image_url": "https://imgur.com/a/iGe2cGe"},
    {"name": "E", "price": 13, "stock": 5, "image_url": "https://imgur.com/a/wsIyuSP"},
]

# 進入應用上下文
with app.app_context():
    for product in products:
        new_product = Product(
            name=product["name"],
            price=product["price"],
            stock=product["stock"],
            image_url=product["image_url"],
        )
        db.session.add(new_product)
    
    db.session.commit()
    print("商品資料已成功加入資料庫！")