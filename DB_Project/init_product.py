from app import db, create_app
from app.models import Product

def initialize_products():
    app = create_app()
    products = [
        {"name": "干貝鮑魚佛跳牆", "price": 350, "stock": 5, "image_url": "干貝鮑魚佛跳牆.jpg"},
        {"name": "脆皮豬腳", "price": 330, "stock": 5, "image_url": "脆皮豬腳.jpg"},
        {"name": "筍乾蹄膀", "price": 290, "stock": 5, "image_url": "筍乾蹄膀.jpg"},
        {"name": "黑蒜頭養生雞", "price": 380, "stock": 5, "image_url": "黑蒜頭養生雞.jpg"},
        {"name": "櫻花蝦米糕", "price": 170, "stock": 5, "image_url": "櫻花蝦米糕.jpg"},
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