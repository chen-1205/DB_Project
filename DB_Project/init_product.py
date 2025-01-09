from app import db, create_app
from app.models import Product

def initialize_products():
    app = create_app()
    products = [
        {"name": "A", "price": 10, "stock": 5, "image_url": "https://imgur.com/a/71yZkPn"},
        {"name": "B", "price": 15, "stock": 5, "image_url": "https://imgur.com/a/qDFalik"},
        {"name": "C", "price": 12, "stock": 5, "image_url": "https://imgur.com/a/k3ceg8F"},
        {"name": "D", "price": 14, "stock": 5, "image_url": "https://imgur.com/a/iGe2cGe"},
        {"name": "E", "price": 13, "stock": 5, "image_url": "https://imgur.com/a/wsIyuSP"},
    ]
    with app.app_context():
        for product in products:
            if not Product.query.filter_by(name=product["name"]).first():
                new_product = Product(**product)
                db.session.add(new_product)
        db.session.commit()
        print("商品資料已成功加入資料庫！")

if __name__ == "__main__":
    initialize_products()