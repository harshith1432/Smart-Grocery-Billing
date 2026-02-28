from extensions import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50), unique=True, nullable=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    price_type = db.Column(db.String(20), nullable=False) # 'item', 'kg', 'g'
    price = db.Column(db.Float, nullable=False)
    gst_percent = db.Column(db.Float, nullable=False, default=0.0)
    stock = db.Column(db.Float, nullable=False, default=0.0)

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False) # 'cash', 'card', 'upi'
    discount = db.Column(db.Float, default=0.0)
    
    items = db.relationship('BillItem', backref='bill', lazy=True, cascade="all, delete-orphan")

class BillItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price_at_time = db.Column(db.Float, nullable=False)
    gst_at_time = db.Column(db.Float, nullable=False)

    product = db.relationship('Product')
