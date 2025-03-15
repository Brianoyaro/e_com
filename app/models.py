from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True) # remove unique=True later.
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    carts = db.relationship('Cart', backref='user', lazy='dynamic')
    

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(120), index=True)
    products = db.relationship('Product', backref='category', lazy='dynamic')


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(120), index=True)
    rating = db.Column(db.Integer)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    
    def __repr__(self):
        return '<Review {}>'.format(self.id)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(120), index=True)
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    in_stock = db.Column(db.Boolean, default=True)
    image = db.Column(db.String(120), index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    reviews = db.relationship('Review', backref='product', lazy='dynamic')
    carts = db.relationship("Cart", back_populates="product")

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quantity = db.Column(db.Integer)
    
    # Add a foreign link to the product incase we need to access the product details later.
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    
    # Add a back-reference to Product
    product = db.relationship("Product", back_populates="carts")
    
    def __repr__(self):
        return '<Cart {}>'.format(self.id)
    
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)  # Total price for the entire order
    transaction_id = db.Column(db.String(120), index=True, unique=True)

    # Relationship to OrderItem (products in the order)
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Order {self.id}>'


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Store price at purchase time

    def __repr__(self):
        return f'<OrderItem Order:{self.order_id}, Product:{self.product_id}>'
    
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Float)
    phone_number = db.Column(db.String(120), index=True)
    mpesaReceiptNumber = db.Column(db.String(120), index=True)
    transactionDate = db.Column(db.String(120), index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))

    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))