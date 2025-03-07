from flask_login import login_user, logout_user, current_user, login_required, abort
from flask import render_template, flash, redirect, url_for, request
from app.models import User, Product, Category, Cart, Order
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, ProductForm, CategoryForm
from app import app, db

@app.route('/')
@app.route('/index')
@login_required
def index():
    '''show the home page which displys :
    - all categories
        - all products within each category
    '''
    categories = Category.query.all()
    #products = Product.query.all()
    return render_template('index.html', title='Home', categories=categories, products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''login a user'''
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        
        # redirect to the admin page if the user is an admin
        if user.is_admin:
            return redirect(url_for('admin'))
        
        # redirect to the next page if it exists
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    '''logout a user'''
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    '''register a new user'''
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/product/<product_id>')
@login_required
def product(product_id):
    '''show a product in detail'''
    product = Product.query.get(product_id)
    return render_template('product.html', title=product.name, product=product)

#ADMIN ROUTE
@app.route('/new-product')
@login_required
def new_product():
    '''create a new product'''
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data, description=form.description.data, price=form.price.data, category_id=form.category.data)
        db.session.add(product)
        db.session.commit()
        flash('Product added!')
        return redirect(url_for('index'))
    return render_template('new_product.html', title='New Product', form=form)

@app.route('/category/<category_id>')
@login_required
def category(category_id):
    '''show all products in a category'''
    category = Category.query.get(category_id)
    products = Product.query.filter_by(category_id=category_id).all()
    return render_template('category.html', title=category.name, category=category, products=products)

#ADMIN ROUTE
@app.route('/new-category')
@login_required
def new_category():
    '''create a new category'''
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, description=form.description.data)
        db.session.add(category)
        db.session.commit()
        flash('Category added!')
        return redirect(url_for('index'))
    return render_template('new_category.html', title='New Category', form=form)

@app.route('/add-to-cart/<product_id>')
@login_required
def add_to_cart(product_id):
    '''add a product to a cart'''
    cart = Cart(user_id=current_user.id, product_id=product_id, quantity=1)
    db.session.add(cart)
    db.session.commit()
    flash('Product added to cart!')
    return redirect(url_for('index'))

@app.route('/remove-from-cart/<cart_id>')
@login_required
def remove_from_cart(cart_id):
    '''remove a product from a cart'''
    cart = Cart.query.get(cart_id)
    db.session.delete(cart)
    db.session.commit()
    flash('Product removed from cart!')
    return redirect(url_for('cart'))

@app.route('/my-cart')
@login_required
def cart():
    '''view and optionally checkout all my pending cart items'''
    carts = Cart.query.filter_by(user_id=current_user.id).all()
    total = 0
    for cart in carts:
        total += cart.product.price * cart.quantity
        # besides totl in the HTML, add a confirm button which sends an M-Pesa request to the user
        # then update the cart to an order by creating an order object and storing the transaction details
    return render_template('cart.html', title='cart', carts=carts, total=total)

@app.route('/admin')
@login_required
def admin():
    '''show admin dashboard'''
    if not current_user.is_admin:
        abort(403)
        return
        #return redirect(url_for('index'))
    return render_template('admin.html')

@app.route('/new-admin', methods=['GET', 'POST'])
def new_admin():
    '''create a new admin'''
    # find a way to limit to only 1 admin
    # Check if there is already an admin
    existing_admin = User.query.filter_by(is_admin=True).first()
    if existing_admin:
        flash('An admin already exists. Only one admin is allowed.')
        return redirect(url_for('login'))

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, is_admin=True)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now an admin!')
        return redirect(url_for('admin'))
    return render_template('Register.html', title='New-admin', form=form)

@app.route('/checkout')
@login_required
def checkout():
    '''checkout all items in a cart'''
    # M-Pesa integration
    #***************************************************************************************************************************
    # retrieve transaction details then include them in the order objects below
    carts = Cart.query.filter_by(user_id=current_user.id).all()
    for cart in carts:
        order = Order(user_id=current_user.id, product_id=cart.product_id, quantity=cart.quantity, total=cart.product.price * cart.quantity)
        db.session.add(order)
        db.session.delete(cart)
    db.session.commit()
    flash('Checkout successful!')
    #return redirect(url_for('index'))
    return render_template('checkout.html')