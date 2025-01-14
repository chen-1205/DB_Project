import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, session, flash, redirect, url_for, abort, current_app
from .models import Product, User, Order, CartItem,OrderItem, db # 確保導入 Product 模型
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


main = Blueprint('main', __name__)

@main.route('/')
def index():
    # 獲取所有商品
    products = Product.query.all()
    return render_template('index.html', products=products)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('註冊成功！請登入。')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['is_admin'] = user.is_admin
            if user.is_admin:  # 檢查是否是管理員
                return redirect(url_for('main.admin_dashboard'))  # 導向管理員儀表板

            else:
                return redirect(url_for('main.index'))  # 導向普通用戶首頁
        else:
            flash('登入失敗，請檢查電子郵件和密碼。')
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.clear()
    flash('已登出！')
    return redirect(url_for('main.index'))

@main.route('/cart', methods=['GET'])
def cart():
    if 'user_id' not in session:
        flash('請先登入！')
        return redirect(url_for('main.login'))
    cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@main.route('/update_cart_item/<int:cart_item_id>', methods=['POST'])
def update_cart_item(cart_item_id):
    if 'user_id' not in session:
        flash('請先登入！')
        return redirect(url_for('main.login'))

    cart_item = CartItem.query.get_or_404(cart_item_id)
    new_quantity = int(request.form['quantity'])

    # 確保新的購物車數量不超過商品庫存
    if new_quantity > cart_item.product.stock:
        flash(f'商品 "{cart_item.product.name}" 的庫存不足，請減少購買數量！', 'error')
        return redirect(url_for('main.cart'))

    if new_quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = new_quantity
    db.session.commit()
    flash('購物車已更新！')
    return redirect(url_for('main.cart'))

@main.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash('請先登入！')
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    product = Product.query.get_or_404(product_id)

    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=1)
        db.session.add(cart_item)
    
    db.session.commit()
    flash(f'Added {product.name} to your cart.')
    return redirect(url_for('main.index'))

@main.route('/remove_from_cart/<int:cart_item_id>', methods=['POST'])
def remove_from_cart(cart_item_id):
    if 'user_id' not in session:
        flash('請先登入！')
        return redirect(url_for('main.login'))
    
    cart_item = CartItem.query.get_or_404(cart_item_id)
    db.session.delete(cart_item)
    db.session.commit()
    flash('商品已從購物車移除！')
    return redirect(url_for('main.cart'))

@main.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        flash('請先登入！')
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    
    if not cart_items:
        flash('購物車是空的！')
        return redirect(url_for('main.index'))

    for item in cart_items:
        if item.quantity > item.product.stock:
            flash(f'商品 "{item.product.name}" 的庫存不足！請調整購物車數量。', 'error')
            print(f"庫存不足檢查: {item.product.name} - 購買量: {item.quantity}, 庫存: {item.product.stock}")
            return redirect(url_for('main.cart'))

    # 接收收件人訊息
    recipient_name = request.form['recipient_name']
    recipient_address = request.form['recipient_address']
    recipient_phone = request.form['recipient_phone']

    # 創建新訂單
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    new_order = Order(
        user_id=user_id,
        total_price=total_price,
        status='待處理',
        recipient_name=recipient_name,
        recipient_address=recipient_address,
        recipient_phone=recipient_phone
    )
    db.session.add(new_order)
    db.session.commit()

    # 添加訂單項目並更新庫存
    for item in cart_items:
        # 減少庫存
        item.product.stock -= item.quantity
        # 如果庫存變為負數，回滾數據庫操作並提示錯誤
        if item.product.stock < 0:
            db.session.rollback()
            flash(f'商品 "{item.product.name}" 的庫存不足，訂單未成功提交！', 'error')
            return redirect(url_for('main.cart'))

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product.id,
            product_name=item.product.name,
            quantity=item.quantity,
            price=item.product.price
        )
        db.session.add(order_item)
        db.session.delete(item)

    db.session.commit()

    flash('訂單已成功提交！')
    return redirect(url_for('main.orders'))

@main.route('/checkout_page', methods=['GET'])
def checkout_page():
    if 'user_id' not in session:
        flash('請先登入！')
        return redirect(url_for('main.login'))
    
    # 渲染 checkout.html
    return render_template('checkout.html')

@main.route('/orders', methods=['GET'])
def orders():
    if 'user_id' not in session:
        flash('請先登入！')
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    user_orders = Order.query.filter_by(user_id=user_id).all()

    return render_template('orders.html', orders=user_orders)


@main.route('/order/<int:order_id>', methods=['GET'])
def order_detail(order_id):
    # 從資料庫查找訂單
    order = Order.query.get_or_404(order_id)
    if 'user_id' not in session or session['user_id'] != order.user_id:
        flash("無權查看此訂單！")
        return redirect(url_for('main.orders'))

    return render_template('order_detail.html', order=order)



@main.route('/admin/orders', methods=['GET', 'POST'])
def admin_orders():
    if not session.get('is_admin', False):
        flash('需要管理員權限！')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        order_id = int(request.form['order_id'])
        new_status = request.form['status']
        order = Order.query.get_or_404(order_id)
        order.status = new_status
        db.session.commit()
        flash(f'訂單狀態已更新為 {new_status}！')

    orders = Order.query.all()
    return render_template('admin_orders.html', orders=orders)


@main.route('/order/<int:order_id>', methods=['GET'])
def order_details(order_id):
    if 'user_id' not in session:
        flash('請先登錄！')
        return redirect(url_for('main.login'))

    order = Order.query.get_or_404(order_id)
    if 'user_id' not in session or session['user_id'] != order.user_id:
        flash('您無權查看此訂單！')
        return redirect(url_for('main.orders'))

    return render_template('order_detail.html', order=order)


@main.route('/admin')
def admin_dashboard():
    if not session.get('is_admin', False):
        return redirect(url_for('main.login'))
    return render_template('admin_dashboard.html')

@main.route('/admin/users', methods=['GET', 'POST'])
def list_users():
    if request.method == 'POST':
        pass
    
    users = User.query.filter(User.is_admin == 0)
    return render_template('admin/users.html', users=users)

@main.route('/admin/delete_users/<int:user_id>', methods=['POST'])
def delete_users(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('使用者不存在', 'error')
        return redirect(url_for('main.list_users'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'使用者 {user.name} 已刪除', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'刪除失敗，原因: {str(e)}', 'error')

    return redirect(url_for('main.list_users'))

@main.route('/admin/orders/<int:order_id>', methods=['GET'])
def admin_order_details(order_id):
    if not session.get('is_admin', False):
        flash('需要管理員權限！')
        return redirect(url_for('main.login'))

    order = Order.query.get_or_404(order_id)
    return render_template('admin/admin_order_detail.html', order=order)

@main.route('/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    # 從表單中獲取新的訂單狀態
    new_status = request.form.get('status')
    if not new_status:
        flash('請選擇訂單狀態', 'error')
        return redirect(url_for('main.admin_orders', order_id=order_id))

    # 更新數據庫中的訂單狀態
    order = Order.query.get(order_id)
    if order:
        order.status = new_status
        db.session.commit()
        flash('訂單狀態已更新', 'success')
    else:
        flash('找不到該訂單', 'error')

    return redirect(url_for('main.admin_orders', order_id=order_id))


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/admin/products', methods=['GET', 'POST'])
def admin_products():
    if request.method == 'POST':
        name = request.form['name']
        price = int(request.form['price'])
        stock = int(request.form['stock'])
        image_url = request.form['image_url']  

        new_product = Product(name=name, price=price, stock=stock, image_url=image_url)
        db.session.add(new_product)
        db.session.commit()

        flash('商品新增成功！', 'success')
        return redirect(url_for('main.admin_products'))

    products = Product.query.all()
    return render_template('admin_products.html', products=products)

@main.route('/admin/upload_product_with_image', methods=['POST'])
def upload_product_with_image():
    import uuid

    # 獲取表單資料
    name = request.form.get('name')
    price = request.form.get('price')
    stock = request.form.get('stock')
    image_name = request.form.get('image_name')  # 用戶輸入的圖片名稱
    file = request.files.get('image')

    # 驗證必填欄位
    if not name or not price or not stock or not image_name or not file:
        flash('所有欄位均為必填項！', 'error')
        return redirect(url_for('main.admin_products'))

    # 檢查圖片檔案是否合法
    if file and allowed_file(file.filename):
        # 為檔案名稱添加副檔名
        extension = os.path.splitext(file.filename)[1].lower()  # 獲取副檔名並轉為小寫
        
        # 使用用戶輸入的圖片名稱和副檔名生成檔案名稱
        filename = f"{image_name}{extension}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # 確保目錄存在
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)

        # 儲存圖片檔案
        file.save(file_path)
    else:
        flash('圖片檔案格式不支援！', 'error')
        return redirect(url_for('main.admin_products'))

    # 新增商品到資料庫
    new_product = Product(
        name=name,
        price=int(price),
        stock=int(stock),
        image_url=filename  # 資料庫中儲存檔案名稱
    )
    db.session.add(new_product)
    db.session.commit()

    flash(f'商品 "{name}" 新增成功，圖片 "{filename}" 已上傳！', 'success')
    return redirect(url_for('main.admin_products'))



# 刪除商品
@main.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('商品已刪除！', 'success')
    return redirect(url_for('main.admin_products'))

# 更新商品
@main.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.price = float(request.form['price'])
        product.stock = int(request.form['stock'])
        product.image_url = request.form['image_url']

        db.session.commit()
        flash('商品已更新！', 'success')
        return redirect(url_for('main.admin_products'))

    return render_template('edit_product.html', product=product)