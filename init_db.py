from app import app, db, Product, Customer
from datetime import date

# 预设商品
products = [
    {'name': '玻璃隔断', 'default_price': 210, 'unit': '平米'},
    {'name': '电动门', 'default_price': 0, 'unit': '套'},
    {'name': '木门', 'default_price': 450, 'unit': '扇'},
    {'name': '地弹门', 'default_price': 1600, 'unit': '套'},
    {'name': '门禁机', 'default_price': 900, 'unit': '套'},
]

# 预设客户
customers = [
    {'name': '邵辉', 'contact': ''},
    {'name': '小黄', 'contact': ''},
    {'name': '顺泽', 'contact': ''},
    {'name': '誉安冯志伟', 'contact': ''},
]

with app.app_context():
    db.create_all()
    print('数据库表创建完成')
    
    # 添加预设商品
    for p in products:
        if not Product.query.filter_by(name=p['name']).first():
            product = Product(name=p['name'], default_price=p['default_price'], unit=p['unit'])
            db.session.add(product)
    print('商品预设完成')
    
    # 添加预设客户
    for c in customers:
        if not Customer.query.filter_by(name=c['name']).first():
            customer = Customer(name=c['name'], contact=c['contact'])
            db.session.add(customer)
    print('客户预设完成')
    
    db.session.commit()
    print('初始化完成！')
    print(f"商品数：{Product.query.count()}")
    print(f"客户数：{Customer.query.count()}")
