from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from .models import Product, User, Order, CartItem,OrderItem, db # 確保導入 Product 模型
from werkzeug.security import check_password_hash, generate_password_hash


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
        flash('註冊成功！請登錄。')
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
            flash('登錄成功！')
            return redirect(url_for('main.index'))
        else:
            flash('登錄失敗，請檢查電子郵件和密碼。')
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.clear()
    flash('已登出！')
    return redirect(url_for('main.index'))

@main.route('/cart', methods=['GET'])
def cart():
    if 'user_id' not in session:
        flash('請先登錄！')
        return redirect(url_for('main.login'))
    cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@main.route('/update_cart_item/<int:cart_item_id>', methods=['POST'])
def update_cart_item(cart_item_id):
    if 'user_id' not in session:
        flash('請先登錄！')
        return redirect(url_for('main.login'))

    cart_item = CartItem.query.get_or_404(cart_item_id)
    new_quantity = int(request.form['quantity'])
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
        flash('請先登錄！')
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
        flash('請先登錄！')
        return redirect(url_for('main.login'))
    
    cart_item = CartItem.query.get_or_404(cart_item_id)
    db.session.delete(cart_item)
    db.session.commit()
    flash('商品已從購物車移除！')
    return redirect(url_for('main.cart'))

@main.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        flash('請先登錄！')
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        flash('購物車是空的！')
        return redirect(url_for('main.index'))

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    new_order = Order(user_id=user_id, total_price=total_price, status='待處理')
    db.session.add(new_order)
    db.session.commit()

    for item in cart_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product.id,
            product_name=item.product.name,
            quantity=item.quantity,
            price=item.product.price
        )
        db.session.add(order_item)

        item.product.stock -= item.quantity
        db.session.delete(item)   

    db.session.commit()

    flash('訂單成立！')
    return redirect(url_for('main.orders'))

@main.route('/orders', methods=['GET'])
def orders():
    if 'user_id' not in session:
        flash('請先登錄！')
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    orders = Order.query.filter_by(user_id=user_id).all()
    return render_template('orders.html', orders=orders)

#########################################################

@main.route('/admin/products', methods=['GET', 'POST'])
def admin_products():
    if not session.get('is_admin', False):
        flash('需要管理員權限！')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # 新增商品
        name = request.form['name']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        image_url = request.form['image_url']
        new_product = Product(name=name, price=price, stock=stock, image_url=image_url)
        db.session.add(new_product)
        db.session.commit()
        flash('商品已新增！')
        return redirect(url_for('main.admin_products'))

    products = Product.query.all()
    return render_template('admin_products.html', products=products)


@main.route('/admin/edit_product/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    if not session.get('is_admin', False):
        flash('需要管理員權限！')
        return redirect(url_for('main.index'))

    product = Product.query.get_or_404(product_id)
    product.name = request.form['name']
    product.price = float(request.form['price'])
    product.stock = int(request.form['stock'])
    product.image_url = request.form['image_url']
    db.session.commit()

    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('商品已刪除！')
    return redirect(url_for('main.admin_products'))

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

@main.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    min_price = request.args.get('min_price', type=float, default=0)
    max_price = request.args.get('max_price', type=float, default=float('inf'))
    products = Product.query.filter(
        Product.name.ilike(f'%{query}%'),
        Product.price >= min_price,
        Product.price <= max_price
    ).all()
    return render_template('index.html', products=products)

@main.route('/order/<int:order_id>', methods=['GET'])
def order_details(order_id):
    if 'user_id' not in session:
        flash('請先登錄！')
        return redirect(url_for('main.login'))

    order = Order.query.get_or_404(order_id)
    if order.user_id != session['user_id'] and not session.get('is_admin', False):
        flash('您無權查看此訂單！')
        return redirect(url_for('main.orders'))

    return render_template('order_details.html', order=order)
    flash('商品已更新！')
    return redirect(url_for('main.admin_products'))

@main.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('is_admin', False):
        flash('需要管理員權限！')
        return redirect(url_for('main.index'))






