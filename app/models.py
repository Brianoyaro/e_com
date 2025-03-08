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


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(120), index=True)
    price = db.Column(db.Float)
    #stock = db.Column(db.Integer)
    #image = db.Column(db.String(120), index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    # Add a back-reference to Cart
    carts = db.relationship("Cart", back_populates="product")

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quantity = db.Column(db.Integer)
    
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product', back_populates='carts')
    
    def __repr__(self):
        return '<Cart {}>'.format(self.id)
    
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    total = db.Column(db.Float)
    #transaction_id = db.Column(db.String(120), index=True)

    def __repr__(self):
        return '<Order {}>'.format(self.id)
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))