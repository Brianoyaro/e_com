from flask_login import login_user, logout_user, current_user, login_required
from flask import render_template, flash, redirect, url_for, request, abort, Blueprint
from app.models import User, Product, Category, Cart, Order, OrderItem, Transaction
from urllib.parse import urlparse as url_parse
from app.forms import LoginForm, RegistrationForm, ProductForm, CategoryForm, MpesaDetailsForm
from app import db
import os
import secrets
from PIL import Image
import requests

'''basedir = os.path.abspath(os.path.dirname(__file__))
image_folder = os.path.join(basedir, 'static')
#picture_path = os.path.join(image_folder, filename)'''


main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    '''show the home page which displys :
    - all categories
        - all products within each category
    '''
    categories = Category.query.all()
    #products = Product.query.all()
    return render_template('index.html', title='Home', categories=categories)

@main.route('/login', methods=['GET', 'POST'])
def login():
    '''login a user'''
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        
        # redirect to the admin page if the user is an admin
        if user.is_admin:
            return redirect(url_for('main.admin'))
        
        # redirect to the next page if it exists
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@main.route('/logout')
@login_required
def logout():
    '''logout a user'''
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    '''register a new user'''
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, is_admin=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user! You can now login.')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main.route('/product/<product_id>')
@login_required
def product(product_id):
    '''show a product in detail'''
    product = Product.query.get_or_404(product_id)
    # I think we can do better. We can allow the user to specify the quantity they want to buy and pass the data through a form rather than a query string.
    quantity = request.args.get('quantity', 1)
    print(quantity)
    return render_template('product.html', title=product.name, product=product, quantity=quantity)

def save_image(pic_data):
    """saves uploaded image"""
    _, fn_ext = os.path.splitext(pic_data.filename)
    random_hex = secrets.token_hex(8)
    filename = random_hex + fn_ext
    picture_path = os.path.join(main.root_path, 'static', filename)
    image_size = (125, 125)
    image = Image.open(pic_data)
    image.thumbnail(image_size)
    image.save(picture_path)
    return filename

#ADMIN ROUTE
@main.route('/product/new', methods=['GET', 'POST'])
@login_required
def new_product():
    '''create a new product'''
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data, description=form.description.data, price=form.price.data, category_id=form.category.data, quantity=form.quantity.data)
        if form.image.data:
            picture_file = save_image(form.image.data)
            product.image = picture_file

        db.session.add(product)
        db.session.commit()
        flash(f"{product.name} successfully added!")
        return redirect(url_for('main.index'))
    return render_template('new_product.html', title='New Product', form=form)

@main.route('/category/<category_id>')
@login_required
def category(category_id):
    '''show all products in a category'''
    category = Category.query.get(category_id)
    products = Product.query.filter_by(category_id=category_id).all()
    return render_template('category.html', title=category.name, category=category, products=products)

#ADMIN ROUTE
@main.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    '''create a new category'''
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, description=form.description.data)
        db.session.add(category)
        db.session.commit()
        flash('Category added!')
        return redirect(url_for('main.index'))
    return render_template('new_category.html', title='New Category', form=form)

@main.route('/cart/add/<product_id>', methods=['GET', 'POST'])
@login_required
def add_to_cart(product_id):
    '''add a product to a cart'''
    product = Product.query.get_or_404(product_id)
    quantity = request.form.get('quantity')
    existing_cart = Cart.query.filter_by(user_id=current_user.id, product=product).first()
    if existing_cart:
        existing_cart.quantity += int(quantity)
        db.session.commit()
        flash('Product added to cart!')
        return redirect(url_for('main.index'))
    # else create a new cart
    cart = Cart(user_id=current_user.id, product=product, quantity=quantity)
    db.session.add(cart)
    db.session.commit()
    flash('Product added to cart!')
    return redirect(url_for('main.index'))

@main.route('/cart/remove/<cart_id>')
@login_required
def remove_from_cart(cart_id):
    '''remove a product from a cart'''
    cart = Cart.query.get_or_404(cart_id)
    db.session.delete(cart)
    db.session.commit()
    flash('Product removed from cart!')
    return redirect(url_for('main.cart'))

@main.route('/my-cart')
@login_required
def cart():
    '''view and optionally checkout all my pending cart items'''
    carts = Cart.query.filter_by(user_id=current_user.id).all()
    total = 0
    for cart in carts:
        total += cart.product.price * cart.quantity
    return render_template('cart.html', title='My Cart', carts=carts, total=total)

@main.route('/admin')
@login_required
def admin():
    '''show admin dashboard'''
    if not current_user.is_admin:
        abort(403)
        return
        #return redirect(url_for('main.index'))
    return render_template('admin.html')

@main.route('/admin/new', methods=['GET', 'POST'])
def new_admin():
    '''create a new admin'''
    # find a way to limit to only 1 admin
    # Check if there is already an admin
    existing_admin = User.query.filter_by(is_admin=True).first()
    print(existing_admin)
    if existing_admin:
        flash('An admin already exists. Only one admin is allowed.')
        return redirect(url_for('main.login'))

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, is_admin=True)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now an admin!')
        return redirect(url_for('main.admin'))
    return render_template('register.html', title='New-admin', form=form)

# Hndle this later and last.
@main.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    '''checkout all items in a cart'''
    carts = Cart.query.filter_by(user_id=current_user.id).all()
    total = 0
    for cart in carts:
        total += cart.product.price * cart.quantity
    form = MpesaDetailsForm()
    if form.validate_on_submit():
        email = form.email.data
        phone_number = form.phone_number.data
        # send a request to M-Pesa
        base_url = 'https://0a14-102-222-145-50.ngrok-free.app' # change this place holder to the actual base url
        #response = requests.post(base_url + '/simulate', json={'email': email, 'phone_number': phone_number, 'amount': total})
        response = requests.get(base_url + '/simulate')
        
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(base_url + '/validate-stk', headers=headers)
        print(f"resp: {resp}")
        
        #resp = requests.get(base_url + '/validate-stk')
        # print(f"MPESA Response Status: {resp.status_code}")
        # print(f"MPESA Response Headers: {resp.headers}")
        print(f"MPESA Response Text: {resp.text}")  # Raw output


        data = resp.json()
        print(f"After MPESA->Data: {data} ")
        if data.get('message') == 'success':
            # send an email ticket to the user if transaction is successful
            #*************************************************************
            # create an order
            order = Order(user_id=current_user.id, total=total)
            db.session.add(order)
            db.session.commit() # because we need order.id in transaction below
            # create a transaction
            data = resp.get('data')
            amount=data[0].get('Value')
            mpesaReceiptNumber=data[1].get('Value')
            transactionDate=data[2].get('Value')
            phoneNumber=data[3].get('Value')
            transaction = Transaction(user_id=current_user.id, amount=amount, mpesaReceiptNumber=mpesaReceiptNumber, transactionDate=transactionDate, phoneNumber=phoneNumber, order_id=order.id)

            # link the order to the transaction
            order.transaction_id = transaction.id
            
            # create order items to link to our order i.e our order has a linked list of order_items
            for cart in carts:
                order_item = OrderItem(order_id=order.id, product_id=cart.product.id, quantity=cart.quantity, price=cart.product.price)
                db.session.add(order_item)
                # remove the cart
                db.session.delete(cart)          
            db.session.add(order)
            db.session.add(transaction)
            db.session.commit()
            flash('Transaction successful!')
            return redirect(url_for('main.index'))
        else:
            flash('Transaction failed. Please try again.')
            return redirect(url_for('main.checkout'))
    return render_template('checkout.html', title='Checkout', form=form)