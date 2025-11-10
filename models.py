from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from passlib.hash import bcrypt
import bcrypt as pybcrypt  # fallback for broken passlib backend

db = SQLAlchemy()

# ======================= USER MODEL =======================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(30), default='user')  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Secure password hashing
    def set_password(self, password):
        if not password:
            raise ValueError("Password cannot be empty")

        password = str(password)[:72]  # bcrypt limit

        try:
            # Try using Passlib first
            self.password_hash = bcrypt.hash(password)
        except Exception:
            # Fallback to direct bcrypt if Passlib backend fails
            hashed = pybcrypt.hashpw(password.encode("utf-8"), pybcrypt.gensalt())
            self.password_hash = hashed.decode("utf-8")

    # Password verification
    def check_password(self, password):
        password = str(password)[:72]
        try:
            return bcrypt.verify(password, self.password_hash)
        except Exception:
            return pybcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))


# ======================= PRODUCT MODEL =======================
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True)
    category = db.Column(db.String(120))
    weight = db.Column(db.Float, default=0.0)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    images = db.Column(db.Text)  # comma separated URLs
    description = db.Column(db.Text)
    deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ======================= ORDER MODEL =======================
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='Pending')  # Pending, Shipped, etc.
    shipping_address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='orders')


# ======================= ORDER ITEM MODEL =======================
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    qty = db.Column(db.Integer, default=1)
    price = db.Column(db.Float)

    # Relationships
    product = db.relationship("Product")
    order = db.relationship("Order", backref="items")
