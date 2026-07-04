import sys
import os
os.chdir(r'C:\Users\roms0\OneDrive\Documents\construction_management_app\construction_management_app\backend\construction_management')
sys.path.insert(0, os.getcwd())

from app import create_app
from user_management.models import User
from extensions import db

app = create_app()

with app.app_context():
    try:
        admin = User.query.filter_by(username='admin').first()
        if admin:
            admin.set_password('admin123')
            db.session.commit()
            print(f"Admin password set to: admin123")
        else:
            print("Admin user not found")
        
    except Exception as e:
        import traceback
        print(f"Error: {str(e)}")
        traceback.print_exc()
