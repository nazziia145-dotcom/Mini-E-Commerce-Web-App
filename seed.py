from app import app
from models import db, User, Product
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(name='Admin', email='admin@example.com', role='admin')
        admin.set_password('Admin@12345')
        db.session.add(admin)
    if not Product.query.first():
        p1 = Product(name='Sample T-Shirt', slug='sample-tshirt', category='Clothing', price=299.0, stock=50, description='Comfort tee', images='')
        p2 = Product(name='Sample Mug', slug='sample-mug', category='Home', price=149.0, stock=100, description='Ceramic mug', images='')
        db.session.add_all([p1,p2])
    db.session.commit()
    print("Seeded admin@example.com / Admin@12345 and sample products.")
