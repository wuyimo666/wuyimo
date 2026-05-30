from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import pandas as pd
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

# 初始化LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 数据库模型
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(50))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    default_price = db.Column(db.Float, default=0)
    unit = db.Column(db.String(20), default='项')

class Purchase(db.Model):
    __tablename__ = 'purchase'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Float, default=1)
    unit_price = db.Column(db.Float)
    total_amount = db.Column(db.Float)
    record_date = db.Column(db.Date, default=date.today)
    note = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now())
    customer = db.relationship('Customer', backref='purchases')
    product = db.relationship('Product', backref='purchases')

class Sale(db.Model):
    __tablename__ = 'sale'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Float, default=1)
    unit_price = db.Column(db.Float)
    total_amount = db.Column(db.Float)
    record_date = db.Column(db.Date, default=date.today)
    note = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now())
    customer = db.relationship('Customer', backref='sales')
    product = db.relationship('Product', backref='sales')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 路由
@app.route('/')
@login_required
def index():
    # 今日数据
    today = date.today()
    purchase_today = Purchase.query.filter(Purchase.record_date == today).with_entities(db.func.sum(Purchase.total_amount)).scalar() or 0
    sale_today = Sale.query.filter(Sale.record_date == today).with_entities(db.func.sum(Sale.total_amount)).scalar() or 0
    
    # 客户欠款
    customers = Customer.query.all()
    debts = []
    for c in customers:
        total_purchase = Purchase.query.filter(Purchase.customer_id == c.id).with_entities(db.func.sum(Purchase.total_amount)).scalar() or 0
        total_sale = Sale.query.filter(Sale.customer_id == c.id).with_entities(db.func.sum(Sale.total_amount)).scalar() or 0
        debt = total_purchase - total_sale
        if debt != 0:
            debts.append({'name': c.name, 'debt': debt})
    
    return render_template('index.html', purchase_today=purchase_today, sale_today=sale_today, debts=debts[:5])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html', error='用户名或密码错误')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/purchase', methods=['GET', 'POST'])
@login_required
def purchase():
    customers = Customer.query.all()
    products = Product.query.all()
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        product_id = request.form.get('product_id')
        quantity = float(request.form.get('quantity', 1))
        unit_price = float(request.form.get('unit_price', 0))
        total = quantity * unit_price
        record_date = request.form.get('record_date') or date.today()
        note = request.form.get('note', '')
        
        p = Purchase(customer_id=customer_id, product_id=product_id, quantity=quantity, 
                     unit_price=unit_price, total_amount=total, record_date=record_date, note=note)
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('purchase'))
    
    records = Purchase.query.order_by(Purchase.record_date.desc()).all()
    return render_template('purchase.html', customers=customers, products=products, records=records)

@app.route('/sale', methods=['GET', 'POST'])
@login_required
def sale():
    customers = Customer.query.all()
    products = Product.query.all()
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        product_id = request.form.get('product_id')
        quantity = float(request.form.get('quantity', 1))
        unit_price = float(request.form.get('unit_price', 0))
        total = quantity * unit_price
        record_date = request.form.get('record_date') or date.today()
        note = request.form.get('note', '')
        
        s = Sale(customer_id=customer_id, product_id=product_id, quantity=quantity,
                  unit_price=unit_price, total_amount=total, record_date=record_date, note=note)
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('sale'))
    
    records = Sale.query.order_by(Sale.record_date.desc()).all()
    return render_template('sale.html', customers=customers, products=products, records=records)

@app.route('/customers')
@login_required
def customers():
    customers = Customer.query.all()
    result = []
    for c in customers:
        total_purchase = Purchase.query.filter(Purchase.customer_id == c.id).with_entities(db.func.sum(Purchase.total_amount)).scalar() or 0
        total_sale = Sale.query.filter(Sale.customer_id == c.id).with_entities(db.func.sum(Sale.total_amount)).scalar() or 0
        debt = total_purchase - total_sale
        result.append({'id': c.id, 'name': c.name, 'contact': c.contact, 'debt': debt})
    return render_template('customers.html', customers=result)

@app.route('/api/add_customer', methods=['POST'])
@login_required
def add_customer():
    data = request.get_json()
    c = Customer(name=data['name'], contact=data.get('contact', ''), address=data.get('address', ''))
    db.session.add(c)
    db.session.commit()
    return jsonify({'success': True, 'id': c.id})

@app.route('/reconciliation')
@login_required
def reconciliation():
    customer_id = request.args.get('customer_id')
    customers = Customer.query.all()
    
    if customer_id:
        customer = Customer.query.get(customer_id)
        purchases = Purchase.query.filter(Purchase.customer_id == customer_id).order_by(Purchase.record_date).all()
        sales = Sale.query.filter(Sale.customer_id == customer_id).order_by(Sale.record_date).all()
        total_purchase = sum(p.total_amount for p in purchases)
        total_sale = sum(s.total_amount for s in sales)
        debt = total_purchase - total_sale
        return render_template('reconciliation.html', 
                          customer=customer, 
                          purchases=purchases, 
                          sales=sales,
                          total_purchase=total_purchase,
                          total_sale=total_sale,
                          debt=debt,
                          customers=customers)
    
    return render_template('reconciliation.html', customers=customers)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 创建管理员账号
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', is_admin=True)
            admin.set_password('123456')
            db.session.add(admin)
            db.session.commit()
    app.run(host='0.0.0.0', port=5000, debug=True)
