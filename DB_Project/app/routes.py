from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from app.models import User, Product, CartItem, Order, OrderItem

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

# GET=取得表單
# POST=接收表單資料


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        new_user = User(
            name=name, 
            email=email,   
            password=hashed_password
        )
        db.session.add(new_user) #新增用戶
        db.session.commit()
        flash('註冊成功！請登錄。')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
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
            return redirect(url_for('index'))
        else:
            flash('登錄失敗，請檢查電子郵件和密碼。')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('已登出！')
    return redirect(url_for('index'))

# 購物車
@app.route('/cart', methods=['GET'])
def cart():
    if 'user_id' not in session:
        flash('請先登錄！')
        return redirect(url_for('login'))
    cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
    total_price = sum(item.product.ptice * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items)

# 新增到購物車
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash('請先登錄！')
        return redirect(url_for('login'))

    user_id = session['user_id']
    product = Product.query.getor404(product_id)

    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=1)
        db.session.add(cart_item)
    
    db.session.commit()
    flash(f'Added {product.name} to your cart.')
    return redirect(url_for('index'))

# 從購物車移除
@app.route('/remove_from_cart/<int:cart_item_id>', method=['POST'])
def remove_from_cart(cart_item_id):
    if 'user_id' not in session:
        flash('請先登錄！')
        return redirect(url_for('login'))
    
    cart_item = CartItem.query.get_or_404(cart_item_id)
    db.session.delete(cart_item)
    db.session.commit()
    flash('商品已從購物車移除！')
    return redirect(url_for('cart'))

@app.route('/checkout', method=['POST'])
def checkout():
    if 'user_id' not in session:
        flash('請先登錄！')
        return redirect(url_for('login'))

    user_id = session['user_id']
    cart_item = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_item:
        flash('購物車是空的！')
        return redirect(url_for('index'))

    total_price = sum(item.product.price * item.quantity for item in cart_item)
    new_order = Order(
        user_id=user_id, 
        total_price=total_price,
        status='待處理'
    )
    db.session.add(new_order)
    db.session.commit()

    for item in cart_item:
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
    return redirect(url_for('orders'))

@app.route('/orders', method=['GET'])
def orders():
    if 'user_id' not in session:
        flash('請先登錄！')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    orders = Order.query.filter_by(user_id=user_id).all()
    return render_template('orders.html', orders=orders)

