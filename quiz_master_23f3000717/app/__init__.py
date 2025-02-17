from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)

    from app.controllers.auth_controller import auth_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.user_controller import user_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    
    with app.app_context():
        db.create_all()
        # ✅ Always ensure a default admin exists
        from app.models.user import User
        admin = User.query.filter_by(email='admin@admin.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@admin.com',
                role='admin'
            )
            admin.set_password('admin123')  # Set default admin password
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin created: admin@admin.com / admin123")
    
    return app
