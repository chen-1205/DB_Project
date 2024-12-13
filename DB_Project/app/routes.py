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

        new_user = User(name=name, email=email, password=hashed_password)
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