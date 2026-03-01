import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from dotenv import load_dotenv
from extensions import db, bcrypt
from models import User, Product, Bill, BillItem
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def create_default_admin():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            user = User(username='admin', password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()

@app.before_request
def check_login():
    protected_endpoints = ['manager', 'billing', 'api_add_product', 'api_edit_product', 'api_delete_product', 'api_create_bill', 'invoice']
    if request.endpoint in protected_endpoints and 'admin_id' not in session:
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Unauthorized'}), 401
        return redirect(url_for('login'))

@app.route('/')
def index():
    if 'admin_id' in session:
        return redirect(url_for('billing'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            session['admin_id'] = user.id
            flash('Logged in successfully.', 'success')
            return redirect(url_for('billing'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_id', None)
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/manager')
def manager():
    products = Product.query.order_by(Product.id.desc()).all()
    low_stock_products = Product.query.filter(Product.stock < 10).all()
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    # Use string matching for sqlite compatibility just in case, but we are on postgres.
    # We can fetch all and filter in python for today for simplicity since it's a demo.
    all_bills = Bill.query.all()
    sales_today = sum(b.total_amount for b in all_bills if b.timestamp.strftime('%Y-%m-%d') == today_str)
    
    return render_template('manager.html', products=products, low_stock=low_stock_products, sales_today=sales_today)

@app.route('/billing')
def billing():
    return render_template('billing.html')

@app.route('/api/product', methods=['POST'])
def api_add_product():
    data = request.json
    try:
        new_prod = Product(
            barcode=data.get('barcode'),
            name=data.get('name'),
            category=data.get('category'),
            price_type=data.get('price_type'),
            price=float(data.get('price')),
            gst_percent=float(data.get('gst_percent', 0)),
            stock=float(data.get('stock', 0))
        )
        db.session.add(new_prod)
        db.session.commit()
        return jsonify({'success': True, 'id': new_prod.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/product/<int:prod_id>', methods=['PUT', 'DELETE'])
def api_edit_delete_product(prod_id):
    prod = Product.query.get_or_404(prod_id)
    if request.method == 'DELETE':
        db.session.delete(prod)
        db.session.commit()
        return jsonify({'success': True})
    
    # PUT
    data = request.json
    try:
        if 'barcode' in data: prod.barcode = data['barcode']
        if 'name' in data: prod.name = data['name']
        if 'category' in data: prod.category = data['category']
        if 'price_type' in data: prod.price_type = data['price_type']
        if 'price' in data: prod.price = float(data['price'])
        if 'gst_percent' in data: prod.gst_percent = float(data['gst_percent'])
        if 'stock' in data: prod.stock = float(data['stock'])
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/product/find')
def api_find_product():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'error': 'Empty query'}), 400
    
    prod = Product.query.filter_by(barcode=q).first()
    if not prod and q.isdigit():
        prod = Product.query.get(int(q))
        
    if prod:
        return jsonify({
            'success': True,
            'id': prod.id,
            'name': prod.name,
            'price': prod.price,
            'price_type': prod.price_type,
            'gst_percent': prod.gst_percent,
            'stock': prod.stock
        })
    return jsonify({'success': False, 'error': 'Product not found'}), 404

@app.route('/api/bill', methods=['POST'])
def api_create_bill():
    data = request.json
    items = data.get('items', [])
    payment_method = data.get('payment_method', 'cash')
    discount = float(data.get('discount', 0.0))
    
    if not items:
        return jsonify({'error': 'No items in bill'}), 400
        
    total_amount = 0.0
    bill_items = []
    
    try:
        bill = Bill(payment_method=payment_method, discount=discount, total_amount=0.0)
        db.session.add(bill)
        db.session.flush() # to get bill.id
        
        for item in items:
            prod = Product.query.get(item['product_id'])
            if not prod:
                raise Exception(f"Product ID {item['product_id']} not found")
                
            qty = float(item['quantity'])
            
            # Reduce stock
            prod.stock -= qty
            
            subtotal = prod.price * qty
            gst = subtotal * (prod.gst_percent / 100.0)
            item_total = subtotal + gst
            total_amount += item_total
            
            bill_item = BillItem(
                bill_id=bill.id,
                product_id=prod.id,
                quantity=qty,
                price_at_time=prod.price,
                gst_at_time=prod.gst_percent
            )
            db.session.add(bill_item)
            
        bill.total_amount = total_amount - discount
        db.session.commit()
        return jsonify({'success': True, 'bill_id': bill.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/invoice/<int:bill_id>')
def invoice(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    return render_template('invoice.html', bill=bill, datetime_now=datetime.utcnow())

if __name__ == '__main__':
    create_default_admin()
    app.run(debug=True, port=5000)
