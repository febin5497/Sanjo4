import sys
import os
os.chdir(r'C:\Users\roms0\OneDrive\Documents\construction_management_app\construction_management_app\backend\construction_management')
sys.path.insert(0, os.getcwd())

from app import create_app
from extensions import db

app = create_app()

# Create a test client
client = app.test_client()

# Get a JWT token from the database
with app.app_context():
    from user_management.models import User
    from flask_jwt_extended import create_access_token
    
    admin = User.query.filter_by(username='admin').first()
    if admin:
        token = create_access_token(identity=admin.id)
        print(f"Token: {token[:50]}...")
        
        # Make the API call
        response = client.get(
            '/api/attendance?start_date=2026-02-16&end_date=2026-03-18',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.get_json()}")
    else:
        print("Admin user not found")
