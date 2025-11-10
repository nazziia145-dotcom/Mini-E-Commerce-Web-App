from flask import Flask, request, jsonify
from flask_cors import CORS
from config import DATABASE_URL
from models import db, User, Product, Order, OrderItem
from auth import create_token, auth_required, admin_required
from sqlalchemy import or_
from io import StringIO
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
db.init_app(app)

# ✅ Create all tables when app starts
with app.app_context():
    db.create_all()

# ===================== AUTH ===================== #

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name', '')

    if not email or not password:
        return jsonify({"message": "Missing fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_token(user)
    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    u = User.query.filter_by(email=data.get('email')).first()
    if not u or not u.check_password(data.get('password', '')):
        return jsonify({"message": "Invalid credentials"}), 401
    token = create_token(u)
    return jsonify({
        "token": token,
        "user": {
            "id": u.id,
            "email": u.email,
            "role": u.role
        }
    })


@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    u = User.query.filter_by(email=data.get('email')).first()
    if not u or not u.check_password(data.get('password', '')) or u.role != 'admin':
        return jsonify({"message": "Invalid admin credentials"}), 401
    token = create_token(u)
    return jsonify({
        "token": token,
        "user": {
            "id": u.id,
            "email": u.email,
            "role": u.role
        }
    })

# ===================== PRODUCTS ===================== #

@app.route('/api/products', methods=['GET'])
def list_products():
    q = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    per = int(request.args.get('per', 50))
    query = Product.query.filter(Product.deleted == False)

    if q:
        query = query.filter(or_(
            Product.name.ilike(f'%{q}%'),
            Product.slug.ilike(f'%{q}%'),
            Product.category.ilike(f'%{q}%')
        ))

    items = db.paginate(query.order_by(Product.created_at.desc()), page=page, per_page=per, error_out=False)
    products = [{
        "id": p.id,
        "name": p.name,
        "slug": p.slug,
        "category": p.category,
        "weight": p.weight,
        "price": p.price,
        "stock": p.stock,
        "images": p.images,
        "description": p.description
    } for p in items.items]

    return jsonify({"products": products, "total": items.total})


@app.route('/api/admin/products', methods=['POST'])
@admin_required
def create_product():
    data = request.json
    p = Product(
        name=data.get('name'),
        slug=data.get('slug'),
        category=data.get('category'),
        weight=data.get('weight', 0),
        price=data.get('price', 0),
        stock=data.get('stock', 0),
        images=data.get('images', ''),
        description=data.get('description', '')
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({"product_id": p.id}), 201


@app.route('/api/admin/products/<int:pid>', methods=['PUT'])
@admin_required
def update_product(pid):
    p = Product.query.get_or_404(pid)
    data = request.json
    for k in ['name', 'slug', 'category', 'weight', 'price', 'stock', 'images', 'description']:
        if k in data:
            setattr(p, k, data[k])
    db.session.commit()
    return jsonify({"ok": True})


@app.route('/api/admin/products/<int:pid>', methods=['DELETE'])
@admin_required
def delete_product(pid):
    p = Product.query.get_or_404(pid)
    p.deleted = True
    db.session.commit()
    return jsonify({"ok": True})


@app.route('/api/admin/products', methods=['GET'])
@admin_required
def admin_list_products():
    page = int(request.args.get('page', 1))
    per = int(request.args.get('per', 50))
    items = db.paginate(Product.query.order_by(Product.created_at.desc()), page=page, per_page=per, error_out=False)
    return jsonify({
        "products": [{"id": p.id, "name": p.name, "price": p.price, "stock": p.stock, "deleted": p.deleted} for p in items.items],
        "total": items.total
    })

# ===================== ORDERS ===================== #

@app.route('/api/orders', methods=['POST'])
@auth_required
def create_order():
    data = request.json
    items = data.get('items', [])
    shipping_address = data.get('shipping_address', '')

    if not items:
        return jsonify({"message": "No items"}), 400

    order = Order(user_id=request.current_user.id, shipping_address=shipping_address, total=0)
    db.session.add(order)

    total = 0
    for it in items:
        p = Product.query.get(it['product_id'])
        if not p or p.deleted:
            continue
        qty = int(it.get('qty', 1))
        oi = OrderItem(order=order, product=p, qty=qty, price=p.price)
        db.session.add(oi)
        total += p.price * qty
        p.stock = max(0, p.stock - qty)

    order.total = total
    db.session.commit()
    return jsonify({"order_id": order.id})


@app.route('/api/admin/orders', methods=['GET'])
@admin_required
def list_orders():
    q = request.args.get('q', '')
    status = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    per = int(request.args.get('per', 50))
    query = Order.query

    if status:
        query = query.filter_by(status=status)
    if q:
        query = query.join(User).filter(User.email.ilike(f'%{q}%'))

    items = db.paginate(query.order_by(Order.created_at.desc()), page=page, per_page=per, error_out=False)
    out = [{
        "id": o.id,
        "user_email": o.user.email if o.user else None,
        "total": o.total,
        "status": o.status,
        "created_at": o.created_at.isoformat()
    } for o in items.items]

    return jsonify({"orders": out, "total": items.total})


@app.route('/api/admin/orders/<int:oid>/status', methods=['PUT'])
@admin_required
def update_order_status(oid):
    data = request.json
    o = Order.query.get_or_404(oid)
    o.status = data.get('status', o.status)
    db.session.commit()
    return jsonify({"ok": True, "status": o.status})


@app.route('/api/admin/orders/export', methods=['POST'])
@admin_required
def export_orders():
    ids = request.json.get('ids', [])
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['order_id', 'user_email', 'total', 'status', 'created_at', 'shipping_address'])

    if ids:
        q = Order.query.filter(Order.id.in_(ids))
    else:
        q = Order.query

    for o in q:
        cw.writerow([
            o.id,
            o.user.email if o.user else '',
            o.total,
            o.status,
            o.created_at.isoformat(),
            o.shipping_address or ''
        ])

    output = si.getvalue()
    return jsonify({"csv": output})


# ===================== MAIN ===================== #
if __name__ == '__main__':
    app.run(debug=True, port=5000)
